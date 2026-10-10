"""
Hand check of the contact detector's releases (state grammar: contact dwell ~1.3 s). Is CI touch-release
cycling that fast, or do detection problems (a keypoint jumping, a dancer briefly lost, occlusion) chop one
long contact into several short ones?

For a stratified random sample of contact -> near/apart transitions (3 per duet, 30 total) the sheet shows
five frames around the release (-0.6, -0.2, +0.2, +0.6, +1.0 s) with both skeletons, the frame state and the
nearest-segment distance in body lengths. Each row is judged by eye and the verdict written to
outputs/grammar/contact_check.csv (column `verdict`: real / false_release / unclear, plus a note).

Round 1 (seed 0, 3 per duet) chose the separation rule SEP_BL in state_grammar.py; round 2 (seed 1, 2 per duet,
run after the rule) is the out-of-sample check, verdicts in outputs/grammar/contact_check_v2.csv.

Outputs: outputs/grammar/{contact_check_sample.csv, check_releases_*.jpg (gitignored)}
"""
from __future__ import annotations

import glob
from pathlib import Path
import numpy as np
import pandas as pd
import cv2

import state_grammar as SG
from rolling_contact import draw

OUT = SG.OUT
OFFSETS = (-0.6, -0.2, 0.2, 0.6, 1.0)
PER_CLIP = 3


def releases(vid):
    st, fps, dmin, both = SG.frame_states(vid, return_dist=True)
    out, prev, start = [], None, 0
    for i, x in enumerate(st):
        if x != prev:
            if prev == "contact" and x in ("near", "apart") and (i - start) >= 0.3 * fps:
                out.append(dict(video=vid, release_s=i / fps, contact_dur_s=(i - start) / fps, next=x))
            prev, start = x, i
    return out, st, fps, dmin


def tile(vid, cap, tr, fi, label, w=260):
    cap.set(1, fi); ok, f = cap.read()
    if not ok:
        return np.zeros((int(w * 0.6), w, 3), np.uint8)
    for j, col in ((0, (255, 160, 0)), (1, (0, 140, 255))):
        if tr.present[fi, j]:
            draw(f, tr.kpts[fi, j], col)
    f = cv2.resize(f, (w, int(w * f.shape[0] / f.shape[1])))
    cv2.rectangle(f, (0, 0), (w, 22), (0, 0, 0), -1)
    cv2.putText(f, label, (4, 16), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)
    return f


def main(seed: int = 0, per_clip: int = PER_CLIP, tag: str = ""):
    from src.io.tracks import load_tracks
    vids = pd.read_csv(OUT / "per_clip.csv").video.tolist()
    rng = np.random.default_rng(seed); rows = []
    for v in vids:
        rel, st, fps, dmin = releases(v)
        pick = rng.choice(len(rel), min(per_clip, len(rel)), replace=False) if rel else []
        tr = load_tracks(f"outputs/{v}/{v}_tracks.npz")
        vp = (sorted(glob.glob(f"videos/{v}.*")) + sorted(glob.glob(f"videos/full/{v}.*")))[0]
        cap = cv2.VideoCapture(vp)
        for k in sorted(pick):
            r = rel[k]; r["n_releases_clip"] = len(rel)
            strip = []
            for o in OFFSETS:
                fi = int(np.clip(round((r["release_s"] + o) * fps), 0, len(st) - 1))
                d = dmin[fi]
                strip.append(tile(v, cap, tr, fi, f"{o:+.1f}s {st[fi] or '-'} d={d:.2f}" if np.isfinite(d) else f"{o:+.1f}s {st[fi] or '-'}"))
            r["strip"] = np.hstack(strip); rows.append(r)
        cap.release()
    df = pd.DataFrame([{k: x for k, x in r.items() if k != "strip"} for r in rows])
    df.insert(0, "id", range(len(df))); df["verdict"] = ""; df["note"] = ""
    df.to_csv(OUT / f"contact_check_sample{tag}.csv", index=False)
    for p in range(0, len(rows), 6):
        S = [cv2.putText(r["strip"].copy(), f"#{p + i} {r['video'][:11]} t={r['release_s']:.1f}s dur={r['contact_dur_s']:.1f}s",
                         (4, r["strip"].shape[0] - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1) for i, r in enumerate(rows[p:p + 6])]
        W = max(x.shape[1] for x in S)
        cv2.imwrite(str(OUT / f"check_releases{tag}_{p // 6}.jpg"),
                    np.vstack([cv2.copyMakeBorder(x, 0, 6, 0, W - x.shape[1], cv2.BORDER_CONSTANT) for x in S]), [cv2.IMWRITE_JPEG_QUALITY, 80])
    print(df.to_string())


if __name__ == "__main__":
    import sys
    # second round (after SEP_BL was chosen on the first): python hand_check_contacts.py 1 2 _v2
    main(int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]) if len(sys.argv) > 3 else main()
