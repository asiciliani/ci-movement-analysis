"""
Identity audit for saved tracks: (1) appearance-consistency check — does the dancer labelled A
look like A's clothing model, frame by frame — and (2) contact sheets of sampled frames with the
A/B labels drawn, for manual verification. Writes <stem>_identity_audit.json, <stem>_identity_sheet_*.jpg
and a review template <stem>_identity_review.csv (frame, A_ok, B_ok, note).
"""
from __future__ import annotations
import argparse, json, csv
from pathlib import Path
import numpy as np, cv2
from src.io.tracks import load_tracks
from src.tracking.appearance import torso_histogram, AppearanceModel, hist_distance, separability
from src.pose.pose_detector import SKELETON_EDGES

COL = {0: (255, 160, 0), 1: (0, 140, 255)}  # A = teal-ish, B = orange (BGR)


def draw(frame, kpts, label, color):
    for a, b in SKELETON_EDGES:
        if kpts[a, 2] > 0.3 and kpts[b, 2] > 0.3:
            cv2.line(frame, tuple(kpts[a, :2].astype(int)), tuple(kpts[b, :2].astype(int)), color, 2)
    c = kpts[[5, 6, 11, 12], :2].mean(axis=0).astype(int)
    cv2.putText(frame, label, (int(c[0]) - 10, int(c[1])), cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 3)


def main(tracks_path, video_path, n_sheet=24, tiles_per_sheet=12):
    tr = load_tracks(tracks_path); stem = Path(tracks_path).name.replace("_tracks.npz", ""); out = Path(tracks_path).parent
    cap = cv2.VideoCapture(video_path); n = tr.n_frames
    models = [AppearanceModel(alpha=0.05), AppearanceModel(alpha=0.05)]
    hists = [[None] * n, [None] * n]
    sample_idx = set(np.linspace(0, n - 1, n_sheet).astype(int).tolist())
    tiles = []
    for i in range(n):
        ok, f = cap.read()
        if not ok: break
        for j in range(2):
            if tr.present[i, j]:
                hists[j][i] = torso_histogram(f, tr.kpts[i, j])
        if tr.present[i].all():
            apart = np.linalg.norm(tr.kpts[i, 0, [5, 6, 11, 12], :2].mean(0) - tr.kpts[i, 1, [5, 6, 11, 12], :2].mean(0)) > 0.6 * max(tr.bbox[i, 0, 3] - tr.bbox[i, 0, 1], tr.bbox[i, 1, 3] - tr.bbox[i, 1, 1])
            if apart:
                models[0].update(hists[0][i]); models[1].update(hists[1][i])
        if i in sample_idx:
            g = f.copy()
            for j in range(2):
                if tr.present[i, j]: draw(g, tr.kpts[i, j], "AB"[j], COL[j])
            cv2.putText(g, f"frame {i}  t={i / tr.meta['fps']:.1f}s", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
            tiles.append(cv2.resize(g, (480, int(480 * g.shape[0] / g.shape[1]))))
    cap.release()
    # consistency: after models are learnt, re-score every frame against the FINAL models
    sep = separability(models[0], models[1])
    flags, scored = [], 0
    for i in range(n):
        if hists[0][i] is None and hists[1][i] is None: continue
        d = {}
        for j in range(2):
            h = hists[j][i]
            if h is not None:
                d[j] = (models[j].distance(h), models[1 - j].distance(h))
        if d:
            scored += 1
            if all(np.isfinite(v).all() and v[1] + 0.05 < v[0] for v in d.values()) and len(d) == 2:
                flags.append(i)
    # contiguous flagged segments
    segs = []
    for i in flags:
        if segs and i - segs[-1][1] <= 2: segs[-1][1] = i
        else: segs.append([i, i])
    rep = {"video": tr.meta.get("video"), "n_frames": n, "frames_scored": scored, "appearance_separability": sep,
           "frames_where_both_look_swapped": len(flags), "swap_like_fraction": len(flags) / max(1, scored),
           "swap_like_segments": [{"start": a, "end": b, "sec": round(a / tr.meta["fps"], 1)} for a, b in segs if b - a >= 3],
           "note": "separability < 0.2 means the two dancers' clothes are too similar for this check"}
    with open(out / f"{stem}_identity_audit.json", "w") as fh: json.dump(rep, fh, indent=2)
    # contact sheets
    for k in range(0, len(tiles), tiles_per_sheet):
        chunk = tiles[k:k + tiles_per_sheet]
        h = max(t.shape[0] for t in chunk); chunk = [cv2.copyMakeBorder(t, 0, h - t.shape[0], 0, 0, cv2.BORDER_CONSTANT) for t in chunk]
        rows = [np.hstack(chunk[r:r + 4]) if len(chunk[r:r + 4]) == 4 else np.hstack(chunk[r:r + 4] + [np.zeros_like(chunk[0])] * (4 - len(chunk[r:r + 4]))) for r in range(0, len(chunk), 4)]
        cv2.imwrite(str(out / f"{stem}_identity_sheet_{k // tiles_per_sheet + 1}.jpg"), np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 80])
    with open(out / f"{stem}_identity_review.csv", "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["frame", "A_ok", "B_ok", "note"])
        for i in sorted(sample_idx): w.writerow([i, "", "", ""])
    print(json.dumps(rep, indent=2))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--tracks", required=True); ap.add_argument("--video", required=True)
    ap.add_argument("--n-sheet", type=int, default=24); a = ap.parse_args()
    main(a.tracks, a.video, a.n_sheet)
