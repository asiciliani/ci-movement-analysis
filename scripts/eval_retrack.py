"""
Compare two-dancer assignment variants on saved detections (no YOLO re-run): replays TwoDancerTracker over
<stem>_detections.csv with the video frames (appearance cue) and reports, per clip, the fraction of frames with
both dancers assigned, and on the hand-checked frames of outputs/pose_models/testset.csv how many have both.
Writes outputs/<stem>/<stem>_tracks_<tag>.npz (does not touch the tracks in use).

Usage: python scripts/eval_retrack.py <tag> [--no-exempt] [stem ...]
"""
from __future__ import annotations

import glob, sys
from pathlib import Path
import numpy as np
import pandas as pd
import cv2

sys.path.insert(0, ".")
from src.pose.pose_detector import PoseDetection
from src.tracking.dancer_tracker import TwoDancerTracker
from src.io.tracks import Tracks, load_tracks, save_tracks

KP = [f"kp{k}_{c}" for k in range(17) for c in "xyc"]


def retrack(stem, tag, exempt=True):
    out = Path(f"outputs/{stem}"); d = pd.read_csv(out / f"{stem}_detections.csv")
    old = load_tracks(out / f"{stem}_tracks.npz"); fps = old.meta["fps"]; n = old.n_frames
    drop = set(old.meta.get("retrack", {}).get("excluded_track_ids", []))            # keep earlier bystander exclusions
    d = d[~d.track_id.isin(drop)]; by = {f: g for f, g in d.groupby("frame")}
    tr = TwoDancerTracker(max_match_distance=old.meta["width"] * 0.45, appearance_weight=0.5, continuity_exempt=exempt)
    kpts = np.full((n, 2, 17, 3), np.nan, np.float32); bbox = np.full((n, 2, 4), np.nan, np.float32)
    present = np.zeros((n, 2), bool); tid = np.full((n, 2), -1, np.int32); conf = np.zeros((n, 2), np.float32)
    vp = [x for dd in ("videos", "videos/full", "videos/external") for x in sorted(glob.glob(f"{dd}/{stem}.*"))][0]
    cap = cv2.VideoCapture(vp)
    for i in range(n):
        ok, frame = cap.read()
        if not ok:
            break
        g = by.get(i)
        dets = [] if g is None else [PoseDetection(r[KP].to_numpy(float).reshape(17, 3), r[["x1", "y1", "x2", "y2"]].to_numpy(float),
                                                   float(r.conf), None if r.track_id < 0 else int(r.track_id)) for _, r in g.iterrows()]
        for j, det in enumerate(tr.step(dets, dt=1.0 / fps, frame=frame)):
            if det is not None:
                kpts[i, j] = det.keypoints; bbox[i, j] = det.bbox; present[i, j] = True
                tid[i, j] = -1 if det.track_id is None else det.track_id; conf[i, j] = det.bbox_conf
    cap.release()
    meta = dict(old.meta); meta["assignment"] = dict(tag=tag, continuity_exempt=exempt)
    save_tracks(out / f"{stem}_tracks_{tag}.npz", Tracks(kpts, bbox, present, tid, conf, old.camera_motion, meta, camera_M=old.camera_M))
    q = tr.quality_report()
    return dict(stem=stem, old_both=float(old.present.all(1).mean()), new_both=float(present.all(1).mean()),
                rescues=q["continuity_rescues"], swaps=q["suspected_identity_swaps"], new_present=present, old_present=old.present)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]; tag = args[0]; exempt = "--no-exempt" not in sys.argv
    stems = args[1:] or pd.read_csv("outputs/grammar/per_clip.csv").video.tolist()
    ts = pd.read_csv("outputs/pose_models/testset.csv"); ts = ts[ts.gt_ok == 1]; rows = []
    for s in stems:
        r = retrack(s, tag, exempt); t = ts[ts.video == s]
        for kind in ("hard", "ordinary"):
            f = t[t.kind == kind].frame.to_numpy()
            r[f"{kind}_old"] = int(r["old_present"][f].all(1).sum()); r[f"{kind}_new"] = int(r["new_present"][f].all(1).sum()); r[f"{kind}_n"] = len(f)
        del r["new_present"], r["old_present"]; rows.append(r); print(r, flush=True)
    df = pd.DataFrame(rows); Path("outputs/pose_models").mkdir(exist_ok=True); df.to_csv(f"outputs/pose_models/retrack_{tag}.csv", index=False)
    print(df.round(3).to_string()); print(df[[c for c in df if c.endswith(("_old", "_new", "_n"))]].sum().to_dict())


if __name__ == "__main__":
    main()
