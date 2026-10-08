"""
Ground-truth test of the coupling method on public mocap data: Bigand, Bianco, Abalde & Novembre (2024)
"The geometry of interpersonal synchrony in human dance", Current Biology; data CC BY 4.0,
doi:10.48557/UR2GBG (download: data_external/bigand2024/fetch.sh).

Dyads dance freely for 60 s per trial in a 2x2 within-dyad design: visual contact (a curtain or not) x
music (same song or a different song through earphones). No physical contact. This is the design we
proposed for Phase 2, already run: "vision + different music" vs "no vision + different music" isolates
coupling that can only come from attending to the partner, with everything else (room, system, people,
time) shared.

Questions answered here
  1. Does our statistic (peak |r| of speeds within ±2 s) detect partner coupling? (vision vs curtain)
  2. Does the naive per-trial circular-shift test fire on a shared driver with NO partner information?
     (curtain + same music = both follow the music only)
  3. Does it survive degradation to what our video pipeline sees: a 2-D virtual camera at 25 fps with
     keypoint jitter and Savitzky-Golay derivatives?
Signals: pelvis speed (whole-body travel) and vertical sternum velocity ("bounce", the movement Bigand
et al. found to be vision-driven).
Outputs: outputs/external_bigand/{trials.csv, report.md}
"""
from __future__ import annotations

import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
from scipy.signal import savgol_filter

from src.analysis.coupling_controls import peak, shift_null

DATA = Path("data_external/bigand2024"); OUT = Path("outputs/external_bigand")
FS_IN, FS = 250, 25.0
MARK = ['LB Head', 'LF Head', 'RF Head', 'RB Head', 'Sternum', 'L Shoulder', 'R Shoulder', 'L Elbow', 'L Wrist', 'L Hand', 'R Elbow',
        'R Wrist', 'R Hand', 'Pelvis', 'L Hip', 'R Hip', 'L Knee', 'L Ankle', 'L Foot', 'R Knee', 'R Ankle', 'R Foot', 'Thigh']
STERNUM, PELVIS = MARK.index('Sternum'), MARK.index('Pelvis')
JITTERS = (0.005, 0.02)   # video keypoint jitter in body lengths: public clips measured 0.2-5 px at 65-400 px trunks
                          # (~0.002-0.03 bl); 0.005 = a good tripod recording, 0.02 = typical public clip


def load(path: Path) -> np.ndarray:
    """-> (T, 23, 3) in mm at 25 Hz: the converted .npz when present (fetch.sh), else the original
    250 Hz csv downsampled by block means (NaN-aware)."""
    npz = path.with_suffix(".npz")
    if npz.exists():
        return np.load(npz)["X"].astype(float)
    m = pd.read_csv(path, index_col=0).to_numpy(float)          # 69 x 15000
    X = m.reshape(23, 3, -1).transpose(2, 0, 1)
    T = X.shape[0] // 10 * 10
    with np.errstate(all="ignore"):
        return np.nanmean(X[:T].reshape(-1, 10, 23, 3), axis=1)


def vertical_axis(X: np.ndarray) -> int:
    """The axis on which the head is consistently above the feet."""
    d = np.nanmedian(X[:, 0, :] - X[:, MARK.index('L Foot'), :], axis=0)
    return int(np.argmax(np.abs(d)))


def deriv(p: np.ndarray) -> np.ndarray:
    """Savitzky-Golay first derivative (window 11, order 3) per coordinate, like the video pipeline."""
    out = np.full_like(p, np.nan); ok = np.isfinite(p).all(axis=1)
    if ok.sum() > 20:
        idx = np.flatnonzero(ok); q = p.copy()
        for k in range(p.shape[1]):
            q[:, k] = np.interp(np.arange(len(p)), idx, p[idx, k])
        out = savgol_filter(q, 11, 3, deriv=1, delta=1 / FS, axis=0); out[~ok] = np.nan
    return out


def signals(X: np.ndarray, up: int, jitter: float, rng) -> dict:
    trunk = np.nanmedian(np.linalg.norm(X[:, STERNUM] - X[:, PELVIS], axis=1))     # mm, = 1 body length
    P = X / trunk                                                                  # body lengths
    if jitter > 0:   # 2-D virtual camera looking along the other horizontal axis, plus keypoint jitter
        horiz = [k for k in range(3) if k != up][0]
        P = P[:, :, [horiz, up]] + rng.normal(0, jitter, P[:, :, [horiz, up]].shape)
    pel = deriv(P[:, PELVIS]); ste = deriv(P[:, STERNUM])
    upk = 1 if jitter > 0 else up
    return {"speed": np.linalg.norm(pel, axis=1), "bounce": ste[:, upk]}


def trial(args):
    dyad, tr, vis, mus, jitter, seed = args
    rng = np.random.default_rng(seed)
    try:
        L = load(DATA / f"Dyad_{dyad:02d}/subj_LEFT/tr{tr:02d}.csv"); R = load(DATA / f"Dyad_{dyad:02d}/subj_RIGHT/tr{tr:02d}.csv")
    except (FileNotFoundError, ValueError, OSError):
        return None
    up = vertical_axis(L); sL, sR = signals(L, up, jitter, rng), signals(R, up, jitter, rng)
    row = {"dyad": dyad, "trial": tr, "vision": vis, "same_music": mus, "video_jitter_bl": jitter}
    for k in ("speed", "bounce"):
        lag, r, r0 = peak(sL[k], sR[k], FS)
        row[f"{k}_peak_abs_r"] = abs(r); row[f"{k}_lag_s"] = lag
        if jitter == 0:
            row[f"{k}_naive_p"] = shift_null(sL[k], sR[k], FS, n=200, seed=seed)["p"]
    return row


def contrast(df: pd.DataFrame, col: str, a: dict, b: dict) -> dict:
    """Per-dyad mean of `col` in condition a minus condition b; Wilcoxon across dyads."""
    ma = df[(df.vision == a["vision"]) & (df.same_music == a["mus"])].groupby("dyad")[col].mean()
    mb = df[(df.vision == b["vision"]) & (df.same_music == b["mus"])].groupby("dyad")[col].mean()
    d = (ma - mb).dropna()
    if len(d) < 5:
        return {"n_dyads": len(d)}
    return {"n_dyads": len(d), "mean_diff": float(d.mean()), "sd_diff": float(d.std()), "dyads_positive": int((d > 0).sum()),
            "wilcoxon_p": float(stats.wilcoxon(d, alternative="greater").pvalue)}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    vis = pd.read_csv(DATA / "cond_vis.csv", index_col=0).to_numpy(); mus = pd.read_csv(DATA / "cond_mus.csv", index_col=0).to_numpy()
    dyads = sorted(int(p.name.split("_")[1]) for p in DATA.glob("Dyad_*"))
    jobs = [(d, t, int(vis[d - 1, t - 1]), int(mus[d - 1, t - 1]), video, d * 100 + t)
            for d in dyads for t in range(1, 33) for video in (0.0, *JITTERS)]
    with ProcessPoolExecutor(4) as ex:
        rows = [r for r in ex.map(trial, jobs, chunksize=4) if r is not None]
    df = pd.DataFrame(rows); df.to_csv(OUT / "trials.csv", index=False)

    VD, ND, VS, NS = ({"vision": 1, "mus": 0}, {"vision": 0, "mus": 0}, {"vision": 1, "mus": 1}, {"vision": 0, "mus": 1})
    md = [f"# Coupling method on Bigand et al. (2024) mocap: {df.dyad.nunique()} dyads, {len(df) // (1 + len(JITTERS))} trials\n",
          "Statistic: peak |r| within ±2 s at 25 Hz. Contrasts are per-dyad means, Wilcoxon (one-sided) across dyads.\n"]
    for video in (0.0, *JITTERS):
        sub = df[df.video_jitter_bl == video]
        md.append(f"\n## {f'2-D virtual camera at 25 fps + keypoint jitter {video} body lengths' if video else '3-D mocap (ground truth)'}\n")
        res = []
        for sig in ("speed", "bounce"):
            col = f"{sig}_peak_abs_r"
            res += [{"signal": sig, "contrast": name, **contrast(sub, col, a, b)} for name, a, b in (
                ("PARTNER: vision vs curtain, different music", VD, ND),
                ("partner with shared music: vision vs curtain, same music", VS, NS),
                ("MUSIC: same vs different music, curtain", NS, ND))]
        md.append(pd.DataFrame(res).round(4).to_markdown(index=False))
        cells = sub.groupby(["vision", "same_music"])[[f"{s}_peak_abs_r" for s in ("speed", "bounce")]].mean().round(3)
        md.append("\n\nMean peak |r| per condition:\n\n" + cells.to_markdown())
        if video == 0:
            fp = sub.groupby(["vision", "same_music"])[["speed_naive_p", "bounce_naive_p"]].apply(lambda g: (g < 0.05).mean()).round(3)
            md.append("\n\n**Naive per-trial circular-shift test, fraction of trials 'significant' (p < 0.05).** "
                      "Curtain + different music has no channel between the dancers, so it is the false-positive rate; "
                      "curtain + same music shares only the music.\n\n" + fp.to_markdown())
    (OUT / "report.md").write_text("\n".join(md)); print("\n".join(md))


if __name__ == "__main__":
    main()
