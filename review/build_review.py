"""
Human review page for the detectors (independent of the assistant's by-eye verdicts in AUDIT 43 and 45).

Builds short looping clips with both skeletons for every sampled event and one local HTML page that shows them
one at a time, without the earlier verdicts, and exports the reviewer's answers as CSV:

  releases       the 48 contact releases of outputs/grammar/contact_check.csv + contact_check_v2.csv
                 (4 s around the release; the frame border turns white when the detector says "released")
  weight_share   the 42 weight-sharing episodes of outputs/roles/episodes.csv
                 (1.5 s before to 1.5 s after; white border while the detector says "weight shared")

Run from the repo root:  python review/build_review.py   then open outputs/review/index.html
Answers: "Exportar CSV" in the page -> save as outputs/review/answers_<name>.csv; compare with
python review/agreement.py. Clips are third-party footage: outputs/review/ stays out of git.
"""
from __future__ import annotations

import glob
import json
import subprocess
from pathlib import Path
import numpy as np
import pandas as pd
import cv2

from src.io.tracks import load_tracks
from src.pose.pose_detector import SKELETON_EDGES

OUT = Path("outputs/review"); (OUT / "clips").mkdir(parents=True, exist_ok=True)
COL = ((255, 160, 0), (0, 140, 255))            # BGR: A blue, B orange
H = 480


def clip(vid, t0, t1, on0, on1, name, tracks={}):
    out = OUT / "clips" / f"{name}.mp4"
    if out.exists():
        return
    tr = tracks.setdefault(vid, load_tracks(f"outputs/{vid}/{vid}_tracks.npz")); fps = float(tr.meta["fps"])
    vp = (sorted(glob.glob(f"videos/{vid}.*")) + sorted(glob.glob(f"videos/full/{vid}.*")))[0]
    cap = cv2.VideoCapture(vp); a = max(0, int(t0 * fps)); b = min(int(t1 * fps), len(tr.present) - 1)
    cap.set(cv2.CAP_PROP_POS_FRAMES, a); enc = None
    for i in range(a, b + 1):
        ok, f = cap.read()
        if not ok:
            break
        for j in (0, 1):
            if tr.present[i, j]:
                k = tr.kpts[i, j]
                for p, q in SKELETON_EDGES:
                    if k[p, 2] > 0.3 and k[q, 2] > 0.3:
                        cv2.line(f, tuple(k[p, :2].astype(int)), tuple(k[q, :2].astype(int)), COL[j], 3, cv2.LINE_AA)
        W = int(round(f.shape[1] * H / f.shape[0])); W += W % 2
        f = cv2.resize(f, (W, H))
        if on0 <= i / fps <= on1:
            cv2.rectangle(f, (0, 0), (W - 1, H - 1), (255, 255, 255), 8)
        if enc is None:
            enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}",
                                    "-r", f"{fps / 2:.3f}", "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "26", str(out)],
                                   stdin=subprocess.PIPE)                      # half speed: easier to judge
        enc.stdin.write(f.tobytes())
    cap.release()
    if enc:
        enc.stdin.close(); enc.wait()


def main():
    items = []
    rel = pd.concat([pd.read_csv("outputs/grammar/contact_check.csv").assign(round=1),
                     pd.read_csv("outputs/grammar/contact_check_v2.csv").assign(round=2)])
    rel = rel.drop_duplicates(subset=["video", "release_s"], keep="first")
    for r in rel.itertuples():
        name = f"rel_r{r.round}_{r.id:02d}"
        clip(r.video, r.release_s - 2, r.release_s + 2, r.release_s, r.release_s + 2, name)
        items.append(dict(set="releases", key=name, clip=f"clips/{name}.mp4"))
    for r in pd.read_csv("outputs/roles/episodes.csv").itertuples():
        name = f"ws_{r.id:02d}"
        clip(r.video, r.start_s - 1.5, r.end_s + 1.5, r.start_s, r.end_s, name)
        items.append(dict(set="weight_share", key=name, clip=f"clips/{name}.mp4"))
    rng = np.random.default_rng(7); order = rng.permutation(len(items)); items = [items[i] for i in order]
    items.sort(key=lambda x: x["set"])
    html = (Path(__file__).parent / "template.html").read_text().replace("__ITEMS__", json.dumps(items))
    (OUT / "index.html").write_text(html)
    print(f"[review] {len(items)} items -> {OUT / 'index.html'}")


if __name__ == "__main__":
    main()
