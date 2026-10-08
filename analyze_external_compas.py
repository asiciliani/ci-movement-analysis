"""
Lead/lag ground truth on CoMPAS3D (Burkanova et al. 2025; CC BY-NC 4.0; data_external/compas3d/fetch.sh):
improvised salsa, 9 pairs (beginner / intermediate / professional), 4 songs x 2 takes, leader and
follower roles known, hand-hold connection. Question for the thesis instrument (METHODS H3c): can the
lag of the speed / bounce cross-correlation recover WHO LEADS, and does it survive the degradation to
video (2-D projection, 25 fps-like jitter)?

Per sequence: pelvis (SMPL-X root) horizontal speed and vertical velocity; gap-aware lagged
correlation r(leader_t, follower_t+k), k within ±1 s. Leadership index = mean r over k in (0, 0.5] s
minus mean r over k in [-0.5, 0) s (positive = leader precedes follower), plus the peak lag.
Pair-level test: sign test / Wilcoxon across the 9 pairs (mean over sequences).
Outputs: outputs/external_compas/{sequences.csv, report.md}
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
from scipy.signal import savgol_filter

from src.analysis.coupling_controls import lagged_corr

DATA = Path("data_external/compas3d/trans"); OUT = Path("outputs/external_compas")
LEVEL = {1: "beginner", 2: "intermediate", 3: "beginner", 4: "intermediate", 5: "professional", 6: "intermediate",
         7: "professional", 8: "beginner", 9: "professional"}
JITTERS = (0.0, 0.005, 0.02)   # in body lengths (1 bl ~ 0.5 m pelvis-to-neck); 0 = mocap
BL_M = 0.5


def deriv(x, fps):
    return savgol_filter(x, 11, 3, deriv=1, delta=1 / fps, axis=0)


def signals(trans, fps, up, jitter, rng):
    P = trans / BL_M
    if jitter > 0:   # 2-D camera looking along one horizontal axis, keypoint jitter
        horiz = [k for k in range(3) if k != up][0]
        P = P[:, [horiz, up]] + rng.normal(0, jitter, (len(P), 2)); up_i, hor = 1, [0]
    else:
        up_i, hor = up, [k for k in range(3) if k != up]
    v = deriv(P, fps)
    return {"speed": np.linalg.norm(v[:, hor], axis=1), "bounce": v[:, up_i]}


def leadership(a, b, fps, max_lag_s=1.0, win_s=0.5):
    L = int(round(max_lag_s * fps)); c = lagged_corr(a, b, L); k = np.arange(-L, L + 1) / fps
    pos = (k > 0) & (k <= win_s); neg = (k < 0) & (k >= -win_s)
    i = int(np.nanargmax(np.abs(c)))
    return {"peak_lag_s": float(k[i]), "peak_r": float(c[i]), "lead_index": float(np.nanmean(c[pos]) - np.nanmean(c[neg]))}


def main():
    OUT.mkdir(parents=True, exist_ok=True); rows = []; rng = np.random.default_rng(0)
    for lp in sorted(DATA.glob("Pair*/*/*_leader.npz")):
        fp = Path(str(lp).replace("_leader.npz", "_follower.npz"))
        if not fp.exists():
            continue
        zl, zf = np.load(lp), np.load(fp); fps = float(zl["fps"])
        tl, tf = zl["trans"].astype(float), zf["trans"].astype(float); n = min(len(tl), len(tf)); tl, tf = tl[:n], tf[:n]
        up = int(np.argmin(np.std(tl, axis=0) / (np.abs(np.mean(tl, axis=0)) + 1e-6)))   # vertical: high mean, small spread
        pair = int(lp.parent.parent.name.replace("Pair", ""))
        for j in JITTERS:
            sl, sf = signals(tl, fps, up, j, rng), signals(tf, fps, up, j, rng)
            for sig in ("speed", "bounce"):
                rows.append({"pair": pair, "level": LEVEL[pair], "sequence": lp.parent.name, "jitter_bl": j, "signal": sig,
                             **leadership(sl[sig], sf[sig], fps)})
    df = pd.DataFrame(rows); df.to_csv(OUT / "sequences.csv", index=False)
    md = [f"# Lead/lag on CoMPAS3D: {df.pair.nunique()} pairs, {df.sequence.nunique()} sequences (leader known)\n",
          "lead_index > 0 means the leader's signal precedes the follower's. Pair = mean over its sequences; "
          "tests across pairs (sign test, one-sided Wilcoxon).\n"]
    for j in JITTERS:
        md.append(f"\n## {'mocap' if j == 0 else f'2-D projection + jitter {j} bl'}\n"); res = []
        for sig in ("speed", "bounce"):
            sub = df[(df.jitter_bl == j) & (df.signal == sig)]
            pm = sub.groupby(["pair", "level"])[["lead_index", "peak_lag_s", "peak_r"]].mean().reset_index()
            d = pm.lead_index.to_numpy()
            res.append({"signal": sig, "pairs_leader_first": f"{int((d > 0).sum())}/{len(d)}",
                        "sequences_leader_first": f"{int((sub.lead_index > 0).sum())}/{len(sub)}",
                        "median_lead_index": float(np.median(d)), "median_peak_lag_s": float(pm.peak_lag_s.median()),
                        "sign_test_p": float(stats.binomtest(int((d > 0).sum()), len(d), 0.5, alternative="greater").pvalue),
                        "wilcoxon_p": float(stats.wilcoxon(d, alternative="greater").pvalue)})
            if j == 0:
                md.append(f"\nPer pair ({sig}):\n\n" + pm.round(3).to_markdown(index=False) + "\n")
        md.append(pd.DataFrame(res).round(4).to_markdown(index=False))
    (OUT / "report.md").write_text("\n".join(md)); print("\n".join(md))


if __name__ == "__main__":
    main()
