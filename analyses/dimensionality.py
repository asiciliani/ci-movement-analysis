"""
Idea B (13 Oct exploration): "spherical space" / degrees of freedom. Does CI use more dimensions of movement than
other dances? Effective dimensionality of each dancer's pose trajectory in 10-s windows.

Representation   12 COCO keypoints (shoulders, elbows, wrists, hips, knees, ankles; face dropped), centred on
                 the hip midpoint every frame, divided by the window's median trunk length -> 24-D (2-D video). Equal
                 confidence filter for every source: a frame counts only if all 12 keypoints have conf >= 0.5. All sources
                 resampled to 15 fps. Windows of 5 s with >= 60 % valid frames and no identity jump (pelvis > 1 bl/frame).
Measures         participation ratio PR = (sum l)^2 / sum l^2 of the window covariance eigenvalues, and n90 = components
                 for 90 % of the variance, in three versions:
                   raw       covariance of the keypoints as detected
                   denoised  covariance minus the per-coordinate jitter variance (estimated from the Savitzky-Golay
                             smoothing residual; white jitter adds sigma^2 to the diagonal) -> conservative, because the
                             residual also contains real fast movement
                   smooth    covariance of the smoothed trajectory
Validation       Bigand et al. 2024 (3-D mocap, 23 markers -> COCO-like 13 points): does the 2-D projected PR rank trials like
                 the 3-D PR? How much does keypoint jitter inflate PR and does the correction remove it?
Comparison       CI duets (each dancer) vs salsa renders (same video pipeline) vs Bigand free dance (2-D virtual camera,
                 jitter matched to the CI median). Also within CI: windows by duet state, and the share of frames that
                 pass the confidence filter per state (floor / inverted poses fail the detector -> selection bias).

Outputs: outputs/dimensionality/{windows.csv, bigand_validation.csv, per_dancer.csv, report.md, pr_by_source.png}
"""
from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
from scipy.signal import savgol_filter, savgol_coeffs
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import explore_common as C
from src.analysis import describe as D
from src.features.kinematics import valid_runs

OUT = Path("outputs/dimensionality"); OUT.mkdir(parents=True, exist_ok=True)
KP13 = [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]   # 12 body keypoints (face dropped: faceless salsa renders)
HIP = (KP13.index(11), KP13.index(12)); SH = (KP13.index(5), KP13.index(6))
FPS = 15.0
WIN_S, MIN_VALID = 5.0, 0.6
CONF = 0.5
SGW = 7                                       # 0.47 s at 15 fps
C0 = float(savgol_coeffs(SGW, 3)[SGW // 2])   # weight of the centre sample: residual var of white noise = (1 - C0) sigma^2


def resample_idx(n, fps):
    t = np.arange(0, n / fps, 1 / FPS)
    return np.minimum(np.round(t * fps).astype(int), n - 1)


def pr_n90(cov):
    w = np.clip(np.linalg.eigvalsh(cov), 0, None)[::-1]
    if w.sum() <= 0:
        return np.nan, np.nan
    pr = w.sum() ** 2 / (w ** 2).sum()
    n90 = int(np.searchsorted(np.cumsum(w) / w.sum(), 0.9) + 1)
    return float(pr), n90


def window_dims(K: np.ndarray, valid: np.ndarray):
    """K: (T,13,2) keypoints in px (or any unit) at 15 fps, valid: (T,) frames passing the filter.
    Returns a list of dicts, one per 10-s window."""
    w = int(WIN_S * FPS); out = []
    hip = (K[:, HIP[0]] + K[:, HIP[1]]) / 2
    sh = (K[:, SH[0]] + K[:, SH[1]]) / 2
    trunk = np.linalg.norm(sh - hip, axis=1)
    X = (K - hip[:, None, :]).reshape(len(K), -1)
    X[~valid] = np.nan
    # smoothing on contiguous valid runs (>= SGW frames); residual -> jitter variance per coordinate
    S = np.full_like(X, np.nan)
    for s, e in valid_runs(np.isfinite(X).all(1)):
        if e - s >= SGW:
            S[s:e] = savgol_filter(X[s:e], SGW, 3, axis=0, mode="interp")
    # identity jumps: hip midpoint moving > 1 trunk length between consecutive frames
    jump = np.r_[False, np.linalg.norm(np.diff(hip, axis=0), axis=1) > np.nanmedian(trunk)]
    for st in range(0, len(X) - w + 1, w):
        sl = slice(st, st + w)
        ok = np.isfinite(S[sl]).all(1)
        if ok.mean() < MIN_VALID or jump[sl][ok].any():
            continue
        L = np.nanmedian(trunk[sl][ok])
        x, s_ = X[sl][ok] / L, S[sl][ok] / L
        cov = np.cov(x.T); covs = np.cov(s_.T)
        noise = np.var(x - s_, axis=0) / max(1 - C0, 1e-6)
        pr_raw, n90_raw = pr_n90(cov); pr_dn, n90_dn = pr_n90(cov - np.diag(noise)); pr_s, n90_s = pr_n90(covs)
        out.append(dict(start_s=st / FPS, valid=float(ok.mean()), pr_raw=pr_raw, n90_raw=n90_raw, pr_dn=pr_dn, n90_dn=n90_dn,
                        pr_smooth=pr_s, n90_smooth=n90_s, jitter_bl=float(np.sqrt(np.median(noise))), total_var=float(np.trace(covs))))
    return out


def video_dancer(K17: np.ndarray, present: np.ndarray, fps: float):
    idx = resample_idx(len(K17), fps)
    K = K17[idx][:, KP13]; pres = present[idx]
    valid = pres & (K[:, :, 2] >= CONF).all(1)
    return K[:, :, :2].astype(float), valid, idx


def ci_or_salsa(vid, genre):
    tr = C.tracks(vid); fps = float(tr.meta["fps"]); rows = []; pass_rows = []
    st = None
    if genre == "CI":
        from state_grammar import frame_states
        st = pd.Series(frame_states(vid)[0]).fillna("none").to_numpy()
    for j in (0, 1):
        K, valid, idx = video_dancer(tr.kpts[:, j], tr.present[:, j], fps)
        sts = st[idx] if st is not None else np.full(len(idx), "salsa", dtype=object)
        # selection bias: share of detected frames that pass the all-13-keypoints filter, per state
        det = tr.present[idx, j]
        for s in np.unique(sts):
            m = det & (sts == s)
            if m.sum() >= 30:
                pass_rows.append(dict(source=genre, video=vid, dancer="AB"[j], state=s, frames=int(m.sum()), pass_frac=float(valid[m].mean())))
        for r in window_dims(K, valid):
            a = int(r["start_s"] * FPS); seg = pd.Series(sts[a:a + int(WIN_S * FPS)])
            r.update(source=genre, video=vid, dancer=f"{vid}:{'AB'[j]}", state=seg.mode().iloc[0], state_share=float((seg == seg.mode().iloc[0]).mean()))
            rows.append(r)
    return rows, pass_rows


def bigand_trial(args):
    dyad, trial, jitters = args
    rows = []
    for side in ("LEFT", "RIGHT"):
        X = C.bigand_load(dyad, trial, side)
        if X is None:
            continue
        up = C.bigand_up_axis(X); view = [k for k in range(3) if k != up][1]
        K3 = C.bigand_coco(X)[resample_idx(len(X), 25.0)]
        trunk = np.nanmedian(np.linalg.norm((K3[:, 5] + K3[:, 6]) / 2 - (K3[:, 11] + K3[:, 12]) / 2, axis=1))
        ok3 = np.isfinite(K3).all((1, 2))
        # 3-D reference: same windows, 39-D
        w3 = window_dims_3d(K3[:, KP13], ok3)
        for jit in jitters:
            rng = np.random.default_rng(dyad * 1000 + trial * 10 + (side == "LEFT"))
            K2 = C.project_2d(K3, up, view, jit, rng, trunk)[:, KP13]
            ws = window_dims(K2[:, :, :2], ok3)
            for r, r3 in zip(ws, w3):
                r.update(source="Bigand", video=f"D{dyad:02d}T{trial:02d}", dancer=f"D{dyad:02d}{side[0]}", jitter_added_bl=jit,
                         pr_3d=r3["pr"], n90_3d=r3["n90"], state="free")
                rows.append(r)
    return rows


def window_dims_3d(K, valid):
    w = int(WIN_S * FPS); out = []
    hip = (K[:, HIP[0]] + K[:, HIP[1]]) / 2; trunk = np.linalg.norm((K[:, SH[0]] + K[:, SH[1]]) / 2 - hip, axis=1)
    X = (K - hip[:, None, :]).reshape(len(K), -1)
    for st in range(0, len(X) - w + 1, w):
        ok = valid[st:st + w]
        if ok.mean() < MIN_VALID:
            out.append(dict(pr=np.nan, n90=np.nan)); continue
        x = X[st:st + w][ok] / np.nanmedian(trunk[st:st + w][ok])
        pr, n90 = pr_n90(np.cov(x.T)); out.append(dict(pr=pr, n90=n90))
    return out


def main():
    ci, salsa = C.ci_videos(), C.salsa_videos()
    rows, passes = [], []
    with ProcessPoolExecutor(3) as ex:
        for r, p in ex.map(ci_or_salsa, ci + salsa, ["CI"] * len(ci) + ["salsa"] * len(salsa)):
            rows += r; passes += p
    W = pd.DataFrame(rows); P = pd.DataFrame(passes)
    ci_jit = float(W[W.source == "CI"].jitter_bl.median()); sa_jit = float(W[W.source == "salsa"].jitter_bl.median())
    print(f"[dims] CI windows {int((W.source == 'CI').sum())}, salsa {int((W.source == 'salsa').sum())}; jitter CI {ci_jit:.4f} salsa {sa_jit:.4f} bl")
    # Bigand at 3 noise levels: none, a clean video (0.005 bl) and the CI median jitter
    vis = pd.read_csv(C.BIG / "cond_vis.csv", index_col=0).to_numpy()
    dy = sorted(int(p.name.split("_")[1]) for p in C.BIG.glob("Dyad_*"))
    jitters = (0.0, 0.005, 0.01, 0.02, round(ci_jit, 4))
    jobs = [(d, t, jitters) for d in dy for t in range(1, 33, 4)]         # 8 of 32 trials per dyad
    with ProcessPoolExecutor(3) as ex:
        B = pd.DataFrame([r for rr in ex.map(bigand_trial, jobs) for r in rr])
    B.to_csv(OUT / "bigand_validation.csv", index=False)
    # salsa with jitter added to match CI: re-run windows on salsa keypoints + extra noise
    extra = np.sqrt(max(ci_jit ** 2 - sa_jit ** 2, 0))
    srows = []
    for vid in salsa:
        tr = C.tracks(vid); fps = float(tr.meta["fps"])
        for j in (0, 1):
            K, valid, _ = video_dancer(tr.kpts[:, j], tr.present[:, j], fps)
            L = np.nanmedian(D.trunk_len(tr.kpts[:, j].astype(float)))
            Kn = K + np.random.default_rng(j).normal(0, extra * L, K.shape)
            for r in window_dims(Kn, valid):
                r.update(source="salsa+jitter", video=vid, dancer=f"{vid}:{'AB'[j]}", state="salsa"); srows.append(r)
    # the added jitter whose MEASURED residual jitter is closest to the CI median (the residual also holds real fast motion)
    meas = B.groupby("jitter_added_bl").jitter_bl.median(); jm = float((meas - ci_jit).abs().idxmin())
    print(f"[dims] Bigand measured jitter by added level: {meas.round(4).to_dict()} -> matched {jm}")
    Bm = B[B.jitter_added_bl == jm].copy(); Bm["source"] = "Bigand 2-D+CI jitter"
    W = pd.concat([W, pd.DataFrame(srows), Bm], ignore_index=True)
    W.to_csv(OUT / "windows.csv", index=False); P.to_csv(OUT / "filter_pass.csv", index=False)
    report(W, B, P, jitters, ci_jit, sa_jit)


def report(W, B, P, jitters, ci_jit, sa_jit):
    md = ["# Idea B: effective dimensionality of each dancer's pose trajectory\n",
          f"12 body keypoints, hip-centred, / window median trunk length; {WIN_S:g}-s windows at 15 fps; conf >= {CONF} on all 12 keypoints. "
          "PR = participation ratio (1 = one dimension, 24 = isotropic 2-D noise). n90 = components for 90 % variance.\n",
          f"Median jitter per coordinate (from the smoothing residual): CI {ci_jit:.4f} bl, salsa renders {sa_jit:.4f} bl.\n",
          "## 1. Validation on Bigand et al. 2024 (35 dyads x 8 trials x 2 dancers)\n"]
    v = []
    for j, g in B.groupby("jitter_added_bl"):
        g = g.dropna(subset=["pr_3d"])
        per = g.groupby("dancer")[["pr_3d", "pr_raw", "pr_dn", "pr_smooth"]].median()
        v.append(dict(jitter_added_bl=j, windows=len(g), pr_3d=g.pr_3d.median(), pr_2d_raw=g.pr_raw.median(), pr_2d_denoised=g.pr_dn.median(),
                      pr_2d_smooth=g.pr_smooth.median(), n90_3d=g.n90_3d.median(), n90_2d_raw=g.n90_raw.median(), n90_2d_dn=g.n90_dn.median(),
                      spearman_window_3d_vs_2d_raw=stats.spearmanr(g.pr_3d, g.pr_raw)[0], spearman_window_3d_vs_2d_dn=stats.spearmanr(g.pr_3d, g.pr_dn)[0],
                      spearman_dancer_3d_vs_2d_raw=stats.spearmanr(per.pr_3d, per.pr_raw)[0], spearman_dancer_3d_vs_2d_dn=stats.spearmanr(per.pr_3d, per.pr_dn)[0]))
    md.append(pd.DataFrame(v).round(3).to_markdown(index=False))
    md.append("\n\n## 2. CI vs salsa vs Bigand, per dancer (median over the dancer's windows)\n")
    per = W.groupby(["source", "dancer"]).agg(windows=("pr_raw", "size"), pr_raw=("pr_raw", "median"), pr_dn=("pr_dn", "median"),
                                             pr_smooth=("pr_smooth", "median"), n90_raw=("n90_raw", "median"), n90_dn=("n90_dn", "median"),
                                             jitter_bl=("jitter_bl", "median"), total_var=("total_var", "median")).reset_index()
    per.to_csv(OUT / "per_dancer.csv", index=False)
    tab = per.groupby("source").agg(dancers=("dancer", "size"), windows=("windows", "sum"), pr_raw=("pr_raw", "median"), pr_dn=("pr_dn", "median"),
                                    pr_smooth=("pr_smooth", "median"), n90_raw=("n90_raw", "median"), n90_dn=("n90_dn", "median"),
                                    jitter_bl=("jitter_bl", "median"), total_var=("total_var", "median"))
    md.append(tab.round(3).to_markdown())
    tests = []
    for other in ("salsa", "salsa+jitter", "Bigand 2-D+CI jitter"):
        for m in ("pr_raw", "pr_dn", "pr_smooth"):
            a, b = per[per.source == "CI"][m].dropna(), per[per.source == other][m].dropna()
            if len(b) >= 3:
                tests.append(dict(contrast=f"CI vs {other}", measure=m, ci_median=a.median(), other_median=b.median(),
                                  mannwhitney_p=stats.mannwhitneyu(a, b).pvalue, n_ci=len(a), n_other=len(b)))
    md.append("\n\nMann-Whitney across dancers (dancers within a duet are not independent; treat p as descriptive):\n\n" + pd.DataFrame(tests).round(4).to_markdown(index=False))
    md.append("\n\n## 3. Within CI: by duet state (window majority state)\n")
    ci = W[W.source == "CI"]
    md.append(ci.groupby("state").agg(windows=("pr_raw", "size"), pr_raw=("pr_raw", "median"), pr_dn=("pr_dn", "median"), jitter_bl=("jitter_bl", "median"),
                                      total_var=("total_var", "median")).round(3).to_markdown())
    md.append("\n\nPer CI duet:\n\n" + ci.groupby("video").agg(windows=("pr_raw", "size"), pr_raw=("pr_raw", "median"), pr_dn=("pr_dn", "median"),
                                                               jitter_bl=("jitter_bl", "median")).round(3).to_markdown())
    md.append("\n\n## 4. Selection bias: share of detected frames with all 12 keypoints at conf >= %.1f\n" % CONF)
    md.append(P.groupby(["source", "state"]).apply(lambda g: pd.Series(dict(frames=g.frames.sum(), pass_frac=np.average(g.pass_frac, weights=g.frames)))).round(3).to_markdown())
    md.append("\n\nCorrelation across windows of jitter with PR (CI): raw r = %.2f, denoised r = %.2f (Spearman)" %
              (stats.spearmanr(ci.jitter_bl, ci.pr_raw)[0], stats.spearmanr(ci.jitter_bl, ci.pr_dn)[0]))
    (OUT / "report.md").write_text("\n".join(md)); print("\n".join(md))

    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    srcs = ["CI", "salsa", "salsa+jitter", "Bigand 2-D+CI jitter"]
    for i, m in enumerate(("pr_raw", "pr_dn")):
        ax[i].boxplot([per[per.source == s][m].dropna() for s in srcs], labels=["CI", "salsa", "salsa\n+jitter", "Bigand 2-D\n+jitter"])
        ax[i].set_title({"pr_raw": "participation ratio (raw)", "pr_dn": "PR after subtracting jitter variance"}[m]); ax[i].set_ylabel("PR per dancer")
    fig.tight_layout(); fig.savefig(OUT / "pr_by_source.png", dpi=130)


def check_sheet(n=5):
    """CI windows with the highest and the lowest denoised PR: 4 frames per window with the dancer's skeleton, to judge by
    eye whether high PR is varied movement or tracking trouble."""
    import glob
    import cv2
    from describe_duets import draw
    W = pd.read_csv(OUT / "windows.csv"); ci = W[W.source == "CI"].sort_values("pr_dn")
    rows = []
    for label, sub in (("LOW", ci.head(n)), ("HIGH", ci.tail(n)[::-1])):
        for r in sub.itertuples():
            vid, d = r.dancer.split(":"); j = "AB".index(d)
            tr = C.tracks(vid); fps = float(tr.meta["fps"])
            vp = (sorted(glob.glob(f"videos/full/{vid}.*")) + sorted(glob.glob(f"videos/{vid}.*")) or [None])[0]
            tiles = []
            for q in (0.1, 0.35, 0.6, 0.85):
                fi = int((r.start_s + q * WIN_S) * fps)
                cap = cv2.VideoCapture(vp); cap.set(1, fi); ok, f = cap.read(); cap.release()
                if not ok:
                    f = np.zeros((360, 480, 3), np.uint8)
                if tr.present[fi, j]:
                    draw(f, tr.kpts[fi, j], (0, 255, 0))
                f = cv2.resize(f, (300, int(300 * f.shape[0] / f.shape[1]))); tiles.append(f)
            h = max(t.shape[0] for t in tiles); tiles = [cv2.copyMakeBorder(t, 0, h - t.shape[0], 0, 0, cv2.BORDER_CONSTANT) for t in tiles]
            row = np.hstack(tiles)
            cv2.putText(row, f"{label} PRdn={r.pr_dn:.2f} raw={r.pr_raw:.2f} {vid[:8]} {d} t={r.start_s:.0f}s {r.state}", (5, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 2)
            rows.append(row)
    W_ = max(x.shape[1] for x in rows)
    rows = [cv2.copyMakeBorder(x, 0, 0, 0, W_ - x.shape[1], cv2.BORDER_CONSTANT) for x in rows]
    cv2.imwrite(str(OUT / "check_pr_extremes.jpg"), np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 70])


if __name__ == "__main__":
    import sys
    check_sheet() if "--check" in sys.argv else main()
