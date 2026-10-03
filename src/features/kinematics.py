"""
Kinematics and Feature Extraction for Contact Improvisation movement analysis.
Computes positions, velocities, inter-dancer distances, directional coordination,
and contact proxies from tracked dancer keypoints.
"""

from typing import Optional, Dict, Any, Tuple, List
import numpy as np
import pandas as pd
from scipy.signal import savgol_filter
from src.pose.pose_detector import KEYPOINT_INDEX


def interpolate_trajectories(df: pd.DataFrame, max_gap: int = 15) -> pd.DataFrame:
    """
    Interpolates missing (NaN) values in coordinate columns using linear interpolation.
    Gaps larger than max_gap remain NaN to prevent false interpolation over long absences.
    """
    df_clean = df.copy()
    coord_cols = [c for c in df.columns if any(k in c for k in ["_x", "_y", "dist", "speed"])]
    for col in coord_cols:
        df_clean[col] = df_clean[col].interpolate(method="linear", limit=max_gap, limit_direction="both")
    return df_clean


def filter_teleport_jumps(pos_x: np.ndarray, pos_y: np.ndarray, max_jump: float = 120.0) -> Tuple[np.ndarray, np.ndarray]:
    """Replaces single-frame teleport jumps (tracker glitches) with NaNs."""
    px = pos_x.copy()
    py = pos_y.copy()
    for i in range(1, len(px)):
        if not (np.isnan(px[i]) or np.isnan(px[i-1]) or np.isnan(py[i]) or np.isnan(py[i-1])):
            dist = np.sqrt((px[i] - px[i-1])**2 + (py[i] - py[i-1])**2)
            if dist > max_jump:
                px[i] = np.nan
                py[i] = np.nan
    return px, py


def compute_smoothed_kinematics(
    pos_x: np.ndarray,
    pos_y: np.ndarray,
    fps: float,
    window_length: int = 11,
    polyorder: int = 3,
    max_physical_speed: float = 2000.0
) -> Dict[str, np.ndarray]:
    """
    Computes smoothed velocity, acceleration, jerk, and kinetic energy proxy
    using Savitzky-Golay differentiation.
    """
    dt = 1.0 / fps
    n = len(pos_x)
    
    # Initialize arrays with NaNs
    res = {k: np.full(n, np.nan) for k in ["vx", "vy", "speed", "ax", "ay", "accel", "jx", "jy", "jerk", "kinetic_energy"]}

    clean_x, clean_y = filter_teleport_jumps(pos_x, pos_y, max_jump=120.0)

    # Interpolate short teleport gaps
    x_series = pd.Series(clean_x).interpolate(limit=5)
    y_series = pd.Series(clean_y).interpolate(limit=5)
    cx = x_series.to_numpy()
    cy = y_series.to_numpy()

    valid_mask = ~(np.isnan(cx) | np.isnan(cy))
    if np.sum(valid_mask) < 4:
        return res

    if np.all(valid_mask) and n >= window_length:
        wl = window_length if window_length % 2 == 1 else window_length + 1
        wl = min(wl, n if n % 2 == 1 else n - 1)
        if wl > polyorder:
            # 1st Derivative: Velocity
            res["vx"] = savgol_filter(cx, window_length=wl, polyorder=polyorder, deriv=1, delta=dt)
            res["vy"] = savgol_filter(cy, window_length=wl, polyorder=polyorder, deriv=1, delta=dt)
            # 2nd Derivative: Acceleration
            res["ax"] = savgol_filter(cx, window_length=wl, polyorder=polyorder, deriv=2, delta=dt)
            res["ay"] = savgol_filter(cy, window_length=wl, polyorder=polyorder, deriv=2, delta=dt)
            # 3rd Derivative: Jerk
            res["jx"] = savgol_filter(cx, window_length=wl, polyorder=polyorder, deriv=3, delta=dt)
            res["jy"] = savgol_filter(cy, window_length=wl, polyorder=polyorder, deriv=3, delta=dt)
        else:
            res["vx"] = np.gradient(cx, dt)
            res["vy"] = np.gradient(cy, dt)
    else:
        res["vx"] = (x_series.diff() / dt).to_numpy()
        res["vy"] = (y_series.diff() / dt).to_numpy()

    raw_speed = np.sqrt(res["vx"]**2 + res["vy"]**2)

    # Clip unphysical derivative spikes caused by detector flicker
    res["speed"] = np.clip(raw_speed, 0.0, max_physical_speed)
    clip_mask = raw_speed > max_physical_speed
    res["vx"][clip_mask] *= (max_physical_speed / (raw_speed[clip_mask] + 1e-6))
    res["vy"][clip_mask] *= (max_physical_speed / (raw_speed[clip_mask] + 1e-6))
    
    # Magnitudes
    res["accel"] = np.sqrt(res["ax"]**2 + res["ay"]**2)
    res["jerk"] = np.sqrt(res["jx"]**2 + res["jy"]**2)
    
    # Kinetic Energy Proxy (proportional to v^2)
    res["kinetic_energy"] = res["speed"]**2

    return res


def compute_directional_similarity(
    vx_A: np.ndarray,
    vy_A: np.ndarray,
    vx_B: np.ndarray,
    vy_B: np.ndarray,
    speed_threshold: float = 2.0
) -> np.ndarray:
    """
    Computes cosine similarity between velocity vectors of Dancer A and Dancer B:
    cos_sim = (v_A . v_B) / (||v_A|| * ||v_B||)
    Returns values in [-1, 1]. NaNs where either speed is below threshold.
    """
    dot = vx_A * vx_B + vy_A * vy_B
    norm_A = np.sqrt(vx_A**2 + vy_A**2)
    norm_B = np.sqrt(vx_B**2 + vy_B**2)
    denom = norm_A * norm_B

    cos_sim = np.full_like(dot, np.nan)
    valid = (denom > 1e-6) & (norm_A >= speed_threshold) & (norm_B >= speed_threshold)
    cos_sim[valid] = dot[valid] / denom[valid]
    return np.clip(cos_sim, -1.0, 1.0)


def compute_keypoint_distance(
    kpts_A: np.ndarray,
    kpts_B: np.ndarray,
    name_A: str,
    name_B: str
) -> float:
    """Computes Euclidean distance between keypoint of A and keypoint of B."""
    idx_A = KEYPOINT_INDEX[name_A]
    idx_B = KEYPOINT_INDEX[name_B]
    p_A = kpts_A[idx_A, :2]
    p_B = kpts_B[idx_B, :2]
    conf_A = kpts_A[idx_A, 2]
    conf_B = kpts_B[idx_B, 2]
    if conf_A < 0.25 or conf_B < 0.25:
        return np.nan
    return float(np.linalg.norm(p_A - p_B))


def compute_min_keypoint_distance(
    kpts_A: np.ndarray,
    kpts_B: np.ndarray,
    conf_thresh: float = 0.3
) -> float:
    """
    Computes minimum Euclidean distance between all pairs of confident keypoints
    between dancer A and dancer B (contact proxy).
    """
    mask_A = kpts_A[:, 2] >= conf_thresh
    mask_B = kpts_B[:, 2] >= conf_thresh
    if np.sum(mask_A) == 0 or np.sum(mask_B) == 0:
        return np.nan

    pts_A = kpts_A[mask_A, :2]
    pts_B = kpts_B[mask_B, :2]
    # Compute pairwise distance matrix
    dists = np.linalg.norm(pts_A[:, None, :] - pts_B[None, :, :], axis=2)
    return float(np.min(dists))


def extract_features_timeseries(
    records_A: List[Dict[str, Any]],
    records_B: List[Dict[str, Any]],
    fps: float,
    frame_width: int,
    frame_height: int
) -> pd.DataFrame:
    """
    Aggregates per-frame records for Dancer A and Dancer B into a consolidated
    feature DataFrame with all interpersonal metrics.
    """
    n_frames = max(len(records_A), len(records_B))
    rows = []

    for i in range(n_frames):
        rec_A = records_A[i] if i < len(records_A) else {}
        rec_B = records_B[i] if i < len(records_B) else {}

        t = i / fps

        # Pelvis positions
        pelvis_A = rec_A.get("pelvis_pos", np.array([np.nan, np.nan]))
        pelvis_B = rec_B.get("pelvis_pos", np.array([np.nan, np.nan]))

        # Torso positions
        torso_A = rec_A.get("torso_pos", np.array([np.nan, np.nan]))
        torso_B = rec_B.get("torso_pos", np.array([np.nan, np.nan]))

        # Body centers
        body_A = rec_A.get("body_pos", np.array([np.nan, np.nan]))
        body_B = rec_B.get("body_pos", np.array([np.nan, np.nan]))

        # Keypoints
        kpts_A = rec_A.get("keypoints", np.zeros((17, 3)))
        kpts_B = rec_B.get("keypoints", np.zeros((17, 3)))

        # Inter-dancer distances
        dist_pelvis = np.linalg.norm(pelvis_A - pelvis_B) if not (np.isnan(pelvis_A).any() or np.isnan(pelvis_B).any()) else np.nan
        dist_torso = np.linalg.norm(torso_A - torso_B) if not (np.isnan(torso_A).any() or np.isnan(torso_B).any()) else np.nan
        dist_body = np.linalg.norm(body_A - body_B) if not (np.isnan(body_A).any() or np.isnan(body_B).any()) else np.nan

        # Contact proxies
        min_kpt_dist = compute_min_keypoint_distance(kpts_A, kpts_B)

        # Specific landmark proximities
        wrist_torso_candidates = [
            compute_keypoint_distance(kpts_A, kpts_B, "left_wrist", "left_hip"),
            compute_keypoint_distance(kpts_A, kpts_B, "right_wrist", "right_hip"),
            compute_keypoint_distance(kpts_B, kpts_A, "left_wrist", "left_hip"),
            compute_keypoint_distance(kpts_B, kpts_A, "right_wrist", "right_hip"),
        ]
        valid_wt = [d for d in wrist_torso_candidates if not np.isnan(d)]
        d_wrists_torso = min(valid_wt) if valid_wt else np.nan

        rows.append({
            "frame": i,
            "time_sec": t,
            "present_A": rec_A.get("present", False),
            "present_B": rec_B.get("present", False),
            "pelvis_A_x": pelvis_A[0],
            "pelvis_A_y": pelvis_A[1],
            "pelvis_B_x": pelvis_B[0],
            "pelvis_B_y": pelvis_B[1],
            "torso_A_x": torso_A[0],
            "torso_A_y": torso_A[1],
            "torso_B_x": torso_B[0],
            "torso_B_y": torso_B[1],
            "body_A_x": body_A[0],
            "body_A_y": body_A[1],
            "body_B_x": body_B[0],
            "body_B_y": body_B[1],
            "dist_pelvis": dist_pelvis,
            "dist_torso": dist_torso,
            "dist_body": dist_body,
            "contact_proxy_min_dist": min_kpt_dist,
            "contact_proxy_hand_torso": d_wrists_torso,
        })

    df = pd.DataFrame(rows)

    # Interpolate short occlusions for smoother kinematics
    df = interpolate_trajectories(df, max_gap=15)

    # Compute smoothed kinematics (velocity, acceleration, jerk, energy)
    for part in ["torso", "pelvis"]:
        kin_A = compute_smoothed_kinematics(
            df[f"{part}_A_x"].to_numpy(), df[f"{part}_A_y"].to_numpy(), fps
        )
        kin_B = compute_smoothed_kinematics(
            df[f"{part}_B_x"].to_numpy(), df[f"{part}_B_y"].to_numpy(), fps
        )

        for metric in ["vx", "vy", "speed", "accel", "jerk", "kinetic_energy"]:
            df[f"{part}_A_{metric}"] = kin_A[metric]
            df[f"{part}_B_{metric}"] = kin_B[metric]

        # Directional cosine similarity
        df[f"dir_sim_{part}"] = compute_directional_similarity(
            kin_A["vx"], kin_A["vy"], kin_B["vx"], kin_B["vy"]
        )

    # Normalized distances (relative to frame diagonal for resolution invariance)
    diag = np.sqrt(frame_width**2 + frame_height**2)
    df["dist_pelvis_norm"] = df["dist_pelvis"] / diag
    df["dist_torso_norm"] = df["dist_torso"] / diag
    df["contact_proxy_min_dist_norm"] = df["contact_proxy_min_dist"] / diag

    return df
