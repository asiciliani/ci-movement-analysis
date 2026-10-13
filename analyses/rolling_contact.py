"""
Rolling vs gripping: does the point of contact travel over the dancers' bodies (CI's "rolling point of
contact") or stay put (a grip / hold)?

For every contact bout (>= 1 s of continuous contact, depth-gated, see describe.py) and for each dancer:
  contact point the weighted centroid of all touching segment pairs (stable; the single closest pair
                flips between neighbouring segments frame to frame and made every bout look like a roll)
  net_travel    distance between the median body-frame location in the first and last 0.5 s (bl)
  spread        radius of the body-frame locations (median distance to their median, bl)
  regions       distinct body regions visited for >= 0.3 s (mode-filtered labels)
  hand_share    fraction of the bout in which the dominant contact region of either dancer is a hand
Locations are on a canonical body chart (T-pose, body lengths): the contact point is mapped to its segment
and position along it, so a hand grip keeps its coordinate however the arm moves. A bout is ROLL when the
contact travels >= ROLL_TRAVEL_BL over at least one body surface, HOLD when it travels and spreads
< GRIP_TRAVEL_BL on both bodies (a grip, a lean, a held carry), otherwise MIXED.
Thresholds are first guesses to be checked on the sheets (check_roll_*.jpg / check_grip_*.jpg) and,
later, against salsa (CoMPAS3D), where contact is mostly hand holds.

Outputs: outputs/rolling/{bouts.csv, per_clip.csv, report.md, check_*.jpg}
"""
from __future__ import annotations

import glob
from pathlib import Path
import numpy as np
import pandas as pd
import cv2
from scipy.ndimage import median_filter

from src.io.tracks import load_tracks
from src.analysis import describe as D
from src.pose.pose_detector import SKELETON_EDGES

OUT = Path("outputs/rolling"); OUT.mkdir(parents=True, exist_ok=True)
CONTACT_BL, MIN_BOUT_S = 0.25, 1.0
ROLL_TRAVEL_BL, ROLL_REGIONS, GRIP_TRAVEL_BL = 0.6, 3, 0.25


def bouts_for_clip(vid: str):
    tr = load_tracks(f"outputs/{vid}/{vid}_tracks.npz"); fps = float(tr.meta["fps"])
    kA, kB = tr.kpts[:, 0].astype(float), tr.kpts[:, 1].astype(float); both = tr.present.all(1)
    sA, sB = np.nanmedian(D.trunk_len(kA)), np.nanmedian(D.trunk_len(kB)); s = (sA + sB) / 2
    _, _, dpx, r1, r2 = D.contact_points(kA, kB)
    limb = np.array([(a in ("hand", "arm")) or (b in ("hand", "arm")) for a, b in zip(r1, r2)])   # see describe_duets: no depth gate for hand holds
    contact = median_filter((np.nan_to_num(dpx / s, nan=9) < CONTACT_BL) & (D.same_depth(kA, kB, sA, sB) | limb), size=5).astype(bool) & both
    pA, pB, rA, rB = D.contact_centroids(kA, kB, CONTACT_BL * s)
    # contact location on the canonical body chart (surface coordinate): a grip stays put even when the arm
    # moves; only travel over the body surface counts (the trunk-frame version called salsa hand holds "rolls")
    locA, locB = D.contact_surface(kA, kB, CONTACT_BL * s)
    rows = []
    for a, b in D.episodes(contact, fps, min_s=MIN_BOUT_S, merge_gap_s=0.3):
        rec = dict(video=vid, start_s=a / fps, end_s=b / fps, dur_s=(b - a) / fps, mid_frame=(a + b) // 2)
        h = max(1, int(0.5 * fps)); minrun = int(0.3 * fps); trim = int(0.3 * fps)
        a, b = a + trim, b - trim            # contact forms and breaks at the edges: the point "travels" as bodies separate
        if b - a < 2 * h:
            continue
        rec["core_s"] = (b - a) / fps
        for lab, loc, reg in (("A", locA, rA), ("B", locB, rB)):
            L = loc[a:b]; ok = np.isfinite(L).all(1)
            if ok.sum() < 2 * h:
                rec.update({f"net_travel_{lab}_bl": np.nan, f"spread_{lab}_bl": np.nan, f"regions_{lab}": 0, f"main_region_{lab}": None}); continue
            first, last = np.nanmedian(L[:h], axis=0), np.nanmedian(L[-h:], axis=0)
            med = np.nanmedian(L, axis=0)
            rec[f"net_travel_{lab}_bl"] = float(np.linalg.norm(last - first))
            rec[f"spread_{lab}_bl"] = float(np.nanmedian(np.linalg.norm(L[ok] - med, axis=1)))
            r = pd.Series(reg[a:b]).ffill().bfill()
            runs = (r != r.shift()).cumsum(); lens = r.groupby(runs).agg(["first", "size"])
            rec[f"regions_{lab}"] = int(lens[lens["size"] >= minrun]["first"].nunique())
            rec[f"main_region_{lab}"] = r.mode().iat[0] if r.notna().any() else None
        hands = pd.Series([(x == "hand") or (y == "hand") for x, y in zip(rA[a:b], rB[a:b])])
        rec["hand_share"] = float(hands.mean())
        travel = np.nanmax([rec["net_travel_A_bl"], rec["net_travel_B_bl"], 0])
        still = all(np.nan_to_num(rec[k], nan=9) < GRIP_TRAVEL_BL for k in ("net_travel_A_bl", "net_travel_B_bl", "spread_A_bl", "spread_B_bl"))
        rec["label"] = "ROLL" if travel >= ROLL_TRAVEL_BL else "HOLD" if still else "MIXED"
        rows.append(rec)
    return rows, tr


def draw(frame, k, color):
    for a, b in SKELETON_EDGES:
        if k[a, 2] > 0.3 and k[b, 2] > 0.3:
            cv2.line(frame, tuple(k[a, :2].astype(int)), tuple(k[b, :2].astype(int)), color, 3)


def strip(vid, tr, start_s, end_s, n=4, w=300):
    """n frames across one bout, side by side, with both skeletons."""
    vp = (sorted(glob.glob(f"videos/{vid}.*")) + sorted(glob.glob(f"videos/full/{vid}.*")) or [None])[0]; fps = tr.meta["fps"]
    cap = cv2.VideoCapture(vp); tiles = []
    for t in np.linspace(start_s, end_s, n):
        fi = int(t * fps); cap.set(1, fi); ok, f = cap.read()
        if not ok:
            continue
        for j, col in ((0, (255, 160, 0)), (1, (0, 140, 255))):
            if tr.present[fi, j]:
                draw(f, tr.kpts[fi, j], col)
        tiles.append(cv2.resize(f, (w, int(w * f.shape[0] / f.shape[1]))))
    cap.release()
    return np.hstack(tiles) if len(tiles) == n else None


def main():
    cur = pd.read_csv("videos/curation.csv")
    vids = cur[cur.pair_ok.isin(["yes", "partial"]) & (cur.content == "ci_dance")].video.unique().tolist()
    vids = [v for v in vids if f"{v}_full" not in vids]          # prefer the full-length version of a clip
    rows, TR = [], {}
    for v in vids:
        if not Path(f"outputs/{v}/{v}_tracks.npz").exists():
            continue
        r, tr = bouts_for_clip(v); rows += r; TR[v] = tr
    B = pd.DataFrame(rows); B.to_csv(OUT / "bouts.csv", index=False)
    pc = B.groupby("video").agg(bouts=("label", "size"), roll=("label", lambda x: (x == "ROLL").mean()),
                                hold=("label", lambda x: (x == "HOLD").mean()), median_dur_s=("dur_s", "median"),
                                median_travel_bl=("net_travel_A_bl", "median"), hand_share=("hand_share", "median")).round(2)
    pc.to_csv(OUT / "per_clip.csv")
    for lab in ("ROLL", "HOLD", "MIXED"):
        sub = B[B.label == lab].sample(min(6, (B.label == lab).sum()), random_state=0) if (B.label == lab).any() else B.iloc[:0]
        strips = [s for s in (strip(r.video, TR[r.video], r.start_s, r.end_s) for r in sub.itertuples()) if s is not None]
        if strips:
            W = max(x.shape[1] for x in strips)
            cv2.imwrite(str(OUT / f"check_{lab.lower()}.jpg"), np.vstack([cv2.copyMakeBorder(x, 0, 6, 0, W - x.shape[1], cv2.BORDER_CONSTANT) for x in strips]),
                        [cv2.IMWRITE_JPEG_QUALITY, 75])
    md = [f"# Rolling vs gripping: {len(B)} contact bouts >= {MIN_BOUT_S:g} s in {B.video.nunique()} clips\n",
          B.label.value_counts().to_frame("bouts").to_markdown(),
          "\n\nBy label (medians):\n\n" + B.groupby("label")[["dur_s", "net_travel_A_bl", "net_travel_B_bl", "spread_A_bl", "spread_B_bl", "regions_A", "regions_B", "hand_share"]].median().round(2).to_markdown(),
          "\n\nPer clip:\n\n" + pc.to_markdown(),
          "\n\nMost common main regions in ROLL bouts:\n\n" + B[B.label == "ROLL"].groupby(["main_region_A", "main_region_B"]).size().sort_values(ascending=False).head(8).to_frame("n").to_markdown()]
    (OUT / "report.md").write_text("\n".join(md)); print("\n".join(md))


if __name__ == "__main__":
    main()
