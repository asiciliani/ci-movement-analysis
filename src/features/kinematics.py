"""
Kinematics for Contact Improvisation duets.

Design rules (all of them came out of the Oct-2026 audit):
1. Nothing is differentiated across a tracking gap. Derivatives are computed on contiguous
   runs of *detected* frames only; gaps of at most `max_fill` frames are filled linearly and
   flagged; the half-window at every run edge is discarded.
2. Every quantity is reported in pixels (for plotting / backward compatibility) AND in
   calibrated units: metres if `px_per_meter` is known, otherwise "body lengths" (bl),
   i.e. the dancer's median trunk length. Columns in calibrated units end in `_u`.
3. The estimator noise floor is reported next to the data: keypoint jitter is estimated
   from the residual of the smoothing filter and propagated through the derivative filter.
4. Raw jerk magnitude is kept only as a diagnostic. Smoothness claims should use SPARC/LDLJ
   on windows (see smoothness.py) which are dimensionless.
"""
from __future__ import annotations

from typing import Dict, Any, Optional, Tuple, List
import numpy as np
import pandas as pd
from scipy.signal import savgol_filter, savgol_coeffs

SG_WINDOW = 11
SG_POLY = 3


# ----------------------------------------------------------------------------- gaps & runs
def fill_small_gaps(x: np.ndarray, max_fill: int) -> Tuple[np.ndarray, np.ndarray]:
    """Linearly fill NaN gaps of length <= max_fill that are bounded by valid samples.
    Returns (filled, filled_mask)."""
    x = np.asarray(x, dtype=float).copy()
    filled = np.zeros(len(x), bool)
    if max_fill <= 0:
        return x, filled
    nan = ~np.isfinite(x)
    i = 0
    n = len(x)
    while i < n:
        if nan[i]:
            j = i
            while j < n and nan[j]:
                j += 1
            L = j - i
            if 0 < i and j < n and L <= max_fill:
                x[i:j] = np.linspace(x[i - 1], x[j], L + 2)[1:-1]
                filled[i:j] = True
            i = j
        else:
            i += 1
    return x, filled


def valid_runs(mask: np.ndarray) -> List[Tuple[int, int]]:
    """[start, end) index pairs of contiguous True values."""
    runs, n, i = [], len(mask), 0
    while i < n:
        if mask[i]:
            j = i
            while j < n and mask[j]:
                j += 1
            runs.append((i, j))
            i = j
        else:
            i += 1
    return runs


def remove_teleports(x: np.ndarray, y: np.ndarray, max_jump_px: float) -> Tuple[np.ndarray, np.ndarray, int]:
    """NaN-out the destination of any single-frame jump larger than max_jump_px (tracker glitch / id swap)."""
    x, y = x.copy(), y.copy()
    d = np.hypot(np.diff(x), np.diff(y))
    bad = np.where(np.isfinite(d) & (d > max_jump_px))[0] + 1
    x[bad] = np.nan
    y[bad] = np.nan
    return x, y, int(len(bad))


# ----------------------------------------------------------------------------- camera compensation
def compensate_camera(pos: np.ndarray, camera_M: np.ndarray) -> Tuple[np.ndarray, Dict[str, float]]:
    """
    Remove camera ego-motion from a (N,2) px trajectory. camera_M[t] maps frame t-1 coordinates
    to frame t coordinates (similarity transform). The dancer's own displacement in frame-t
    coordinates is p_t - M_t(p_{t-1}); summing these gives a trajectory in a virtual static frame
    (absolute offset is arbitrary; derivatives are unaffected). Frames whose transform is missing
    or whose position is missing become gaps. Zoom is compensated per step but changes the px/bl
    scale over time; the per-step scale factor is returned for screening.
    """
    n = len(pos)
    q = np.full((n, 2), np.nan)
    valid_M = np.isfinite(camera_M).all(axis=(1, 2))
    scales = np.full(n, np.nan)
    acc = None
    for t in range(n):
        p_t = pos[t]
        if not np.isfinite(p_t).all():
            acc = None
            continue
        if t == 0 or acc is None or not np.isfinite(pos[t - 1]).all():
            acc = p_t.copy(); q[t] = acc; continue
        if not valid_M[t]:
            acc = None
            continue
        M = camera_M[t]
        moved_prev = M[:, :2] @ pos[t - 1] + M[:, 2]
        acc = acc + (p_t - moved_prev)
        q[t] = acc
        scales[t] = float(np.sqrt(abs(np.linalg.det(M[:, :2]))))
    info = {"compensated_fraction": float(np.isfinite(q).all(axis=1).sum() / max(1, np.isfinite(pos).all(axis=1).sum())),
            "zoom_p95_abs": float(np.nanpercentile(np.abs(scales - 1), 95)) if np.isfinite(scales).any() else float("nan")}
    return q, info


# ----------------------------------------------------------------------------- derivatives
def differentiate_runs(x: np.ndarray, y: np.ndarray, fps: float, window: int = SG_WINDOW, poly: int = SG_POLY,
                       max_fill: int = 2) -> Dict[str, np.ndarray]:
    """Savitzky-Golay derivatives on contiguous detected runs. Returns dict with
    x_s, y_s (smoothed), vx, vy, ax, ay, jx, jy, filled (bool), valid_deriv (bool), residual (px)."""
    n = len(x)
    dt = 1.0 / fps
    xf, fx = fill_small_gaps(x, max_fill)
    yf, fy = fill_small_gaps(y, max_fill)
    filled = fx | fy
    valid = np.isfinite(xf) & np.isfinite(yf)
    out = {k: np.full(n, np.nan) for k in ("x_s", "y_s", "vx", "vy", "ax", "ay", "jx", "jy", "residual")}
    half = window // 2
    for s, e in valid_runs(valid):
        if e - s < window:
            continue
        seg_x, seg_y = xf[s:e], yf[s:e]
        for name, d in (("x_s", 0), ("vx", 1), ("ax", 2), ("jx", 3)):
            out[name][s:e] = savgol_filter(seg_x, window, poly, deriv=d, delta=dt, mode="interp")
        for name, d in (("y_s", 0), ("vy", 1), ("ay", 2), ("jy", 3)):
            out[name][s:e] = savgol_filter(seg_y, window, poly, deriv=d, delta=dt, mode="interp")
        out["residual"][s:e] = np.hypot(seg_x - out["x_s"][s:e], seg_y - out["y_s"][s:e])
        # discard the poorly-conditioned edges of every run
        for name in ("vx", "vy", "ax", "ay", "jx", "jy"):
            out[name][s:s + half] = np.nan
            out[name][e - half:e] = np.nan
    out["filled"] = filled
    out["valid_deriv"] = np.isfinite(out["vx"]) & np.isfinite(out["jx"])
    return out


def estimate_jitter_sigma(residual: np.ndarray) -> float:
    """Per-axis keypoint jitter (px) from the smoothing residual: residual is the 2-D magnitude,
    so sigma_axis ~ median(|r|) / 1.1774 for a Rayleigh distribution."""
    r = residual[np.isfinite(residual)]
    if len(r) < 50:
        return float("nan")
    return float(np.median(r) / 1.1774)


def jerk_noise_floor(sigma_px: float, fps: float, window: int = SG_WINDOW, poly: int = SG_POLY) -> float:
    """Expected jerk *magnitude* produced by white keypoint jitter of std sigma_px per axis,
    through the same SG third-derivative filter. Mean of a Rayleigh with that sigma."""
    c = savgol_coeffs(window, poly, deriv=3, delta=1.0 / fps)
    s_axis = float(np.linalg.norm(c)) * sigma_px
    return float(s_axis * np.sqrt(np.pi / 2))


# ----------------------------------------------------------------------------- per-dancer kinematics
def dancer_kinematics(pos: np.ndarray, fps: float, scale_px: float, max_jump_bl: float = 1.0,
                      max_speed_u: float = 15.0, max_fill: int = 2) -> Dict[str, Any]:
    """pos: (N,2) px positions with NaN where not detected. scale_px: px per unit (bl or m)."""
    x, y = pos[:, 0].astype(float), pos[:, 1].astype(float)
    if np.isfinite(scale_px) and scale_px > 0:
        x, y, n_tele = remove_teleports(x, y, max_jump_bl * scale_px)
    else:
        n_tele = 0
    d = differentiate_runs(x, y, fps, max_fill=max_fill)
    speed = np.hypot(d["vx"], d["vy"])
    accel = np.hypot(d["ax"], d["ay"])
    jerk = np.hypot(d["jx"], d["jy"])
    # implausible speeds -> drop that frame's derivatives (never clip: clipping fabricates values)
    if np.isfinite(scale_px) and scale_px > 0:
        bad = speed > max_speed_u * scale_px
        for arr in (speed, accel, jerk, d["vx"], d["vy"]):
            arr[bad] = np.nan
    else:
        bad = np.zeros(len(x), bool)
    sigma = estimate_jitter_sigma(d["residual"])
    return {
        "vx": d["vx"], "vy": d["vy"], "speed": speed, "accel": accel, "jerk": jerk,
        "kinetic_energy": speed ** 2,  # mass-less proxy, px^2/s^2 ; use *_u version for comparisons
        "filled": d["filled"], "valid_deriv": d["valid_deriv"] & ~bad,
        "jitter_sigma_px": sigma, "n_teleports": n_tele, "n_implausible_speed": int(bad.sum()),
        "jerk_noise_floor_px": jerk_noise_floor(sigma, fps) if np.isfinite(sigma) else float("nan"),
    }


def compute_directional_similarity(vx_A, vy_A, vx_B, vy_B, speed_threshold: float = 0.0) -> np.ndarray:
    dot = vx_A * vx_B + vy_A * vy_B
    nA, nB = np.hypot(vx_A, vy_A), np.hypot(vx_B, vy_B)
    denom = nA * nB
    cos = np.full_like(dot, np.nan, dtype=float)
    ok = np.isfinite(denom) & (denom > 1e-9) & (nA >= speed_threshold) & (nB >= speed_threshold)
    cos[ok] = dot[ok] / denom[ok]
    return np.clip(cos, -1.0, 1.0)


# ----------------------------------------------------------------------------- frame table
def build_frame_table(positions: Dict[str, np.ndarray], present: np.ndarray, fps: float, width: int, height: int,
                      scale_A: float, scale_B: float, unit: str,
                      contact_min_dist: Optional[np.ndarray] = None, hand_torso: Optional[np.ndarray] = None,
                      camera_motion: Optional[np.ndarray] = None, extra: Optional[Dict[str, np.ndarray]] = None,
                      contact_thresh_u: float = 0.35, camera_M: Optional[np.ndarray] = None) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """positions: {'torso_A': (N,2), 'pelvis_A', 'body_A', 'torso_B', ...} in px, NaN when absent.
    If camera_M is given, kinematics are computed on camera-compensated trajectories (positions and
    inter-dancer distances stay in raw frame coordinates)."""
    n = len(present)
    pair_scale = np.nanmean([scale_A, scale_B])
    df = pd.DataFrame({"frame": np.arange(n), "time_sec": np.arange(n) / fps,
                       "present_A": present[:, 0].astype(bool), "present_B": present[:, 1].astype(bool)})
    for key, arr in positions.items():
        df[f"{key}_x"], df[f"{key}_y"] = arr[:, 0], arr[:, 1]
    for part in ("pelvis", "torso", "body"):
        d = np.linalg.norm(positions[f"{part}_A"] - positions[f"{part}_B"], axis=1)
        df[f"dist_{part}"] = d
        df[f"dist_{part}_u"] = d / pair_scale
    if contact_min_dist is not None:
        df["contact_proxy_min_dist"] = contact_min_dist
        df["contact_proxy_min_dist_u"] = contact_min_dist / pair_scale
        raw = pd.Series(df["contact_proxy_min_dist_u"] < contact_thresh_u, dtype=float)
        raw[~np.isfinite(df["contact_proxy_min_dist_u"])] = np.nan
        df["contact_state"] = raw.rolling(5, center=True, min_periods=3).median()
    if hand_torso is not None:
        df["contact_proxy_hand_torso"] = hand_torso
        df["contact_proxy_hand_torso_u"] = hand_torso / pair_scale
    if camera_motion is not None:
        df["camera_motion_px"] = camera_motion

    info: Dict[str, Any] = {"unit": unit, "scale_A_px": scale_A, "scale_B_px": scale_B, "fps": fps, "width": width, "height": height,
                            "n_frames": n, "detected_fraction_A": float(present[:, 0].mean()), "detected_fraction_B": float(present[:, 1].mean()),
                            "both_detected_fraction": float((present[:, 0] & present[:, 1]).mean())}
    kin_pos = dict(positions)
    if camera_M is not None:
        comp_info = []
        for key in ("torso_A", "torso_B", "pelvis_A", "pelvis_B"):
            kin_pos[key], ci = compensate_camera(positions[key], camera_M)
            comp_info.append(ci)
        info["camera_compensated"] = True
        info["camera_compensated_fraction"] = float(np.mean([c["compensated_fraction"] for c in comp_info]))
        info["camera_zoom_p95_abs"] = float(np.nanmax([c["zoom_p95_abs"] for c in comp_info]))
    else:
        info["camera_compensated"] = False
    for part in ("torso", "pelvis"):
        kin = {}
        for lab, sc in (("A", scale_A), ("B", scale_B)):
            k = dancer_kinematics(kin_pos[f"{part}_{lab}"], fps, sc)
            kin[lab] = k
            for m in ("vx", "vy", "speed", "accel", "jerk", "kinetic_energy"):
                df[f"{part}_{lab}_{m}"] = k[m]
            df[f"{part}_{lab}_speed_u"] = k["speed"] / sc
            df[f"{part}_{lab}_accel_u"] = k["accel"] / sc
            df[f"{part}_{lab}_jerk_u"] = k["jerk"] / sc
            df[f"{part}_{lab}_ke_u"] = (k["speed"] / sc) ** 2
            df[f"{part}_{lab}_valid_deriv"] = k["valid_deriv"]
            df[f"filled_{lab}"] = k["filled"] if part == "torso" else df.get(f"filled_{lab}", k["filled"])
            info[f"{part}_{lab}_jitter_sigma_px"] = k["jitter_sigma_px"]
            info[f"{part}_{lab}_jerk_noise_floor_px"] = k["jerk_noise_floor_px"]
            info[f"{part}_{lab}_jerk_noise_floor_u"] = k["jerk_noise_floor_px"] / sc if np.isfinite(sc) else float("nan")
            info[f"{part}_{lab}_median_jerk_u"] = float(np.nanmedian(df[f"{part}_{lab}_jerk_u"])) if np.isfinite(df[f"{part}_{lab}_jerk_u"]).any() else float("nan")
            info[f"{part}_{lab}_teleports_removed"] = k["n_teleports"]
            info[f"{part}_{lab}_implausible_speed_frames"] = k["n_implausible_speed"]
        df[f"dir_sim_{part}"] = compute_directional_similarity(kin["A"]["vx"], kin["A"]["vy"], kin["B"]["vx"], kin["B"]["vy"])
    diag = float(np.hypot(width, height))
    df["dist_pelvis_norm"] = df["dist_pelvis"] / diag
    df["dist_torso_norm"] = df["dist_torso"] / diag
    if "contact_proxy_min_dist" in df:
        df["contact_proxy_min_dist_norm"] = df["contact_proxy_min_dist"] / diag
    if extra:
        for k, v in extra.items():
            df[k] = v
    df["unit_scale_A_px"] = scale_A
    df["unit_scale_B_px"] = scale_B
    return df, info


# ----------------------------------------------------------------------------- windowed table
def build_window_table(df: pd.DataFrame, fps: float, window_s: float = 4.0, step_s: float = 1.0, part: str = "torso") -> pd.DataFrame:
    """Dimensionless smoothness per window, computed only on windows with complete, uninterrupted derivatives."""
    from src.features.smoothness import sparc, ldlj, ke_transfer_r
    W = int(round(window_s * fps)); S = max(1, int(round(step_s * fps)))
    rows = []
    n = len(df)
    for s in range(0, n - W + 1, S):
        e = s + W
        seg = df.iloc[s:e]
        row = {"t_start": seg.time_sec.iloc[0], "t_center": float(seg.time_sec.iloc[0] + window_s / 2), "t_end": seg.time_sec.iloc[-1],
               "n_frames": W}
        complete = {}
        for lab in "AB":
            ok = seg[f"{part}_{lab}_valid_deriv"].to_numpy().astype(bool)
            frac = float(ok.mean()); complete[lab] = frac == 1.0
            row[f"valid_fraction_{lab}"] = frac
            sp = seg[f"{part}_{lab}_speed_u"].to_numpy()
            row[f"mean_speed_u_{lab}"] = float(np.nanmean(sp)) if np.isfinite(sp).any() else np.nan
            row[f"median_jerk_u_{lab}"] = float(np.nanmedian(seg[f"{part}_{lab}_jerk_u"])) if np.isfinite(seg[f"{part}_{lab}_jerk_u"]).any() else np.nan
            if complete[lab]:
                vel = seg[[f"{part}_{lab}_vx", f"{part}_{lab}_vy"]].to_numpy() / seg[f"unit_scale_{lab}_px"].iloc[0]
                row[f"sparc_{lab}"] = sparc(sp, fps)
                row[f"ldlj_{lab}"] = ldlj(vel, fps)
            else:
                row[f"sparc_{lab}"] = np.nan; row[f"ldlj_{lab}"] = np.nan
        both = seg.present_A.to_numpy() & seg.present_B.to_numpy()
        row["both_detected_fraction"] = float(both.mean())
        row["mean_dist_torso_u"] = float(np.nanmean(seg["dist_torso_u"])) if np.isfinite(seg["dist_torso_u"]).any() else np.nan
        if "contact_state" in seg:
            cs = seg["contact_state"].to_numpy()
            row["contact_fraction"] = float(np.nanmean(cs)) if np.isfinite(cs).any() else np.nan
        row["mean_dir_sim"] = float(np.nanmean(seg[f"dir_sim_{part}"])) if np.isfinite(seg[f"dir_sim_{part}"]).any() else np.nan
        if complete["A"] and complete["B"]:
            row["ke_transfer_r"] = ke_transfer_r(seg[f"{part}_A_speed_u"].to_numpy(), seg[f"{part}_B_speed_u"].to_numpy(), fps)
        else:
            row["ke_transfer_r"] = np.nan
        if "camera_motion_px" in seg:
            row["camera_motion_p95_px"] = float(np.nanpercentile(seg["camera_motion_px"], 95)) if np.isfinite(seg["camera_motion_px"]).any() else np.nan
        rows.append(row)
    return pd.DataFrame(rows)
