"""
Build the analysis dataset from every outputs/<stem>/ directory.

Writes outputs/dataset/
  videos.csv   one row per video: resolution, fps, units, scales, detection rates, jitter,
               noise floor, camera-motion verdict, tracking diagnostics, inclusion flag + reason
  frames.csv   concatenated per-frame features (only included videos)
  windows.csv  concatenated per-window smoothness features (only included videos)

Inclusion rules (documented in the thesis, applied identically everywhere):
  camera static, OR ego-motion compensated (>= 80% of frames, zoom p95 <= 1%)  |  both dancers detected in >= 40% of frames
  >= 600 frames (20 s)           |  body scale available for both dancers
  human content check in videos/curation.csv: content == ci_dance (screens cannot tell a
  videoconference of two talking heads from a duet; 10 such clips passed the automatic screen)
"""
from __future__ import annotations

import glob
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd

MIN_FRAMES = 600
MIN_BOTH_DETECTED = 0.40


def collect(outputs_dir: str = "outputs", curation_csv: str = "videos/curation.csv"):
    cur = pd.read_csv(curation_csv).set_index("video") if Path(curation_csv).exists() else pd.DataFrame(columns=["content", "setting", "source_group"])
    rows, frames, windows = [], [], []
    seen_hashes = {}
    for d in sorted(Path(outputs_dir).iterdir()):
        if not d.is_dir():
            continue
        stem = d.name
        info_p = d / f"{stem}_feature_info.json"
        if not info_p.exists():
            continue
        info = json.load(open(info_p))
        cam = info.get("camera_motion") or (json.load(open(d / f"{stem}_camera_motion.json")) if (d / f"{stem}_camera_motion.json").exists() else {})
        tq = info.get("tracking_quality") or {}
        row = {"video": stem, "source": info.get("source"), "width": info.get("width"), "height": info.get("height"), "fps": info.get("fps"),
               "n_frames": info.get("n_frames"), "unit": info.get("unit"), "scale_A_px": info.get("scale_A_px"), "scale_B_px": info.get("scale_B_px"),
               "detected_A": info.get("detected_fraction_A"), "detected_B": info.get("detected_fraction_B"), "both_detected": info.get("both_detected_fraction"),
               "jitter_A_px": info.get("torso_A_jitter_sigma_px"), "jitter_B_px": info.get("torso_B_jitter_sigma_px"),
               "noise_floor_A_u": info.get("torso_A_jerk_noise_floor_u"), "median_jerk_A_u": info.get("torso_A_median_jerk_u"),
               "camera_static": cam.get("camera_static"), "camera_moving_fraction": cam.get("moving_fraction"), "camera_p95_px": cam.get("p95_motion_px"),
               "camera_compensated": bool(info.get("camera_compensated", False)), "camera_compensated_fraction": info.get("camera_compensated_fraction"),
               "camera_zoom_p95_abs": info.get("camera_zoom_p95_abs"),
               "suspected_swaps": tq.get("suspected_identity_swaps"), "id_switches_A": tq.get("tracker_id_switches_A"), "id_switches_B": tq.get("tracker_id_switches_B"),
               "tracker": info.get("tracker")}
        reasons = []
        compensated_ok = (row["camera_compensated"] and (row["camera_compensated_fraction"] or 0) >= 0.8
                          and (row["camera_zoom_p95_abs"] if row["camera_zoom_p95_abs"] is not None else 1.0) <= 0.01)
        row["camera_ok"] = bool(row["camera_static"]) or compensated_ok
        if row["camera_static"] is False and not compensated_ok:
            reasons.append("moving_camera")
        if (row["n_frames"] or 0) < MIN_FRAMES:
            reasons.append("too_short")
        if (row["both_detected"] or 0) < MIN_BOTH_DETECTED:
            reasons.append("low_detection")
        if not (np.isfinite(row["scale_A_px"] or np.nan) and np.isfinite(row["scale_B_px"] or np.nan)):
            reasons.append("no_body_scale")
        # Duplicate detection: the pre-audit batch copied one features file into 12 directories.
        f = pd.read_csv(d / f"{stem}_features.csv", low_memory=False)
        sig = hashlib.md5(np.nan_to_num(f[["torso_A_x", "torso_A_y", "torso_B_x"]].to_numpy(dtype=np.float32)[:2000]).tobytes()).hexdigest()
        if sig in seen_hashes:
            reasons.append(f"duplicate_of:{seen_hashes[sig]}")
        else:
            seen_hashes[sig] = stem
        if stem in cur.index:
            row.update(content=cur.loc[stem, "content"], setting=cur.loc[stem, "setting"], source_group=cur.loc[stem, "source_group"])
            if row["content"] != "ci_dance":
                reasons.append(f"not_dance:{row['content']}")
        else:
            row.update(content=None, setting=None, source_group=stem)
            reasons.append("not_curated")
        # review flag (not an exclusion): a tracked "dancer" with median speed < 0.35 bl/s is often a
        # spectator or a shadow (2 of the 5 wrong pairs found by the 7 Oct pair audit had this)
        meds = [np.nanmedian(f[c]) for c in ("torso_A_speed_u", "torso_B_speed_u") if c in f and np.isfinite(f[c]).any()]
        row["pair_low_activity_flag"] = bool(meds and min(meds) < 0.35)
        row["included"] = len(reasons) == 0
        row["exclusion_reason"] = ";".join(reasons)
        rows.append(row)
        if row["included"]:
            f.insert(0, "video", stem); frames.append(f)
            wp = d / f"{stem}_windows.csv"
            if wp.exists():
                w = pd.read_csv(wp); w.insert(0, "video", stem); windows.append(w)
    out = Path(outputs_dir) / "dataset"; out.mkdir(exist_ok=True)
    videos = pd.DataFrame(rows)
    videos.to_csv(out / "videos.csv", index=False)
    if frames:
        pd.concat(frames, ignore_index=True).to_csv(out / "frames.csv", index=False)
    if windows:
        pd.concat(windows, ignore_index=True).to_csv(out / "windows.csv", index=False)
    inc = videos[videos.included]
    print(f"[dataset] {len(videos)} videos with features; {len(inc)} included "
          f"({int(inc.n_frames.sum()) if len(inc) else 0} frames); excluded: {videos[~videos.included].exclusion_reason.value_counts().to_dict()}")
    return videos


if __name__ == "__main__":
    collect()
