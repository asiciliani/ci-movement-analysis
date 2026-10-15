"""
Idea B (13 Oct): mirror vs complement. At each moment, are the two bodies in similar postures (mirroring,
imitation) or in complementary ones (one open/high, the other closed/low)?

Posture descriptors per dancer and frame, invariant to image position, scale and left/right:
  level      pelvis height above the own lowest foot           inverted   head below pelvis
  trunk_tilt trunk from vertical (0 upright, 180 inverted)    openness   mean distance of wrists and ankles from the
  knee/hip/elbow angles and arm elevation, as (min, max) of               body centre
             the two sides (left/right swaps do not matter)  stance     ankle spread
Lengths are divided by the dancer's own trunk length, a 3 s rolling median (camera zoom and walking towards the
camera change the image size of both dancers at once: a fixed per-clip scale would make that look like mirroring).
Each descriptor is robust-z-scored per dancer and clip, so the measure is about co-variation, not about two
dancers having the same build or the same camera angle. Similarity S(t) = - mean |zA - zB| over the descriptors
present (>= 6). "shape" = the angles, openness, stance and arms only (no level / tilt / inversion).

Nulls: (1) B circularly shifted against A by 5 s .. T - 5 s (200 shifts); (2) pseudo-pairs: A of one duet with B
of another duet (random circular offsets). A real excess over both is needed; frames in contact are reported
separately because overlapping bodies make the pose model mix limbs between them (spurious similarity).
Per descriptor, the lag-0 Spearman correlation between partners (+ mirror, - complement) against the shift null.

Genres: CI (10 verified duets, 2-D), salsa renders (same 2-D pipeline, 3 clips), salsa CoMPAS3D (3-D markers,
same descriptors computed from the surface markers, no camera). On the 3 render clips the 2-D S(t) is compared
with the 3-D S(t) of the same seconds (does the 2-D measure track what the bodies do?).

Outputs: outputs/mirroring/{per_duet.csv, per_feature.csv, report.md, check_high.jpg, check_low.jpg, examples.csv}
"""
from __future__ import annotations

import glob
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

from src.io.tracks import load_tracks
from src.analysis import describe as D

OUT = Path("outputs/mirroring"); OUT.mkdir(parents=True, exist_ok=True)
SHAPE = ["knee_min", "knee_max", "hip_min", "hip_max", "elbow_min", "elbow_max", "armup_min", "armup_max", "openness", "stance"]
LEVELF = ["level", "trunk_tilt", "inverted"]
FEATS = LEVELF + SHAPE
RNG = np.random.default_rng(0)
N_SHIFT = 200


def rolling_scale(k, fps):
    L = pd.Series(D.trunk_len(k)).rolling(int(3 * fps), center=True, min_periods=int(fps / 2)).median()
    return L.bfill().ffill().to_numpy()


def feats2d(k: np.ndarray, fps: float) -> pd.DataFrame:
    sc = rolling_scale(k, fps)
    P = k[:, :, :2].copy(); P[k[:, :, 2] < D.CONF] = np.nan
    sh = (P[:, 5] + P[:, 6]) / 2; hp = (P[:, 11] + P[:, 12]) / 2; head = P[:, 0]
    tr = sh - hp
    ang = D._angle
    two = lambda a, b: (np.fmin(a, b), np.fmax(a, b))
    kn = two(ang(P[:, 11], P[:, 13], P[:, 15]), ang(P[:, 12], P[:, 14], P[:, 16]))
    hi = two(ang(P[:, 5], P[:, 11], P[:, 13]), ang(P[:, 6], P[:, 12], P[:, 14]))
    el = two(ang(P[:, 5], P[:, 7], P[:, 9]), ang(P[:, 6], P[:, 8], P[:, 10]))
    au = two((sh[:, 1] - P[:, 9, 1]) / sc, (sh[:, 1] - P[:, 10, 1]) / sc)
    centre = (sh + hp) / 2
    ends = P[:, [9, 10, 15, 16]]
    openness = np.nanmean(np.linalg.norm(ends - centre[:, None], axis=2), axis=1) / sc
    foot = np.where(k[:, [15, 16], 2] >= D.CONF, k[:, [15, 16], 1], np.nan)
    with np.errstate(all="ignore"):
        lev = (np.nanmax(foot, 1) - hp[:, 1]) / sc
    f = dict(level=lev, trunk_tilt=np.degrees(np.arctan2(np.abs(tr[:, 0]), -tr[:, 1])), inverted=(head[:, 1] - hp[:, 1]) / sc,
             knee_min=kn[0], knee_max=kn[1], hip_min=hi[0], hip_max=hi[1], elbow_min=el[0], elbow_max=el[1],
             armup_min=au[0], armup_max=au[1], openness=openness, stance=np.abs(P[:, 15, 0] - P[:, 16, 0]) / sc)
    return pd.DataFrame(f)[FEATS]


# 3-D: same descriptors from the 53 CoMPAS3D surface markers (layout in rolling_3d.py), z up, metres
HAND_L, HAND_R, HEAD = list(range(40, 44)), list(range(44, 48)), list(range(48, 53))
FOOT_L, FOOT_R = [9, 10, 11, 12, 30, 31, 32, 33, 34], [23, 24, 25, 26, 35, 36, 37, 38, 39]


def feats3d(M: np.ndarray) -> pd.DataFrame:
    from roles import TRUNK
    c = M[:, TRUNK].mean(1); h = M[:, HEAD].mean(1); hl, hr = M[:, HAND_L].mean(1), M[:, HAND_R].mean(1)
    fl, fr = M[:, FOOT_L].mean(1), M[:, FOOT_R].mean(1); low = np.fmin(M[:, FOOT_L, 2].min(1), M[:, FOOT_R, 2].min(1))
    sc = np.nanmedian(h[:, 2] - low) / 2.6           # ~ trunk length: head-to-floor standing is ~2.6 trunk lengths in 2-D
    up = h - c
    au = np.sort(np.c_[hl[:, 2] - h[:, 2], hr[:, 2] - h[:, 2]], 1) / sc
    f = dict(level=(c[:, 2] - low) / sc, trunk_tilt=np.degrees(np.arctan2(np.linalg.norm(up[:, :2], axis=1), up[:, 2])),
             inverted=(c[:, 2] - h[:, 2]) / sc, armup_min=au[:, 0], armup_max=au[:, 1],
             openness=np.mean([np.linalg.norm(x - c, axis=1) for x in (hl, hr, fl, fr)], 0) / sc,
             stance=np.linalg.norm((fl - fr)[:, :2], axis=1) / sc)
    return pd.DataFrame(f)


def robust_z(F: pd.DataFrame) -> np.ndarray:
    med = F.median(); iqr = (F.quantile(0.75) - F.quantile(0.25)).replace(0, np.nan)
    return ((F - med) / (iqr / 1.35)).clip(-3, 3).to_numpy()


def sim(zA, zB, min_feats):
    d = np.abs(zA - zB); n = np.isfinite(d).sum(1)
    with np.errstate(all="ignore"):
        s = -np.nanmean(d, 1)
    s[n < min_feats] = np.nan
    return s


def shift_null(zA, zB, mask, fps, min_feats, n=N_SHIFT, rng=RNG):
    T = len(zA); lo = int(5 * fps)
    if T < 2 * lo + 10:
        return np.full(n, np.nan)
    out = []
    for d in rng.integers(lo, T - lo, n):
        s = sim(zA, np.roll(zB, d, axis=0), min_feats); out.append(np.nanmean(s[mask]))
    return np.array(out)


def load_ci(vid):
    tr = load_tracks(f"outputs/{vid}/{vid}_tracks.npz"); fps = float(tr.meta["fps"])
    kA, kB = tr.kpts[:, 0].astype(float), tr.kpts[:, 1].astype(float)
    both = tr.present.all(1)
    FA, FB = feats2d(kA, fps), feats2d(kB, fps)
    FA[~tr.present[:, 0]] = np.nan; FB[~tr.present[:, 1]] = np.nan
    s = (np.nanmedian(D.trunk_len(kA)) + np.nanmedian(D.trunk_len(kB))) / 2
    dmin = D.contact_regions(kA, kB, s)[0]
    return dict(name=vid, fps=fps, FA=FA, FB=FB, both=both, dmin=dmin)


def analyse(units, genre, cols, min_feats, label):
    """units: list of dicts with FA, FB (DataFrames), both, dmin (or None), fps. Returns per-unit rows and per-feature rows."""
    rows, frows = [], []
    Z = [(robust_z(u["FA"][cols]), robust_z(u["FB"][cols])) for u in units]
    for i, u in enumerate(units):
        zA, zB = Z[i]; S = sim(zA, zB, min_feats); fps = u["fps"]
        masks = {"all": u["both"] & np.isfinite(S)}
        if u.get("dmin") is not None:
            dm = np.nan_to_num(u["dmin"], nan=99)
            masks["contact"] = masks["all"] & (dm < 0.25); masks["apart"] = masks["all"] & (dm > 1.0)
        for mname, m in masks.items():
            if m.sum() < 5 * fps:
                continue
            obs = float(np.nanmean(S[m])); null = shift_null(zA, zB, m, fps, min_feats)
            # pseudo-pairs: this A with every other unit's B, random circular offset, over the overlapping length
            ps = []
            for j, v in enumerate(units):
                if j == i or (u.get("group") is not None and u.get("group") == v.get("group")):
                    continue
                zb = Z[j][1]; T = min(len(zA), len(zb))
                for off in RNG.integers(0, len(zb), 5):
                    zbs = np.roll(zb, off, axis=0)[:T]
                    s2 = sim(zA[:T], zbs, min_feats); mm = m[:T] & np.isfinite(s2)
                    if mm.sum() > fps:
                        ps.append(np.nanmean(s2[mm]))
            ps = np.array(ps)
            rows.append(dict(genre=genre, unit=u["name"], features=label, frames=mname, n_frames=int(m.sum()), S=obs,
                             shift_mean=float(np.nanmean(null)), excess_shift=obs - float(np.nanmean(null)),
                             z_shift=(obs - np.nanmean(null)) / np.nanstd(null), p_shift=float(np.mean(null >= obs)),
                             pseudo_mean=float(np.nanmean(ps)) if len(ps) else np.nan, excess_pseudo=obs - float(np.nanmean(ps)) if len(ps) else np.nan,
                             p_pseudo=float(np.mean(ps >= obs)) if len(ps) else np.nan))
        if label == "all":
            m = masks["all"]
            lo = int(5 * fps)
            nulls = {f: [] for f in cols}
            for d in RNG.integers(lo, max(len(zA) - lo, lo + 1), 100):
                zr = np.roll(zB, d, axis=0)
                for k_, f in enumerate(cols):
                    a, b = zA[m, k_], zr[m, k_]; ok = np.isfinite(a) & np.isfinite(b)
                    nulls[f].append(stats.spearmanr(a[ok], b[ok])[0] if ok.sum() > 50 else np.nan)
            for k_, f in enumerate(cols):
                a, b = zA[m, k_], zB[m, k_]; ok = np.isfinite(a) & np.isfinite(b)
                r = stats.spearmanr(a[ok], b[ok])[0] if ok.sum() > 50 else np.nan
                nl = np.array(nulls[f], float)
                frows.append(dict(genre=genre, unit=u["name"], feature=f, r=r, null_mean=np.nanmean(nl), null_sd=np.nanstd(nl),
                                  z=(r - np.nanmean(nl)) / np.nanstd(nl) if np.nanstd(nl) > 0 else np.nan))
    return rows, frows


def salsa_render_units():
    us = []
    for p in sorted(q for q in Path("outputs").glob("salsa_*/salsa_*_tracks.npz") if q.parent.name == q.name.replace("_tracks.npz", "")):
        tr = load_tracks(p); fps = float(tr.meta["fps"])
        kA, kB = tr.kpts[:, 0].astype(float), tr.kpts[:, 1].astype(float)
        FA, FB = feats2d(kA, fps), feats2d(kB, fps); FA[~tr.present[:, 0]] = np.nan; FB[~tr.present[:, 1]] = np.nan
        s = (np.nanmedian(D.trunk_len(kA)) + np.nanmedian(D.trunk_len(kB))) / 2
        us.append(dict(name=p.parent.name, fps=fps, FA=FA, FB=FB, both=tr.present.all(1), dmin=D.contact_regions(kA, kB, s)[0]))
    return us


def salsa3d_units(max_s=None, only=None):
    root = Path("data_external/compas3d/markers"); us = []
    for ld in sorted(root.glob("Pair*/*/*_leader.npz")):
        seq = ld.parent.name
        if only and seq not in only:
            continue
        fd = ld.parent / ld.name.replace("leader", "follower")
        if not fd.exists():
            continue
        z = np.load(ld); fps = float(z["fps"]); ML = z["markers"]; MF = np.load(fd)["markers"]
        if max_s:
            ML, MF = ML[:int(max_s * fps)], MF[:int(max_s * fps)]
        step = 2                                           # 15 fps, like the CI video
        FA, FB = feats3d(ML[::step]), feats3d(MF[::step])
        us.append(dict(name=seq, group=ld.parent.parent.name, fps=fps / step, FA=FA, FB=FB, both=np.ones(len(FA), bool), dmin=None))
    return us


def main():
    ci_vids = pd.read_csv("outputs/grammar/per_clip.csv").video.tolist()
    ci = [load_ci(v) for v in ci_vids]
    sal2 = salsa_render_units()
    sal3 = salsa3d_units()
    S3 = [c for c in sal3[0]["FA"].columns]
    rows, frows = [], []
    for genre, units, cols, mf in (("CI 2-D", ci, FEATS, 6), ("salsa 2-D render", sal2, FEATS, 6), ("salsa 3-D mocap", sal3, S3, 5)):
        r, f = analyse(units, genre, cols, mf, "all"); rows += r; frows += f
        if genre != "salsa 3-D mocap":
            r, _ = analyse(units, genre, SHAPE, 5, "shape"); rows += r
        # the 2-D descriptors restricted to those the 3-D markers also give (same comparison across genres)
        r, _ = analyse(units, genre, S3, 5, "common7"); rows += r
        print(f"[mirroring] {genre} done", flush=True)
    df = pd.DataFrame(rows); fdf = pd.DataFrame(frows)
    df.to_csv(OUT / "per_duet.csv", index=False); fdf.to_csv(OUT / "per_feature.csv", index=False)

    # 2-D vs 3-D on the same render seconds
    val = []
    for u2 in sal2:
        seq = u2["name"].replace("salsa_", "")
        u3 = salsa3d_units(max_s=60, only={seq})
        if not u3:
            continue
        u3 = u3[0]
        s2 = sim(robust_z(u2["FA"][S3]), robust_z(u2["FB"][S3]), 5)
        s3 = sim(robust_z(u3["FA"]), robust_z(u3["FB"]), 5)
        a = pd.Series(s2).rolling(int(u2["fps"]), center=True, min_periods=5).mean().to_numpy()[::2]   # 30 -> 15 fps
        b = pd.Series(s3).rolling(15, center=True, min_periods=5).mean().to_numpy()
        T = min(len(a), len(b)); ok = np.isfinite(a[:T]) & np.isfinite(b[:T])
        null = [stats.spearmanr(a[:T][ok], np.roll(b[:T], d)[ok])[0] for d in RNG.integers(75, T - 75, 200)]
        r = stats.spearmanr(a[:T][ok], b[:T][ok])[0]
        val.append(dict(seq=seq, n=int(ok.sum()), r_2d_3d=r, null_mean=float(np.mean(null)), p=float(np.mean(np.array(null) >= r))))
    val = pd.DataFrame(val); val.to_csv(OUT / "validation_2d_vs_3d.csv", index=False)

    # summaries
    def summ(sub):
        g = sub.groupby(["genre", "features", "frames"])
        return g.agg(units=("unit", "nunique"), S=("S", "median"), excess_shift=("excess_shift", "median"),
                     n_p_shift_lt05=("p_shift", lambda x: int((x < 0.05).sum())), excess_pseudo=("excess_pseudo", "median"),
                     n_p_pseudo_lt05=("p_pseudo", lambda x: int((x < 0.05).sum()))).round(3)
    sm = summ(df)
    fz = fdf.groupby(["genre", "feature"]).agg(r_median=("r", "median"), null_median=("null_mean", "median"), z_median=("z", "median"),
                                              n_pos=("z", lambda x: int((x > 2).sum())), n_neg=("z", lambda x: int((x < -2).sum())), n=("z", "size")).round(2)
    ci_all = df[(df.genre == "CI 2-D") & (df.features == "all") & (df.frames == "all")]
    md = ["# Mirror vs complement: frame-wise posture similarity between partners\n",
          "Method in the docstring of mirroring.py. S = - mean |zA - zB| over robust-z posture descriptors (0 = identical; "
          "about -1.1 for independent standard normals). Excess = S minus the null mean (> 0: more similar than the null).\n",
          "## Summary (medians over duets / sequences)\n", sm.to_markdown(), "",
          "## CI per duet (all descriptors, all frames)\n",
          ci_all[["unit", "n_frames", "S", "excess_shift", "z_shift", "p_shift", "excess_pseudo", "p_pseudo"]].round(3).to_markdown(index=False), "",
          "## Per descriptor: lag-0 Spearman between partners vs shift null (+ mirror / - complement; counts of units with |z| > 2)\n",
          fz.to_markdown(), "",
          "## 2-D measure vs 3-D truth on the salsa renders (1 s smoothed S(t), 7 common descriptors)\n", val.round(3).to_markdown(index=False)]
    (OUT / "report.md").write_text("\n".join(md)); print("\n".join(md))




# ------------------------------------------------------------------------------------------- controls and check sheets
def iou(b1, b2):
    x0 = np.fmax(b1[:, 0], b2[:, 0]); y0 = np.fmax(b1[:, 1], b2[:, 1]); x1 = np.fmin(b1[:, 2], b2[:, 2]); y1 = np.fmin(b1[:, 3], b2[:, 3])
    inter = np.clip(x1 - x0, 0, None) * np.clip(y1 - y0, 0, None)
    a = lambda b: (b[:, 2] - b[:, 0]) * (b[:, 3] - b[:, 1])
    return inter / (a(b1) + a(b2) - inter)


def excess(zA, zB, m, fps, min_feats, lo_s, hi_s, n=N_SHIFT):
    S = sim(zA, zB, min_feats); m = m & np.isfinite(S)
    if m.sum() < 5 * fps:
        return np.nan, np.nan, int(m.sum())
    T = len(zA); sh = RNG.integers(int(lo_s * fps), int(min(hi_s * fps, T - lo_s * fps)), n) * RNG.choice([-1, 1], n)
    null = np.array([np.nanmean(sim(zA, np.roll(zB, d, axis=0), min_feats)[m]) for d in sh])
    obs = np.nanmean(S[m]); return float(obs - null.mean()), float(np.mean(null >= obs)), int(m.sum())


def controls():
    """CI: is the excess similarity (a) pose-model mixing of overlapping bodies, (b) slow co-occurrence of the same
    kind of activity (both on the floor in the same phase) rather than moment-to-moment imitation? (b) uses a local
    null: B shifted by only 1-3 s, which keeps the phase (what the duet is doing) and breaks the moment."""
    import state_grammar as SG
    rows = []
    for v in pd.read_csv("outputs/grammar/per_clip.csv").video.tolist():
        tr = load_tracks(f"outputs/{v}/{v}_tracks.npz"); u = load_ci(v); fps = u["fps"]
        st = SG.frame_states(v)[0]
        ov = np.nan_to_num(iou(tr.bbox[:, 0].astype(float), tr.bbox[:, 1].astype(float)), nan=0)
        dm = np.nan_to_num(u["dmin"], nan=99)
        for cols, lab, mf in ((FEATS, "all", 6), (SHAPE, "shape", 5)):
            zA, zB = robust_z(u["FA"][cols]), robust_z(u["FB"][cols])
            masks = {"all": u["both"], "boxes_IoU<0.2": u["both"] & (ov < 0.2), "apart(>1bl)": u["both"] & (dm > 1.0),
                     "not_floor_or_share_state": u["both"] & np.isin(st, ["apart", "near", "contact"]), "floor_state": u["both"] & (st == "floor")}
            for mn, m in masks.items():
                for null, lo, hi in (("shift>=5s", 5, 1e9), ("local 1-3s", 1, 3)):
                    ex, p, n = excess(zA, zB, m, fps, mf, lo, hi)
                    rows.append(dict(genre="CI 2-D", unit=v, features=lab, frames=mn, null=null, n=n, excess=ex, p=p))
    for u in salsa3d_units():
        zA, zB = robust_z(u["FA"]), robust_z(u["FB"])
        for null, lo, hi in (("shift>=5s", 5, 1e9), ("local 1-3s", 1, 3)):
            ex, p, n = excess(zA, zB, u["both"], u["fps"], 5, lo, hi, n=100)
            rows.append(dict(genre="salsa 3-D mocap", unit=u["name"], features="common7", frames="all", null=null, n=n, excess=ex, p=p))
    df = pd.DataFrame(rows); df.to_csv(OUT / "controls.csv", index=False)
    s = df.groupby(["genre", "features", "frames", "null"]).agg(units=("excess", lambda x: int(x.notna().sum())), frames_n=("n", "sum"),
                                                                excess_median=("excess", "median"),
                                                                n_p_lt05=("p", lambda x: int((x < 0.05).sum()))).round(3)
    md = "\n## Controls (CI: overlap, apart, state; local 1-3 s null; salsa 3-D for comparison)\n\n" + s.to_markdown()
    with open(OUT / "report.md", "a") as fh:
        fh.write(md + "\n")
    print(md)


def sheets():
    """Highest / lowest 1-s similarity moments, 2 per duet each (>= 10 s apart), both skeletons drawn."""
    import cv2
    from roles import tile, video_path
    hi, lo = [], []
    for v in pd.read_csv("outputs/grammar/per_clip.csv").video.tolist():
        u = load_ci(v); fps = u["fps"]
        S = pd.Series(sim(robust_z(u["FA"][FEATS]), robust_z(u["FB"][FEATS]), 6)).rolling(int(fps), center=True, min_periods=int(fps * 0.8)).mean().to_numpy()
        S[~u["both"]] = np.nan
        for lst, sign in ((hi, -1), (lo, 1)):
            order = np.argsort(np.where(np.isfinite(S), sign * S, np.inf)); picked = []
            for i in order:
                if not np.isfinite(S[i]):
                    continue
                if all(abs(i - j) > 10 * fps for j in picked):
                    picked.append(i)
                if len(picked) == 2:
                    break
            lst += [(v, int(i), float(S[i]), float(u["dmin"][i]) if np.isfinite(u["dmin"][i]) else np.nan) for i in picked]
    ex = pd.DataFrame([dict(kind=k, video=v, frame=f, S=s, dmin_bl=d) for k, L in (("high", hi), ("low", lo)) for v, f, s, d in L])
    ex.insert(0, "id", range(len(ex))); ex["verdict"] = ""; ex.to_csv(OUT / "examples_sample.csv", index=False)
    for kind in ("high", "low"):
        tiles = []
        for r in ex[ex.kind == kind].itertuples():
            tr = load_tracks(f"outputs/{r.video}/{r.video}_tracks.npz"); cap = cv2.VideoCapture(video_path(r.video))
            tiles.append(tile(cap, tr, r.frame, f"#{r.id} {r.video[:8]} {r.frame / tr.meta['fps']:.0f}s S={r.S:.2f} d={r.dmin_bl:.1f}", w=310, h=260))
            cap.release()
        while len(tiles) % 4:
            tiles.append(np.zeros_like(tiles[0]))
        cv2.imwrite(str(OUT / f"check_{kind}.jpg"), np.vstack([np.hstack(tiles[i:i + 4]) for i in range(0, len(tiles), 4)]), [cv2.IMWRITE_JPEG_QUALITY, 82])
    print(ex.to_string())



# ------------------------------------------------------------------------------------------- segment-direction variant
# (design input relayed by the coordinator, after github.com/jeremyipark/vision-demos dance_sync, Apache-2.0)
SEGS = {"uarm_L": (5, 7), "farm_L": (7, 9), "thigh_L": (11, 13), "shin_L": (13, 15),
        "uarm_R": (6, 8), "farm_R": (8, 10), "thigh_R": (12, 14), "shin_R": (14, 16)}
SEG_W = {"uarm": 1.0, "farm": 0.7, "thigh": 2.0, "shin": 1.0}
TOL_DEG = 10.0


def seg_angles(k):
    """Signed segment directions (deg) in the dancer's own torso frame (up = mid-hip -> mid-shoulder), plus torso
    lean from image vertical. Columns: the 8 segments, 'lean'. Image x is mirrored per dancer only through the data."""
    P = k[:, :, :2].copy(); P[k[:, :, 2] < D.CONF] = np.nan
    up = (P[:, 5] + P[:, 6]) / 2 - (P[:, 11] + P[:, 12]) / 2
    a_up = np.arctan2(up[:, 0], -up[:, 1])                       # 0 = upright, + = leaning to image right
    out = {}
    for n, (i, j) in SEGS.items():
        v = P[:, j] - P[:, i]; a = np.arctan2(v[:, 0], -v[:, 1])
        out[n] = np.degrees(np.angle(np.exp(1j * (a - a_up))))
    out["lean"] = np.degrees(a_up)
    return pd.DataFrame(out)


def seg_dist(A, B, mirror=False):
    """Weighted mean angular difference (deg, minus a TOL_DEG tolerance) between postures; mirror=True reflects B
    (angles negated, left/right segments swapped). A, B: (T, 9) arrays in SEGS order + lean."""
    names = list(SEGS) + ["lean"]
    if mirror:
        idx = [names.index(n.replace("_L", "_X").replace("_R", "_L").replace("_X", "_R")) for n in names]
        B = -B[:, idx]
    d = np.abs(np.degrees(np.angle(np.exp(1j * np.radians(A - B)))))
    d = np.clip(d - TOL_DEG, 0, None)
    w = np.array([SEG_W[n.split("_")[0]] if n != "lean" else 2.0 for n in names])
    ok = np.isfinite(d); W = (ok * w).sum(1)
    out = np.where(W >= 0.7 * w.sum(), np.nansum(np.where(ok, d, 0) * w, 1) / np.maximum(W, 1e-9), np.nan)
    return out


def best_lag(A, B, mirror, lag=2):
    """Per frame, the smallest distance to B within +-lag frames (a small delay is not a shape difference)."""
    ds = np.stack([seg_dist(A, np.roll(B, l, axis=0), mirror) for l in range(-lag, lag + 1)])
    with np.errstate(all="ignore"):
        return np.nanmin(ds, 0)


def segments():
    rows = []
    units = []
    for v in pd.read_csv("outputs/grammar/per_clip.csv").video.tolist():
        tr = load_tracks(f"outputs/{v}/{v}_tracks.npz"); units.append(("CI 2-D", v, tr))
    for p in sorted(q for q in Path("outputs").glob("salsa_*/salsa_*_tracks.npz") if q.parent.name == q.name.replace("_tracks.npz", "")):
        units.append(("salsa 2-D render", p.parent.name, load_tracks(p)))
    data = []
    for g, v, tr in units:
        fps = float(tr.meta["fps"]); k = tr.kpts.astype(float)
        full = tr.present.all(1) & (k[:, :, 5:, 2] >= D.CONF).all(2).all(1)      # both bodies fully in shot (all 12 body keypoints confident; face ignored)
        A, B = seg_angles(k[:, 0]).to_numpy(), seg_angles(k[:, 1]).to_numpy()
        A[~full] = np.nan; B[~full] = np.nan
        data.append((g, v, fps, A, B, full))
    for i, (g, v, fps, A, B, full) in enumerate(data):
        for mirror in (False, True):
            d = best_lag(A, B, mirror); m = full & np.isfinite(d)
            if m.sum() < 5 * fps:
                rows.append(dict(genre=g, unit=v, mode="mirror" if mirror else "same-side", n_full=int(m.sum()))); continue
            obs = np.nanmean(d[m]); T = len(A)
            null = np.array([np.nanmean(best_lag(A, np.roll(B, s, axis=0), mirror)[m]) if np.isfinite(best_lag(A, np.roll(B, s, axis=0), mirror)[m]).any() else np.nan for s in RNG.integers(int(5 * fps), T - int(5 * fps), 100)])
            ps = []
            for j, (g2, v2, f2, A2, B2, full2) in enumerate(data):
                if j == i or g2 != g:
                    continue
                Tm = min(T, len(B2))
                for off in RNG.integers(0, len(B2), 3):
                    dd = best_lag(A[:Tm], np.roll(B2, off, axis=0)[:Tm], mirror); mm = m[:Tm] & np.isfinite(dd)
                    if mm.sum() > fps:
                        ps.append(np.nanmean(dd[mm]))
            # calibrated score: 0 % = median distance at >= 2 s apart within the clip, 100 % = the clip's 10th percentile
            far = np.nanmedian(np.concatenate([best_lag(A, np.roll(B, s, axis=0), mirror)[m] for s in RNG.integers(int(2 * fps), T - int(2 * fps), 20)]))
            p10 = np.nanpercentile(d[m], 10)
            rows.append(dict(genre=g, unit=v, mode="mirror" if mirror else "same-side", n_full=int(m.sum()), mean_deg=obs,
                             shift_mean=float(np.nanmean(null)), excess_shift_deg=float(np.nanmean(null) - obs), p_shift=float(np.mean(null[np.isfinite(null)] <= obs)),
                             pseudo_mean=float(np.mean(ps)) if ps else np.nan, excess_pseudo_deg=float(np.mean(ps) - obs) if ps else np.nan,
                             p_pseudo=float(np.mean(np.array(ps) <= obs)) if ps else np.nan,
                             calibrated_score_pct=float(100 * (far - np.nanmedian(d[m])) / (far - p10)) if far > p10 else np.nan))
    df = pd.DataFrame(rows); df.to_csv(OUT / "segments_per_duet.csv", index=False)
    s = df.groupby(["genre", "mode"]).agg(units=("mean_deg", lambda x: int(x.notna().sum())), full_frames=("n_full", "sum"),
                                          mean_deg=("mean_deg", "median"), excess_shift_deg=("excess_shift_deg", "median"),
                                          n_p_shift_lt05=("p_shift", lambda x: int((x < 0.05).sum())),
                                          excess_pseudo_deg=("excess_pseudo_deg", "median"), n_p_pseudo_lt05=("p_pseudo", lambda x: int((x < 0.05).sum())),
                                          calibrated_pct=("calibrated_score_pct", "median")).round(2)
    md = ("\n## Variant (v2, face keypoints not required): segment directions in each torso frame (+-2 frame best match, 10 deg tolerance, core weighted; "
          "only frames with both bodies fully in shot)\n\nDistances in degrees (lower = more similar); excess = null - observed "
          "(> 0: more similar than the null). Mirror = B reflected left/right. In 2-D a same-side movement of two dancers facing "
          "each other looks mirrored in the image and vice versa: mirror vs same-side cannot be read as imitation style without "
          "the facing direction.\n\n" + s.to_markdown() + "\n\nPer unit:\n\n" + df.round(3).to_markdown(index=False))
    with open(OUT / "report.md", "a") as fh:
        fh.write(md + "\n")
    print(md)


def segments_controls():
    """Segment variant, CI: frames with both bodies fully in shot AND separate boxes (IoU < 0.2), shift >= 5 s vs local 1-3 s null."""
    rows = []
    for v in pd.read_csv("outputs/grammar/per_clip.csv").video.tolist():
        tr = load_tracks(f"outputs/{v}/{v}_tracks.npz"); fps = float(tr.meta["fps"]); k = tr.kpts.astype(float)
        full = tr.present.all(1) & (k[:, :, 5:, 2] >= D.CONF).all(2).all(1)
        sep = np.nan_to_num(iou(tr.bbox[:, 0].astype(float), tr.bbox[:, 1].astype(float)), nan=0) < 0.2
        A, B = seg_angles(k[:, 0]).to_numpy(), seg_angles(k[:, 1]).to_numpy(); A[~full] = np.nan; B[~full] = np.nan
        for mirror in (False, True):
            d = best_lag(A, B, mirror)
            for mn, m in (("full", full), ("full & IoU<0.2", full & sep)):
                m = m & np.isfinite(d)
                if m.sum() < 5 * fps:
                    continue
                obs = np.nanmean(d[m]); T = len(A)
                for null, lo, hi in (("shift>=5s", 5, T / fps - 5), ("local 1-3s", 1, 3)):
                    sh = RNG.integers(int(lo * fps), int(hi * fps), 100) * RNG.choice([-1, 1], 100)
                    nl = np.array([np.nanmean(best_lag(A, np.roll(B, x, axis=0), mirror)[m]) for x in sh]); nl = nl[np.isfinite(nl)]
                    rows.append(dict(unit=v, mode="mirror" if mirror else "same-side", frames=mn, null=null, n=int(m.sum()),
                                     excess_deg=float(nl.mean() - obs), p=float(np.mean(nl <= obs))))
    df = pd.DataFrame(rows); df.to_csv(OUT / "segments_controls.csv", index=False)
    s = df.groupby(["mode", "frames", "null"]).agg(units=("unit", "nunique"), frames_n=("n", "sum"), excess_deg=("excess_deg", "median"),
                                                   n_p_lt05=("p", lambda x: int((x < 0.05).sum()))).round(2)
    md = "\n## Segment variant, CI controls (overlap removed, local 1-3 s null)\n\n" + s.to_markdown()
    with open(OUT / "report.md", "a") as fh:
        fh.write(md + "\n")
    print(md)


if __name__ == "__main__":
    {"main": main, "controls": controls, "sheets": sheets, "segments": segments, "segments_controls": segments_controls}[sys.argv[1] if len(sys.argv) > 1 else "main"]()
