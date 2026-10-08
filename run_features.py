"""
Stage 2: raw tracks -> features (frame table + window table + info json).

Inputs (one of):
  --tracks outputs/<stem>/<stem>_tracks.npz          produced by run_tracking.py (preferred)
  --legacy-csv outputs/<stem>/<stem>_features.csv    a features CSV from the pre-audit pipeline
                                                      (positions only; keypoint-based features unavailable)
Optional:
  --px-per-meter 123.4   floor-plane calibration; otherwise units are body lengths (bl)

Outputs: <stem>_features.csv, <stem>_windows.csv, <stem>_feature_info.json
"""
from __future__ import annotations

import argparse
import json
import glob
from pathlib import Path
import numpy as np
import pandas as pd
import cv2

from src.io.tracks import load_tracks, Tracks
from src.features.scale import body_scale
from src.features.kinematics import build_frame_table, build_window_table
from src.features.contact import min_keypoint_distance, hand_to_hip_distance
from src.features.laban_movement_analysis import contraction_index, bounding_area
from src.pose.pose_detector import KEYPOINT_INDEX

I = KEYPOINT_INDEX


def _centers(k: np.ndarray, bbox: np.ndarray):
    pelvis = (k[:, I["left_hip"], :2] + k[:, I["right_hip"], :2]) / 2
    torso = (k[:, I["left_shoulder"], :2] + k[:, I["right_shoulder"], :2] + k[:, I["left_hip"], :2] + k[:, I["right_hip"], :2]) / 4
    body = np.column_stack([(bbox[:, 0] + bbox[:, 2]) / 2, (bbox[:, 1] + bbox[:, 3]) / 2])
    return pelvis, torso, body


def features_from_tracks(tr: Tracks, px_per_meter: float | None = None):
    fps, w, h = tr.meta["fps"], tr.meta["width"], tr.meta["height"]
    kA, kB = tr.kpts[:, 0].astype(float), tr.kpts[:, 1].astype(float)
    kA[~tr.present[:, 0]] = np.nan; kB[~tr.present[:, 1]] = np.nan
    pos = {}
    for lab, k, b in (("A", kA, tr.bbox[:, 0]), ("B", kB, tr.bbox[:, 1])):
        pos[f"pelvis_{lab}"], pos[f"torso_{lab}"], pos[f"body_{lab}"] = _centers(k, b.astype(float))
    if px_per_meter:
        sA = sB = float(px_per_meter); unit = "m"; methods = ("calibration", "calibration")
    else:
        (sA, mA), (sB, mB) = body_scale(kA, tr.bbox[:, 0]), body_scale(kB, tr.bbox[:, 1]); unit = "bl"; methods = (mA, mB)
    kA_f, kB_f = np.nan_to_num(kA, nan=0.0), np.nan_to_num(kB, nan=0.0)
    extra = {}
    for lab, k, s in (("A", kA, sA), ("B", kB, sB)):
        if np.isfinite(s):
            extra[f"lma_contraction_u_{lab}"] = contraction_index(np.nan_to_num(k, nan=0.0), s)
            extra[f"lma_bbox_area_u_{lab}"] = bounding_area(np.nan_to_num(k, nan=0.0), s)
        extra[f"track_id_{lab}"] = tr.track_id[:, 0 if lab == "A" else 1]
    df, info = build_frame_table(pos, tr.present, fps, w, h, sA, sB, unit,
                                 contact_min_dist=min_keypoint_distance(kA_f, kB_f), hand_torso=hand_to_hip_distance(kA_f, kB_f),
                                 camera_motion=tr.camera_motion.astype(float), extra=extra,
                                 camera_M=tr.camera_M.astype(float) if tr.camera_M is not None and np.isfinite(tr.camera_M).any() else None)
    info.update({"source": "tracks", "scale_method_A": methods[0], "scale_method_B": methods[1], "video": tr.meta.get("video"),
                 "tracker": tr.meta.get("tracker"), "model": tr.meta.get("model")})
    return df, info


def features_from_legacy_csv(path: str, fps: float, width: int, height: int, px_per_meter: float | None = None):
    old = pd.read_csv(path, low_memory=False)
    n = len(old)
    present = np.column_stack([old.present_A.to_numpy().astype(bool), old.present_B.to_numpy().astype(bool)])
    pos = {}
    for lab in "AB":
        for part in ("pelvis", "torso", "body"):
            arr = old[[f"{part}_{lab}_x", f"{part}_{lab}_y"]].to_numpy().astype(float)
            arr[~present[:, 0 if lab == "A" else 1]] = np.nan  # legacy CSVs had interpolated positions: undo
            pos[f"{part}_{lab}"] = arr
    scales = {}
    for lab in "AB":
        # torso centre = midpoint(shoulder-mid, hip-mid); pelvis = hip-mid  =>  trunk = 2 * |torso - pelvis|
        t = 2 * np.linalg.norm(pos[f"torso_{lab}"] - pos[f"pelvis_{lab}"], axis=1)
        t = t[np.isfinite(t) & (t > 2)]
        scales[lab] = float(np.median(t)) if len(t) >= 30 else float("nan")
    if px_per_meter:
        sA = sB = float(px_per_meter); unit = "m"
    else:
        sA, sB, unit = scales["A"], scales["B"], "bl"
    cmd = old["contact_proxy_min_dist"].to_numpy().astype(float) if "contact_proxy_min_dist" in old else None
    if cmd is not None:
        cmd[~(present[:, 0] & present[:, 1])] = np.nan
    ht = old["contact_proxy_hand_torso"].to_numpy().astype(float) if "contact_proxy_hand_torso" in old else None
    df, info = build_frame_table(pos, present, fps, width, height, sA, sB, unit, contact_min_dist=cmd, hand_torso=ht)
    info.update({"source": "legacy_csv", "scale_method_A": "2x_torso_pelvis_median", "scale_method_B": "2x_torso_pelvis_median"})
    return df, info


def video_meta(video_path: str | None, stem: str):
    cands = [video_path] if video_path else glob.glob(f"videos/{stem}.mp4") + glob.glob(f"videos/{stem}.mov")
    for c in cands:
        if c and Path(c).exists():
            cap = cv2.VideoCapture(c)
            if cap.isOpened():
                m = (cap.get(cv2.CAP_PROP_FPS) or 30.0, int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
                cap.release()
                return m
    return None


def run(tracks: str | None, legacy_csv: str | None, output_dir: str | None, video: str | None = None,
        px_per_meter: float | None = None, fps: float | None = None, width: int | None = None, height: int | None = None):
    src = Path(tracks or legacy_csv)
    stem = src.name.replace("_tracks.npz", "").replace("_features.csv", "").replace("ci_features.csv", src.parent.name)
    if stem == "" or stem == "ci":
        stem = src.parent.name
    out = Path(output_dir or src.parent); out.mkdir(parents=True, exist_ok=True)
    if tracks:
        df, info = features_from_tracks(load_tracks(tracks), px_per_meter)
    else:
        meta = video_meta(video, stem)
        if meta is None and not (fps and width and height):
            old = pd.read_csv(legacy_csv, nrows=2000, low_memory=False)
            fps_est = 1.0 / np.nanmedian(np.diff(old.time_sec)) if len(old) > 2 else 30.0
            meta = (fps_est, int(np.nanmax(old.filter(like="_x").max()) + 1), int(np.nanmax(old.filter(like="_y").max()) + 1))
            print(f"[features] WARNING: video not found, fps/size estimated from CSV: {meta}")
        fps_, w_, h_ = (fps or meta[0], width or meta[1], height or meta[2])
        df, info = features_from_legacy_csv(legacy_csv, fps_, w_, h_, px_per_meter)
        legacy_backup = out / f"{stem}_features_legacy.csv"
        if Path(legacy_csv).resolve() == (out / f"{stem}_features.csv").resolve() and not legacy_backup.exists():
            Path(legacy_csv).rename(legacy_backup)
    info["stem"] = stem
    win = build_window_table(df, info["fps"])
    df.to_csv(out / f"{stem}_features.csv", index=False)
    win.to_csv(out / f"{stem}_windows.csv", index=False)
    # attach tracking / camera-motion summaries if present
    for name in ("tracking_quality", "camera_motion"):
        p = out / f"{stem}_{name}.json"
        if p.exists():
            with open(p) as f:
                info[name] = json.load(f)
    with open(out / f"{stem}_feature_info.json", "w") as f:
        json.dump(info, f, indent=2, default=lambda o: None if (isinstance(o, float) and not np.isfinite(o)) else str(o))
    nf = info.get("torso_A_jerk_noise_floor_u") or float("nan"); mj = info.get("torso_A_median_jerk_u") or float("nan")
    print(f"[features] {stem}: unit={info['unit']} scale A/B = {info['scale_A_px']:.1f}/{info['scale_B_px']:.1f} px; "
          f"jitter A = {info.get('torso_A_jitter_sigma_px', float('nan')):.2f} px; median jerk A = {mj:.1f} {info['unit']}/s^3 vs noise floor {nf:.1f}; "
          f"windows with SPARC: {int(win['sparc_A'].notna().sum()) if 'sparc_A' in win else 0}/{len(win)}")
    return df, win, info


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Stage 2: tracks -> features")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--tracks"); g.add_argument("--legacy-csv")
    ap.add_argument("--output-dir", default=None)
    ap.add_argument("--video", default=None, help="video file (for fps/size when using --legacy-csv)")
    ap.add_argument("--px-per-meter", type=float, default=None)
    ap.add_argument("--fps", type=float); ap.add_argument("--width", type=int); ap.add_argument("--height", type=int)
    a = ap.parse_args()
    run(a.tracks, a.legacy_csv, a.output_dir, a.video, a.px_per_meter, a.fps, a.width, a.height)
