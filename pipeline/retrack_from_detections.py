"""
Re-run the two-dancer assignment from saved detections, without re-running YOLO / BoT-SORT.

For clips where the pair audit found that the tracker followed the wrong people (spectators, a
bystander on the floor), the detections of those people are removed before assignment:
  --exclude-ids 7,19          BoT-SORT track ids to drop (read them off the --id-sheet)
  --auto-static 0.12          also drop tracklets >= 3 s long whose median camera-compensated
                              centroid speed is below this many bbox heights per second
  --id-sheet                  only write <stem>_ids_sheet.jpg (all detections with their ids) and exit
The video is decoded again for the appearance cue and the original camera transforms are reused.
Writes <stem>_tracks.npz (previous one kept as <stem>_tracks_pre_retrack.npz) and
<stem>_retrack.json; then run run_features.py and audit_identity.py again.
"""
from __future__ import annotations

import argparse, json, shutil
from pathlib import Path
import numpy as np
import pandas as pd
import cv2

from src.pose.pose_detector import PoseDetection
from src.tracking.dancer_tracker import TwoDancerTracker
from src.io.tracks import Tracks, load_tracks, save_tracks

KP = [f"kp{k}_{c}" for k in range(17) for c in "xyc"]


def tracklet_activity(d: pd.DataFrame, camera_M: np.ndarray, fps: float) -> pd.DataFrame:
    d = d.copy()
    d["cx"] = d[["kp5_x", "kp6_x", "kp11_x", "kp12_x"]].mean(1); d["cy"] = d[["kp5_y", "kp6_y", "kp11_y", "kp12_y"]].mean(1)
    rows = []
    for tid, g in d[d.track_id >= 0].groupby("track_id"):
        g = g.sort_values("frame"); f = g.frame.to_numpy()
        p = g[["cx", "cy"]].rolling(5, center=True, min_periods=1).median().to_numpy(); h = float((g.y2 - g.y1).median())
        disp = []
        for k in range(1, len(f)):
            if f[k] - f[k - 1] != 1:
                continue
            M = camera_M[f[k]] if camera_M is not None else None
            q = M[:, :2] @ p[k - 1] + M[:, 2] if M is not None and np.isfinite(M).all() else p[k - 1]
            disp.append(np.linalg.norm(p[k] - q))
        rows.append({"track_id": int(tid), "n_frames": len(g), "seconds": len(g) / fps, "bbox_h": h,
                     "activity": float(np.nanmedian(disp) * fps / h) if disp else np.nan})
    return pd.DataFrame(rows)


def id_sheet(video: str, d: pd.DataFrame, out: Path, n: int = 12):
    cap = cv2.VideoCapture(video); N = int(cap.get(7)); tiles = []
    for fi in np.linspace(0, N - 1, n).astype(int):
        cap.set(1, fi); ok, fr = cap.read()
        if not ok:
            continue
        for _, r in d[d.frame == fi].iterrows():
            cv2.rectangle(fr, (int(r.x1), int(r.y1)), (int(r.x2), int(r.y2)), (0, 255, 255), 2)
            cv2.putText(fr, str(int(r.track_id)), (int(r.x1), int(r.y1) + 30), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
        cv2.putText(fr, f"frame {fi}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)
        tiles.append(cv2.resize(fr, (640, int(640 * fr.shape[0] / fr.shape[1]))))
    rows = [np.hstack(tiles[i:i + 3]) for i in range(0, len(tiles) - len(tiles) % 3, 3)]
    cv2.imwrite(str(out), np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 80])


def main(stem, video, exclude_ids=(), auto_static=None, sheet_only=False, appearance_weight=0.5):
    out = Path(f"outputs/{stem}"); d = pd.read_csv(out / f"{stem}_detections.csv")
    if sheet_only:
        id_sheet(video, d, out / f"{stem}_ids_sheet.jpg"); print(f"wrote {out / f'{stem}_ids_sheet.jpg'}"); return
    old = load_tracks(out / f"{stem}_tracks.npz"); fps = old.meta["fps"]; n = old.n_frames
    drop = set(int(i) for i in exclude_ids)
    act = tracklet_activity(d, old.camera_M, fps)
    if auto_static is not None:
        drop |= set(act[(act.seconds >= 3) & (act.activity < auto_static)].track_id.astype(int))
    d = d[~d.track_id.isin(drop)]
    by_frame = {f: g for f, g in d.groupby("frame")}
    W = old.meta["width"]; tracker = TwoDancerTracker(max_match_distance=W * 0.45, appearance_weight=appearance_weight)
    kpts = np.full((n, 2, 17, 3), np.nan, np.float32); bbox = np.full((n, 2, 4), np.nan, np.float32)
    present = np.zeros((n, 2), bool); tid = np.full((n, 2), -1, np.int32); conf = np.zeros((n, 2), np.float32)
    cap = cv2.VideoCapture(video)
    for i in range(n):
        ok, frame = cap.read()
        if not ok:
            break
        g = by_frame.get(i)
        dets = [] if g is None else [PoseDetection(r[KP].to_numpy(float).reshape(17, 3), r[["x1", "y1", "x2", "y2"]].to_numpy(float),
                                                   float(r.conf), None if r.track_id < 0 else int(r.track_id)) for _, r in g.iterrows()]
        for j, det in enumerate(tracker.step(dets, dt=1.0 / fps, frame=frame)):
            if det is not None:
                kpts[i, j] = det.keypoints; bbox[i, j] = det.bbox; present[i, j] = True
                tid[i, j] = -1 if det.track_id is None else det.track_id; conf[i, j] = det.bbox_conf
    cap.release()
    shutil.copy(out / f"{stem}_tracks.npz", out / f"{stem}_tracks_pre_retrack.npz")
    meta = dict(old.meta); meta["retrack"] = {"excluded_track_ids": sorted(drop), "auto_static": auto_static}
    save_tracks(out / f"{stem}_tracks.npz", Tracks(kpts, bbox, present, tid, conf, old.camera_motion, meta, camera_M=old.camera_M))
    rep = {"excluded_track_ids": sorted(drop), "auto_static": auto_static, **tracker.quality_report()}
    json.dump(rep, open(out / f"{stem}_retrack.json", "w"), indent=2, default=float)
    print(json.dumps({k: rep[k] for k in rep if k in ("excluded_track_ids", "detected_fraction_A", "detected_fraction_B", "suspected_identity_swaps")}, default=float))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--stem", required=True); ap.add_argument("--video", required=True)
    ap.add_argument("--exclude-ids", default=""); ap.add_argument("--auto-static", type=float, default=None)
    ap.add_argument("--id-sheet", action="store_true"); ap.add_argument("--appearance-weight", type=float, default=0.5)
    a = ap.parse_args()
    main(a.stem, a.video, [x for x in a.exclude_ids.split(",") if x], a.auto_static, a.id_sheet, a.appearance_weight)
