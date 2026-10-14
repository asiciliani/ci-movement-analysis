"""
Candidate bystanders for the pair audit: every BoT-SORT tracklet >= 3 s whose camera-compensated centroid barely
moves (activity < 0.15 bbox heights/s, as in retrack_from_detections.tracklet_activity) is shown as one crop at
its median frame, with its id, so a person can mark spectators by eye. The ids then go to
`pipeline/retrack_from_detections.py --exclude-ids` (dancers lying still also appear here: do not exclude them).

Usage: python scripts/static_tracklet_sheet.py <stem>   -> outputs/<stem>/<stem>_static_tracklets.jpg (+ .csv)
"""
import glob, sys
from pathlib import Path
import numpy as np, pandas as pd, cv2
sys.path.insert(0, "pipeline")
from retrack_from_detections import tracklet_activity
from src.io.tracks import load_tracks


def main(stem, max_act=0.15, min_s=3.0, n_max=40):
    out = Path(f"outputs/{stem}"); d = pd.read_csv(out / f"{stem}_detections.csv"); tr = load_tracks(out / f"{stem}_tracks.npz")
    act = tracklet_activity(d, tr.camera_M, tr.meta["fps"])
    cand = act[(act.seconds >= min_s) & (act.activity < max_act)].sort_values("seconds", ascending=False).head(n_max)
    # how often each candidate was used as dancer A/B
    used = pd.Series(tr.track_id[tr.present]).value_counts()
    cand["frames_as_dancer"] = cand.track_id.map(used).fillna(0).astype(int)
    vp = [x for dd in ("videos", "videos/full", "videos/external") for x in sorted(glob.glob(f"{dd}/{stem}.*"))][0]
    cap = cv2.VideoCapture(vp); tiles = []
    for r in cand.itertuples():
        g = d[d.track_id == r.track_id].sort_values("frame"); row = g.iloc[len(g) // 2]
        cap.set(1, int(row.frame)); ok, f = cap.read()
        if not ok:
            continue
        x1, y1, x2, y2 = map(int, (row.x1, row.y1, row.x2, row.y2)); h = y2 - y1
        cv2.rectangle(f, (x1, y1), (x2, y2), (0, 255, 255), 3)
        X1, Y1, X2, Y2 = max(0, x1 - 2 * h), max(0, y1 - h), min(f.shape[1], x2 + 2 * h), min(f.shape[0], y2 + h)
        t = cv2.resize(f[Y1:Y2, X1:X2], (300, 200))
        cv2.rectangle(t, (0, 0), (300, 20), (0, 0, 0), -1)
        cv2.putText(t, f"id {r.track_id}  {r.seconds:.0f}s  dancer {r.frames_as_dancer}f", (3, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)
        tiles.append(t)
    cap.release()
    if not tiles:
        print(stem, "no static tracklets"); return
    tiles += [np.zeros_like(tiles[0])] * ((-len(tiles)) % 5)
    cv2.imwrite(str(out / f"{stem}_static_tracklets.jpg"), np.vstack([np.hstack(tiles[i:i + 5]) for i in range(0, len(tiles), 5)]), [cv2.IMWRITE_JPEG_QUALITY, 80])
    cand.to_csv(out / f"{stem}_static_tracklets.csv", index=False)
    print(stem, len(cand), "candidates;", int((cand.frames_as_dancer > 0).sum()), "used as a dancer")


if __name__ == "__main__":
    for s in sys.argv[1:]:
        main(s)
