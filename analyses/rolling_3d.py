"""
Rolling vs gripping in 3-D, on salsa mocap with a known answer (AUDIT 41: not measurable with 2-D skeletons).

CoMPAS3D (Burkanova et al. 2025, CC BY-NC 4.0) ships, per dancer, 53 observed mocap markers: points on the
body surface, in one world frame for both partners. Same index layout for every dancer (checked by rigid-group
clustering): 40-47 hands, 4-6/13 and 18-20/27 forearms, 9-12/30-34 and 23-26/35-39 shanks/feet, 48-52 head,
the rest trunk (incl. upper arms and hips).

  contact        grip = hand markers of both dancers < CONTACT_M (a palm-to-palm hold puts the back-of-hand
                 markers ~5-8 cm apart); surface = any pair with trunk, forearm or head < its threshold
                 (CONTACT_TRUNK_M when trunk markers are involved, see contact_track)
  body chart     each dancer's markers placed in a canonical 3-D layout: classical MDS of the median (over the
                 sequence) distance between every two of that dancer's markers. A grip keeps its chart
                 position however the arm turns; that is what the 2-D version could not do.
  location       per frame and body, the soft-min weighted chart position of the markers in surface contact
                 (distances normalised by their threshold, weights exp(-(d - dmin) / SIGMA)); low-passed at 2 Hz
  travel         per surface-contact bout (>= 1 s; edges trimmed 0.3 s) or annotated figure: net displacement of
                 the location between the first and the last 0.5 s, max over the two bodies (m on the body chart)

Known-answer checks, with the dance-move annotations shipped with the data (one label per ~2.5 s figure):
  1. "closed hold" (the leader's hand on the follower's back) has more hand-trunk contact than "open hold"
  2. turns under the arm with an open hold keep the contact on the hands: low travel (the 2-D failure)
  3. "hands change behind/over/on the back" figures move the contact over the body: high travel
  4. the 2-D ROLL/HOLD labels of rolling_contact.py on the rendered video vs 3-D travel in the same bouts

Outputs: outputs/rolling_3d/{segments.csv, bouts.csv, compare_2d.csv, report.md, travel_by_figure.png}
"""
from __future__ import annotations

import glob
import re
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats
from scipy.signal import butter, filtfilt

ROOT = Path("data_external/compas3d")
OUT = Path("outputs/rolling_3d"); OUT.mkdir(parents=True, exist_ok=True)
CONTACT_M, CONTACT_TRUNK_M, SIGMA, MIN_BOUT_S, TRIM_S, END_S = 0.10, 0.16, 0.15, 1.0, 0.3, 0.5
REGION = np.array(["trunk"] * 53, dtype=object)
REGION[40:48] = "hand"; REGION[[4, 5, 6, 13, 18, 19, 20, 27]] = "forearm"; REGION[48:53] = "head"
REGION[[9, 10, 11, 12, 30, 31, 32, 33, 34, 23, 24, 25, 26, 35, 36, 37, 38, 39]] = "foot"
RIGID = [list(range(40, 44)), list(range(44, 48)), list(range(48, 53))]   # hands, head: rigid marker groups


def body_chart(M):
    """Classical MDS of the median within-body marker distances -> (53, 3) canonical layout (m)."""
    D = np.median(np.linalg.norm(M[::5, :, None] - M[::5, None], axis=-1), axis=0)
    n = len(D); J = np.eye(n) - 1 / n; B = -0.5 * J @ (D ** 2) @ J
    w, V = np.linalg.eigh(B); i = np.argsort(w)[::-1][:3]
    return V[:, i] * np.sqrt(np.maximum(w[i], 0))


def noise_level(M):
    """Median std of within-group distances of rigid marker groups (m): ~0 for a clean capture."""
    sd = [np.linalg.norm(M[:, g[:, None]] - M[:, g[None]], axis=-1).std(0)[np.triu_indices(len(g), 1)].mean()
          for g in map(np.array, RIGID)]
    return float(np.median(sd))


def lowpass(x, fps, hz=2.0):
    b, a = butter(2, hz / (fps / 2)); out = x.copy()
    ok = np.isfinite(x).all(1)
    if ok.sum() > 12:
        out[ok] = filtfilt(b, a, x[ok], axis=0)
    return out


def contact_track(L, F, fps):
    """Per frame: grip flag (hand-hand), surface-contact flag and its chart locations on both bodies, region pairs.

    Two contact kinds are tracked separately, because a closed hold has both at once (one hand in the partner's
    hand, the other on their back) and their average location would be meaningless:
      grip     a hand marker of each dancer within CONTACT_M
      surface  any pair with trunk, forearm or head within its threshold (CONTACT_TRUNK_M when trunk markers are
               involved: they are ~15 cm apart, so a palm on the back can be >10 cm from the nearest one)
    The rolling question is about surface contacts: does their location travel over either body?
    """
    CL, CF = body_chart(L), body_chart(F)
    small = REGION != "trunk"; hand = REGION == "hand"
    thr = np.where(small[:, None] & small[None], CONTACT_M, CONTACT_TRUNK_M)          # (53, 53)
    surf_pair = ~(hand[:, None] & hand[None])
    T = len(L); grip = np.zeros(T, bool); surf = np.zeros(T, bool)
    locL = np.full((T, 3), np.nan); locF = np.full((T, 3), np.nan); regs = np.empty(T, dtype=object)
    for t0 in range(0, T, 500):                         # chunks: 500 x 53 x 53 distances at a time
        d = np.linalg.norm(L[t0:t0 + 500, :, None] - F[t0:t0 + 500, None], axis=-1)
        close = d < thr
        grip[t0:t0 + len(d)] = (close & ~surf_pair).any((1, 2))
        for k in range(len(d)):
            c = close[k] & surf_pair
            regs[t0 + k] = frozenset((REGION[i], REGION[j]) for i, j in zip(*np.nonzero(close[k])))
            if not c.any():
                continue
            surf[t0 + k] = True
            ds = np.where(surf_pair, d[k] / thr, np.inf)                 # normalised so trunk and limb pairs compare
            m = ds.min(); wL = np.exp(-(ds.min(1) - m) / SIGMA); wF = np.exp(-(ds.min(0) - m) / SIGMA)
            locL[t0 + k] = wL @ CL / wL.sum(); locF[t0 + k] = wF @ CF / wF.sum()
    return grip, surf, lowpass(locL, fps), lowpass(locF, fps), regs


def episodes(mask, fps, min_s, merge_gap_s=0.2):
    idx = np.flatnonzero(np.diff(np.r_[0, mask.astype(int), 0]))
    ep = list(zip(idx[::2], idx[1::2])); merged = []
    for a, b in ep:
        if merged and a - merged[-1][1] <= merge_gap_s * fps:
            merged[-1] = (merged[-1][0], b)
        else:
            merged.append((a, b))
    return [(a, b) for a, b in merged if b - a >= min_s * fps]


def travel(loc, a, b, fps):
    h = int(END_S * fps); L = loc[a:b]
    if np.isfinite(L).all(1).sum() < 2 * h:
        return np.nan
    return float(np.linalg.norm(np.nanmedian(L[-h:], 0) - np.nanmedian(L[:h], 0)))


def annotations(seq_dir):
    txt = glob.glob(str(seq_dir / "*.txt"))
    if not txt:
        return pd.DataFrame(columns=["start_s", "end_s", "label"])
    rows = []
    for line in open(txt[0], encoding="utf-8", errors="ignore"):
        f = line.rstrip("\n").split("\t")
        if len(f) >= 9 and f[0] == "Together":
            rows.append(dict(start_s=float(f[3]), end_s=float(f[5]), label=f[8]))
    return pd.DataFrame(rows)


def figure_class(label: str) -> str:
    s = label.lower()
    if re.search(r"hands? change|behind the|on the back|over the follower|around", s):
        return "hand travels over body"
    if "closed" in s or "embrace" in s:
        return "closed hold"
    if "turn" in s and ("open hold" in s or "crossed hold" in s):
        return "turn, hands held"
    if "open hold" in s or "crossed hold" in s or "both hands" in s:
        return "open hold"
    return "other"


def sequence(seq_dir: Path, rows_seg, rows_bout):
    name = seq_dir.name
    L = np.load(seq_dir / f"{name}_leader.npz"); F = np.load(seq_dir / f"{name}_follower.npz")
    fps = float(L["fps"]); ML, MF = L["markers"].astype(float), F["markers"].astype(float)
    T = min(len(ML), len(MF)); ML, MF = ML[:T], MF[:T]
    noise = max(noise_level(ML), noise_level(MF))
    grip, surf, locL, locF, regs = contact_track(ML, MF, fps)
    has = lambda a, b: np.array([(a, b) in r or (b, a) in r for r in regs])
    hand_trunk = has("hand", "trunk")
    for a, b in episodes(surf, fps, MIN_BOUT_S):
        a2, b2 = a + int(TRIM_S * fps), b - int(TRIM_S * fps)
        if b2 - a2 < 2 * END_S * fps:
            continue
        rp = pd.Series([p for r in regs[a2:b2] for p in r if "trunk" in p or "forearm" in p or "head" in p])
        rows_bout.append(dict(seq=name, start_s=a / fps, end_s=b / fps, dur_s=(b - a) / fps, noise_m=noise,
                              travel_leader_m=travel(locL, a2, b2, fps), travel_follower_m=travel(locF, a2, b2, fps),
                              main_regions="-".join(rp.value_counts().index[0]) if len(rp) else "", grip_frac=float(grip[a2:b2].mean())))
    for r in annotations(seq_dir).itertuples():
        a, b = int(r.start_s * fps), min(int(r.end_s * fps), T)
        if b - a < fps:
            continue
        tr = [travel(loc, a + int(TRIM_S * fps), b - int(TRIM_S * fps), fps) for loc in (locL, locF)]
        rows_seg.append(dict(seq=name, start_s=r.start_s, end_s=r.end_s, label=r.label, cls=figure_class(r.label),
                             noise_m=noise, grip_frac=float(grip[a:b].mean()), surface_frac=float(surf[a:b].mean()),
                             hand_trunk_frac=float(hand_trunk[a:b].mean()),
                             travel_m=float(np.nanmax(tr)) if np.isfinite(tr).any() else np.nan))
    return dict(fps=fps, locL=locL, locF=locF, grip=grip, surf=surf)


def compare_2d(cache):
    """2-D ROLL/HOLD labels (rolling_contact.py on the rendered salsa video) vs 3-D travel in the same bouts."""
    import rolling_contact as RC
    rows = []
    for p in sorted(Path("outputs").glob("salsa_*/salsa_*_tracks.npz")):
        vid = p.parent.name; seq = vid.replace("salsa_", "")
        if seq not in cache:
            continue
        c = cache[seq]; fps = c["fps"]
        for b in RC.bouts_for_clip(vid)[0]:
            a, e = int((b["start_s"] + TRIM_S) * fps), int((b["end_s"] - TRIM_S) * fps)
            t3 = np.nanmax([travel(c["locL"], a, e, fps), travel(c["locF"], a, e, fps), np.nan])
            rows.append(dict(video=vid, start_s=b["start_s"], end_s=b["end_s"], label_2d=b["label"],
                             grip_3d_frac=float(c["grip"][a:e].mean()) if e > a else np.nan,
                             surface_3d_frac=float(c["surf"][a:e].mean()) if e > a else np.nan, travel_3d_m=t3))
    return pd.DataFrame(rows)


def main():
    seqs = sorted(p.parent for p in ROOT.glob("markers/Pair*/*/*_leader.npz") if (p.parent / p.name.replace("leader", "follower")).exists())
    rows_seg, rows_bout, cache = [], [], {}
    for s in seqs:
        ann = ROOT / "trans" / s.relative_to(ROOT / "markers")
        for t in glob.glob(str(ann / "*.txt")):          # annotations live with the trans/ download
            (s / Path(t).name).exists() or (s / Path(t).name).symlink_to(Path(t).resolve())
        cache[s.name] = sequence(s, rows_seg, rows_bout)
        print(f"[rolling3d] {s.name}: {sum(r['seq'] == s.name for r in rows_bout)} bouts")
    S = pd.DataFrame(rows_seg); B = pd.DataFrame(rows_bout)
    noisy = sorted(B[B.noise_m > 0.01].seq.unique())
    S, B = S[S.noise_m <= 0.01], B[B.noise_m <= 0.01]
    S.to_csv(OUT / "segments.csv", index=False); B.to_csv(OUT / "bouts.csv", index=False)
    C = compare_2d(cache); C.to_csv(OUT / "compare_2d.csv", index=False)

    order = ["open hold", "turn, hands held", "closed hold", "hand travels over body", "other"]
    tab = S.groupby("cls").agg(figures=("label", "size"), grip=("grip_frac", "median"), surface=("surface_frac", "median"),
                               hand_trunk=("hand_trunk_frac", "median"), travel_m=("travel_m", "median"),
                               travel_measured=("travel_m", lambda x: x.notna().mean())).reindex(order).round(3)
    def mw(x, y, col):
        x, y = S[S.cls == x][col].dropna(), S[S.cls == y][col].dropna()
        return stats.mannwhitneyu(x, y, alternative="greater").pvalue if len(x) > 2 and len(y) > 2 else np.nan
    checks = pd.DataFrame([
        ("closed hold > open hold", "hand_trunk_frac", mw("closed hold", "open hold", "hand_trunk_frac")),
        ("hand travels > turn, hands held", "travel_m", mw("hand travels over body", "turn, hands held", "travel_m")),
        ("hand travels > open hold", "travel_m", mw("hand travels over body", "open hold", "travel_m")),
        ("turn, hands held > open hold (should NOT hold)", "travel_m", mw("turn, hands held", "open hold", "travel_m")),
    ], columns=["check", "measure", "mann_whitney_p_one_sided"]).round(4)

    fig, ax = plt.subplots(figsize=(7, 3.6))
    data = [S[S.cls == c].travel_m.dropna() for c in order[:4]]
    ax.boxplot(data, showfliers=False); ax.set_xticks(range(1, 5)); ax.set_xticklabels(order[:4], fontsize=8)
    ax.set_ylabel("contact travel on body chart (m)"); ax.set_title("Salsa mocap: how far the contact point moves per figure")
    fig.tight_layout(); fig.savefig(OUT / "travel_by_figure.png", dpi=130)

    md = [f"# Rolling vs gripping in 3-D: CoMPAS3D salsa markers ({S.seq.nunique()} sequences, {len(S)} annotated figures, {len(B)} contact bouts)\n",
          f"Grip = hand-hand markers < {CONTACT_M} m; surface contact = pairs with trunk/forearm/head < {CONTACT_M} m ({CONTACT_TRUNK_M} m with trunk markers); location on a per-dancer MDS body chart; travel = net displacement "
          f"between the first and last {END_S} s of the window (edges trimmed {TRIM_S} s), max over the two bodies. "
          f"Excluded as noisy captures (rigid-group distance SD > 1 cm): {', '.join(noisy) or 'none'}.\n",
          "## By annotated figure class\n", tab.to_markdown(), "\n\n## Known-answer checks\n", checks.to_markdown(index=False),
          "\n\n## Contact bouts (>= 1 s)\n", B[["dur_s", "travel_leader_m", "travel_follower_m", "grip_frac"]].describe().round(3).to_markdown(),
          "\n\nMain region pairs:\n\n" + B.main_regions.value_counts(normalize=True).head(8).round(3).to_frame("share").to_markdown()]
    if len(C):
        md += ["\n\n## 2-D labels vs 3-D in the same bouts (rendered video vs mocap)\n",
               C.groupby("label_2d").agg(bouts=("travel_3d_m", "size"), grip_3d=("grip_3d_frac", "median"),
                                         surface_3d=("surface_3d_frac", "median"), travel_3d_median_m=("travel_3d_m", "median")).round(3).to_markdown()]
    (OUT / "report.md").write_text("\n".join(md)); print("\n".join(md))


if __name__ == "__main__":
    main()
