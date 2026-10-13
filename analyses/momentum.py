"""
Idea A (13 Oct exploration): momentum ride / energy hand-off. CI dancers are said to redirect existing momentum
instead of starting and stopping with muscle. Mass and depth are unknown, so only scale-free measures:

  hand-off     correlation between d/dt(v_A^2) and d/dt(v_B^2) (pelvis, camera-compensated, body lengths/s, rank ->
               normal scores so identity-swap spikes cannot dominate). Negative = one speeds up while the other slows.
               (i) lag-0 r over all frames of a state, (ii) most negative r within +-1 s, (iii) share of 2-s windows
               with r < -0.5 ("hand-off windows") and > +0.5 ("co-moving windows").
  continuity   per dancer and state: fraction of time near-stopped (pelvis speed < 0.25 bl/s), median SPARC of 4-s
               speed windows (aggregated per clip only: per-window SPARC is unreliable, AUDIT 17).

Controls
  circular     B shifted >= 5 s on the full timeline, state mask kept (as coupling_controls.shift_null)
  camera/scale normal-score d(v^2)/dt regressed on camera translation speed, its change, zoom rate and the shared
               log trunk-length change rate before correlating (AUDIT 27-31)
  pseudo-pairs dancer A of one duet vs dancer B of another duet (all frames)
  noise match  contact frames have worse tracking: apart frames get extra keypoint jitter until their smoothing
               residual matches the contact frames, then continuity is recomputed
Ground truth
  Bigand et al. 2024: 35 dyads x 32 one-minute trials of free dance without touch -> hand-off should be ~0
               (esp. curtain + different music, no channel at all); also 2-D virtual camera + jitter
  CoMPAS3D salsa: pelvis translation of 71 sequences (3-D and 2-D+jitter); the 3 rendered sequences also through the
               video pipeline, compared with their own mocap over the same 60 s

Outputs: outputs/momentum/{ci_handoff.csv, ci_continuity.csv, pseudo_pairs.csv, bigand.csv, compas.csv,
         compas_video_vs_mocap.csv, report.md, handoff.png}
"""
from __future__ import annotations

import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import numpy as np
import pandas as pd
from numpy.lib.stride_tricks import sliding_window_view
from scipy import stats
from scipy.signal import savgol_filter
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import explore_common as C
from src.analysis.coupling_controls import lagged_corr, partial_out
from src.features.smoothness import sparc

OUT = Path("outputs/momentum"); OUT.mkdir(parents=True, exist_ok=True)
STOP_BL_S = 0.25
WIN_S, STEP_S, THR = 2.0, 0.5, 0.5
N_NULL = 200


# ----------------------------------------------------------------------------------------------- statistics
def windows_r(a, b, fps):
    """Pearson r in every 2-s window (step 0.5 s) where both series are fully finite."""
    w, st = int(WIN_S * fps), max(int(STEP_S * fps), 1)
    if len(a) < w:
        return np.array([])
    A = sliding_window_view(a, w)[::st]; B = sliding_window_view(b, w)[::st]
    ok = np.isfinite(A).all(1) & np.isfinite(B).all(1)
    A, B = A[ok], B[ok]
    if not len(A):
        return np.array([])
    A = A - A.mean(1, keepdims=True); B = B - B.mean(1, keepdims=True)
    den = np.sqrt((A ** 2).sum(1) * (B ** 2).sum(1))
    r = np.where(den > 1e-12, (A * B).sum(1) / np.maximum(den, 1e-12), np.nan)
    return r[np.isfinite(r)]


def r0(a, b):
    m = np.isfinite(a) & np.isfinite(b)
    if m.sum() < 30:
        return np.nan
    return float(np.corrcoef(a[m], b[m])[0, 1])


def stats_once(a, b, fps):
    L = int(fps); c = lagged_corr(a, b, L, min_pairs=30)
    wr = windows_r(a, b, fps)
    return dict(r0=r0(a, b), rmin=float(np.nanmin(c)) if np.isfinite(c).any() else np.nan,
                frac_neg=float((wr < -THR).mean()) if len(wr) else np.nan,
                frac_pos=float((wr > THR).mean()) if len(wr) else np.nan, n_win=len(wr))


def handoff_test(a, b, mask, fps, n=N_NULL, seed=0, prefix=""):
    """Observed statistics on the masked frames and a circular-shift null (B rolled >= 5 s, mask fixed)."""
    rng = np.random.default_rng(seed); T = len(a)
    aa = np.where(mask, a, np.nan); obs = stats_once(aa, np.where(mask, b, np.nan), fps)
    obs["n_frames"] = int((np.isfinite(aa) & np.isfinite(np.where(mask, b, np.nan))).sum())
    lo = int(5 * fps); hi = T - lo
    out = {f"{prefix}{k}": v for k, v in obs.items()}
    if hi <= lo or obs["n_frames"] < 60:
        return out
    nulls = []
    for _ in range(n):
        k = int(rng.integers(lo, hi + 1))
        nulls.append(stats_once(aa, np.where(mask, np.roll(b, k), np.nan), fps))
    N = pd.DataFrame(nulls)
    for k, side in (("r0", "two"), ("rmin", "less"), ("frac_neg", "greater"), ("frac_pos", "greater")):
        x = N[k].dropna().to_numpy(); o = obs[k]
        if len(x) < 20 or not np.isfinite(o):
            continue
        if side == "two":
            p = (np.sum(np.abs(x - x.mean()) >= abs(o - x.mean())) + 1) / (len(x) + 1)
        elif side == "less":
            p = (np.sum(x <= o) + 1) / (len(x) + 1)
        else:
            p = (np.sum(x >= o) + 1) / (len(x) + 1)
        out[f"{prefix}{k}_null_mean"] = float(x.mean()); out[f"{prefix}{k}_p"] = float(p)
    return out


def sparc_windows(speed, mask, fps, win_s=4.0):
    w = int(win_s * fps); vals = []
    s = np.where(mask, speed, np.nan)
    for st in range(0, len(s) - w, w // 2):
        seg = s[st:st + w]
        if np.isfinite(seg).all():
            vals.append(sparc(seg, fps, fc=min(6.0, fps / 2 - 0.5)))
    vals = [v for v in vals if np.isfinite(v)]
    return float(np.median(vals)) if vals else np.nan, len(vals)


def sg_resid_factor(win):
    x = np.random.default_rng(1).normal(0, 1, (20000, 2))
    r = np.linalg.norm(x - savgol_filter(x, win, 3, axis=0), axis=1)
    return float(np.median(r))          # median residual magnitude per unit per-axis sigma


def continuity(speed, jit, mask):
    s = speed[mask & np.isfinite(speed)]
    return dict(stop_frac=float((s < STOP_BL_S).mean()) if len(s) > 30 else np.nan, speed_med=float(np.median(s)) if len(s) > 30 else np.nan,
                jitter_bl=float(np.nanmedian(jit[mask])) if (mask & np.isfinite(jit)).sum() > 30 else np.nan, n=int(len(s)))


# ----------------------------------------------------------------------------------------------- CI duets
def ci_clip(vid):
    from state_grammar import frame_states
    tr = C.tracks(vid); fps = float(tr.meta["fps"])
    st, _ = frame_states(vid)
    st = pd.Series(st).fillna("none").to_numpy()
    masks = {"contact": np.isin(st, ["contact", "share"]), "apart": np.isin(st, ["apart", "near"]), "all": st != "none"}
    kA, kB = C.pelvis_kin(tr, 0, fps), C.pelvis_kin(tr, 1, fps)
    eA, eB = C.normal_scores(kA["dke"]), C.normal_scores(kB["dke"])
    cov = C.camera_covariates(tr, (kA["L"] + kB["L"]) / 2, fps)
    pA, pB = partial_out(eA, cov), partial_out(eB, cov)
    row = dict(video=vid, fps=fps, contact_share=float(masks["contact"].mean() / max(masks["all"].mean(), 1e-9)))
    for name, m in masks.items():
        row.update(handoff_test(eA, eB, m, fps, prefix=f"{name}_", seed=1))
        if name != "all":
            row.update(handoff_test(pA, pB, m, fps, prefix=f"{name}_campart_", seed=2))
    # uncompensated (no camera compensation at all) for comparison: how much does the camera matter?
    uA, uB = C.pelvis_kin(tr, 0, fps, compensate=False), C.pelvis_kin(tr, 1, fps, compensate=False)
    row["contact_nocomp_r0"] = r0(np.where(masks["contact"], C.normal_scores(uA["dke"]), np.nan), np.where(masks["contact"], C.normal_scores(uB["dke"]), np.nan))
    row["apart_nocomp_r0"] = r0(np.where(masks["apart"], C.normal_scores(uA["dke"]), np.nan), np.where(masks["apart"], C.normal_scores(uB["dke"]), np.nan))

    # continuity, with a noise-matched version of the apart frames
    crow = []
    fac = sg_resid_factor(C.sg_window(fps))
    for j, kin in ((0, kA), (1, kB)):
        r = dict(video=vid, dancer="AB"[j])
        for name in ("contact", "apart"):
            c = continuity(kin["speed"], kin["jitter_bl"], masks[name]); sp, nw = sparc_windows(kin["speed"], masks[name], fps)
            r.update({f"{name}_{k}": v for k, v in c.items()}); r[f"{name}_sparc"] = sp; r[f"{name}_sparc_nwin"] = nw
        jc, ja = r["contact_jitter_bl"], r["apart_jitter_bl"]
        if np.isfinite(jc) and np.isfinite(ja) and jc > ja:
            add_bl = np.sqrt(jc ** 2 - ja ** 2) / fac
            for _ in range(4):        # residuals are not exactly additive (real fast motion): calibrate the added noise
                noise = np.where(masks["apart"], add_bl * kin["L"], 0.0)
                kn = C.pelvis_kin(tr, j, fps, extra_noise_px=noise, rng=np.random.default_rng(7 + j))
                c = continuity(kn["speed"], kn["jitter_bl"], masks["apart"])
                got = c["jitter_bl"]
                if not np.isfinite(got) or abs(got - jc) / jc < 0.05 or got <= ja:
                    break
                add_bl *= np.sqrt((jc ** 2 - ja ** 2) / max(got ** 2 - ja ** 2, 1e-12))
            sp, _ = sparc_windows(kn["speed"], masks["apart"], fps)
            r.update({f"apart_nm_{k}": v for k, v in c.items()}); r["apart_nm_sparc"] = sp
        else:
            for k in ("stop_frac", "speed_med", "jitter_bl", "sparc"):
                r[f"apart_nm_{k}"] = r[f"apart_{k}"]
        crow.append(r)
    series = (C.normal_scores(kA["dke"]), C.normal_scores(kB["dke"]), fps)
    return row, crow, series


def pseudo_pairs(series):
    rows = []
    vids = list(series)
    for i in vids:
        ai, bi, fi = series[i]
        true = r0(ai, bi); null = []
        for j in vids:
            if j == i:
                continue
            aj, bj, fj = series[j]
            for x, fx, y, fy in ((ai, fi, bj, fj), (aj, fj, bi, fi)):
                if fx != fy:                      # resample the 30-fps clip to 15 fps
                    x = x[::2] if fx > fy else x; y = y[::2] if fy > fx else y
                L = min(len(x), len(y)); null.append(r0(x[:L], y[:L]))
        null = np.array([v for v in null if np.isfinite(v)])
        rows.append(dict(video=i, true_r0_all=true, pseudo_mean=float(null.mean()), pseudo_sd=float(null.std()),
                         pseudo_lo=float(np.percentile(null, 2.5)), pseudo_hi=float(np.percentile(null, 97.5)), n_pseudo=len(null)))
    return pd.DataFrame(rows)


# ----------------------------------------------------------------------------------------------- ground truth
def kin3(P, fps):
    """P: (T,d) positions in bl -> speed, normal-score d(v^2)/dt."""
    w = C.sg_window(fps)
    v = C.sg_runs(P, fps, w, 1); a = C.sg_runs(P, fps, w, 2)
    speed = np.linalg.norm(v, axis=1); dke = 2 * np.einsum("ij,ij->i", v, a)
    return speed, C.normal_scores(dke)


def bigand_trial(args):
    dyad, trial, vis, mus = args
    L, R = C.bigand_load(dyad, trial, "LEFT"), C.bigand_load(dyad, trial, "RIGHT")
    if L is None or R is None:
        return []
    n = min(len(L), len(R)); L, R = L[:n], R[:n]
    up = C.bigand_up_axis(L); fps = 25.0; rng = np.random.default_rng(dyad * 100 + trial)
    view = [k for k in range(3) if k != up][1]
    out = []
    trunk = np.nanmedian(np.linalg.norm(L[:, C._bi("Sternum")] - L[:, C._bi("Pelvis")], axis=1))
    for jit in (0.0, 0.02):
        sig = []
        for X in (L, R):
            if jit == 0:
                P = X[:, C._bi("Pelvis")] / trunk
            else:   # 2-D virtual camera, hips with keypoint jitter, as the video pipeline sees the pelvis
                K = C.project_2d(C.bigand_coco(X), up, view, jit, rng, trunk)
                P = (K[:, 11, :2] + K[:, 12, :2]) / 2 / 100.0
            sig.append(kin3(P, fps))
        (sL, eL), (sR, eR) = sig
        row = dict(dyad=dyad, trial=trial, vision=vis, same_music=mus, jitter_bl=jit)
        row.update(handoff_test(eL, eR, np.ones(n, bool), fps, n=100, seed=trial))
        for lab, s in (("L", sL), ("R", sR)):
            row[f"stop_frac_{lab}"] = float(np.nanmean(s[np.isfinite(s)] < STOP_BL_S))
            row[f"sparc_{lab}"] = sparc_windows(s, np.ones(n, bool), fps)[0]
        out.append(row)
    return out


def compas_seq(lp):
    fp = Path(str(lp).replace("_leader.npz", "_follower.npz"))
    zl, zf = np.load(lp), np.load(fp); fps = float(zl["fps"])
    tl, tf = zl["trans"].astype(float), zf["trans"].astype(float); n = min(len(tl), len(tf)); tl, tf = tl[:n], tf[:n]
    up = int(np.argmin(np.std(tl, axis=0) / (np.abs(np.mean(tl, axis=0)) + 1e-6)))
    rng = np.random.default_rng(len(str(lp))); rows = []
    for jit in (0.0, 0.02):
        sig = []
        for t in (tl, tf):
            P = t / 0.5                                                  # 1 bl ~ 0.5 m
            if jit:
                horiz = [k for k in range(3) if k != up][0]
                P = P[:, [horiz, up]] + rng.normal(0, jit / np.sqrt(2), (n, 2))
            sig.append(kin3(P, fps))
        row = dict(sequence=lp.parent.name, pair=lp.parent.parent.name, jitter_bl=jit)
        row.update(handoff_test(sig[0][1], sig[1][1], np.ones(n, bool), fps, n=100, seed=3))
        rows.append(row)
    return rows


def compas_video_vs_mocap():
    """The 3 rendered salsa sequences: hand-off statistics from the video pipeline vs from the mocap of the same 60 s."""
    rows = []
    for vid in C.salsa_videos():
        seq = vid.replace("salsa_", ""); pair = seq.split("_")[0]
        lp = Path(f"data_external/compas3d/trans/{pair}/{seq}/{seq}_leader.npz")
        if not lp.exists():
            continue
        tr = C.tracks(vid); fps = float(tr.meta["fps"]); n = tr.kpts.shape[0]
        kA, kB = C.pelvis_kin(tr, 0, fps), C.pelvis_kin(tr, 1, fps)
        zl, zf = np.load(lp), np.load(str(lp).replace("_leader", "_follower"))
        sl, el = kin3(zl["trans"][:n].astype(float) / 0.5, fps); sf, ef = kin3(zf["trans"][:n].astype(float) / 0.5, fps)
        # alignment / identity check: correlation of video speed with mocap speed (best of the two assignments)
        def rr(x, y):
            return r0(x, y)
        assign = max([(rr(kA["speed"], sl) + rr(kB["speed"], sf), "A=leader"), (rr(kA["speed"], sf) + rr(kB["speed"], sl), "A=follower")])
        lagc = lagged_corr(kA["speed"], sl if assign[1] == "A=leader" else sf, int(fps))
        eA, eB = C.normal_scores(kA["dke"]), C.normal_scores(kB["dke"])
        vstat = handoff_test(eA, eB, np.ones(n, bool), fps, n=100, prefix="video_")
        mstat = handoff_test(el, ef, np.ones(n, bool), fps, n=100, prefix="mocap_")
        rows.append(dict(video=vid, assignment=assign[1], speed_r_video_mocap=assign[0] / 2,
                         speed_peak_lag_s=float((np.nanargmax(lagc) - int(fps)) / fps),
                         both_present=float(tr.present.all(1).mean()), **vstat, **mstat))
    return pd.DataFrame(rows)


# ----------------------------------------------------------------------------------------------- main
def main(skip_external=False):
    vids = C.ci_videos()
    with ProcessPoolExecutor(3) as ex:
        res = list(ex.map(ci_clip, vids))
    H = pd.DataFrame([r[0] for r in res]); H.to_csv(OUT / "ci_handoff.csv", index=False)
    K = pd.DataFrame([x for r in res for x in r[1]]); K.to_csv(OUT / "ci_continuity.csv", index=False)
    PP = pseudo_pairs({v: r[2] for v, r in zip(vids, res)}); PP.to_csv(OUT / "pseudo_pairs.csv", index=False)
    print(H[["video", "contact_r0", "contact_r0_p", "apart_r0", "apart_r0_p", "contact_campart_r0", "contact_frac_neg", "contact_frac_neg_null_mean", "contact_frac_neg_p"]].round(3).to_string())
    if skip_external and (OUT / "bigand.csv").exists():
        B = pd.read_csv(OUT / "bigand.csv"); CP = pd.read_csv(OUT / "compas.csv"); CV = pd.read_csv(OUT / "compas_video_vs_mocap.csv")
    else:
        vis = pd.read_csv(C.BIG / "cond_vis.csv", index_col=0).to_numpy(); mus = pd.read_csv(C.BIG / "cond_mus.csv", index_col=0).to_numpy()
        dy = sorted(int(p.name.split("_")[1]) for p in C.BIG.glob("Dyad_*"))
        jobs = [(d, t, int(vis[d - 1, t - 1]), int(mus[d - 1, t - 1])) for d in dy for t in range(1, 33)]
        with ProcessPoolExecutor(3) as ex:
            B = pd.DataFrame([r for rr in ex.map(bigand_trial, jobs, chunksize=8) for r in rr])
        B.to_csv(OUT / "bigand.csv", index=False)
        seqs = sorted(Path("data_external/compas3d/trans").glob("Pair*/*/*_leader.npz"))
        with ProcessPoolExecutor(3) as ex:
            CP = pd.DataFrame([r for rr in ex.map(compas_seq, seqs) for r in rr])
        CP.to_csv(OUT / "compas.csv", index=False)
        CV = compas_video_vs_mocap(); CV.to_csv(OUT / "compas_video_vs_mocap.csv", index=False)
    report(H, K, PP, B, CP, CV)


def wil(x):
    x = pd.Series(x).dropna()
    if len(x) < 5:
        return np.nan
    return float(stats.wilcoxon(x).pvalue)


def report(H, K, PP, B, CP, CV):
    md = ["# Idea A: momentum ride / energy hand-off\n",
          "Signal: pelvis d(v^2)/dt per dancer (camera-compensated, body lengths from a rolling 5 s trunk length, rank -> normal scores). "
          "`r0` = lag-0 correlation between the two dancers; `rmin` = most negative r within ±1 s; `frac_neg` / `frac_pos` = share of 2-s windows with r < -0.5 / > +0.5. "
          "Nulls: B circularly shifted ≥ 5 s with the state mask fixed (`_null_mean`, `_p`). `campart` = after regressing out camera speed, zoom and shared scale change.\n",
          "## CI duets (10 clips)\n"]
    cols = ["video", "contact_share", "contact_n_frames", "contact_r0", "contact_r0_null_mean", "contact_r0_p", "contact_campart_r0", "contact_campart_r0_p",
            "contact_nocomp_r0", "apart_n_frames", "apart_r0", "apart_r0_p", "apart_campart_r0", "apart_campart_r0_p", "apart_nocomp_r0"]
    md.append(H[cols].round(3).to_markdown(index=False))
    cols2 = ["video", "contact_rmin", "contact_rmin_null_mean", "contact_rmin_p", "contact_frac_neg", "contact_frac_neg_null_mean", "contact_frac_neg_p",
             "contact_frac_pos", "contact_frac_pos_null_mean", "contact_frac_pos_p", "apart_frac_neg", "apart_frac_neg_null_mean", "apart_frac_neg_p",
             "contact_campart_frac_neg", "contact_campart_frac_neg_p"]
    md.append("\n\nWindows (2 s): hand-off (r < -0.5) and co-moving (r > 0.5) shares vs the circular null\n\n" + H[cols2].round(3).to_markdown(index=False))
    s = dict(contact_r0_med=H.contact_r0.median(), contact_r0_pos=int((H.contact_r0 > 0).sum()), apart_r0_med=H.apart_r0.median(),
             contact_vs_apart_p=wil(H.contact_r0 - H.apart_r0), contact_campart_med=H.contact_campart_r0.median(),
             n_contact_r0_sig=int((H.contact_r0_p < 0.05).sum()), n_contact_campart_sig=int((H.contact_campart_r0_p < 0.05).sum()),
             n_apart_r0_sig=int((H.apart_r0_p < 0.05).sum()),
             n_fracneg_sig=int((H.contact_frac_neg_p < 0.05).sum()), n_fracneg_campart_sig=int((H.contact_campart_frac_neg_p < 0.05).sum()),
             n_fracpos_sig=int((H.contact_frac_pos_p < 0.05).sum()),
             fracneg_excess_med=float((H.contact_frac_neg - H.contact_frac_neg_null_mean).median()),
             fracneg_excess_p=wil(H.contact_frac_neg - H.contact_frac_neg_null_mean))
    md.append("\n\nSummary across the 10 duets: " + ", ".join(f"{k} = {v:.3g}" if isinstance(v, float) else f"{k} = {v}" for k, v in s.items()))
    md.append("\n\n## Pseudo-pairs (dancer A of one duet vs dancer B of another, all frames)\n\n" + PP.round(3).to_markdown(index=False))
    md.append("\n\n## Continuity: near-stopped fraction (pelvis < %.2f bl/s) and SPARC, contact vs apart, per dancer\n" % STOP_BL_S)
    kc = ["video", "dancer", "contact_n", "apart_n", "contact_jitter_bl", "apart_jitter_bl", "apart_nm_jitter_bl", "contact_stop_frac", "apart_stop_frac",
          "apart_nm_stop_frac", "contact_speed_med", "apart_speed_med", "contact_sparc", "apart_sparc", "apart_nm_sparc"]
    md.append(K[kc].round(3).to_markdown(index=False))
    Kd = K.groupby("video")[[c for c in kc if c not in ("video", "dancer")]].mean()
    cs = dict(stop_contact_minus_apart_med=float((Kd.contact_stop_frac - Kd.apart_stop_frac).median()), p=wil(Kd.contact_stop_frac - Kd.apart_stop_frac),
              stop_contact_minus_apart_nm_med=float((Kd.contact_stop_frac - Kd.apart_nm_stop_frac).median()), p_nm=wil(Kd.contact_stop_frac - Kd.apart_nm_stop_frac),
              sparc_contact_minus_apart_med=float((Kd.contact_sparc - Kd.apart_sparc).median()), p_sparc=wil(Kd.contact_sparc - Kd.apart_sparc),
              sparc_contact_minus_apart_nm_med=float((Kd.contact_sparc - Kd.apart_nm_sparc).median()), p_sparc_nm=wil(Kd.contact_sparc - Kd.apart_nm_sparc),
              jitter_ratio_contact_apart_med=float((Kd.contact_jitter_bl / Kd.apart_jitter_bl).median()))
    md.append("\n\nPer duet (mean of the two dancers), Wilcoxon across 10 duets: " + ", ".join(f"{k} = {v:.3g}" for k, v in cs.items()))

    md.append("\n\n## Ground truth 1: Bigand et al. 2024 (free dance, never touching)\n")
    g = B.groupby(["jitter_bl", "vision", "same_music"]).agg(trials=("r0", "size"), r0_mean=("r0", "mean"), r0_null_mean=("r0_null_mean", "mean"),
                                                              r0_sig=("r0_p", lambda p: (p < 0.05).mean()), frac_neg=("frac_neg", "mean"),
                                                              frac_neg_null=("frac_neg_null_mean", "mean"), frac_neg_sig=("frac_neg_p", lambda p: (p < 0.05).mean()),
                                                              frac_pos=("frac_pos", "mean"), frac_pos_null=("frac_pos_null_mean", "mean"),
                                                              stop_frac=("stop_frac_L", "mean"), sparc=("sparc_L", "mean"))
    md.append(g.round(3).to_markdown())
    md.append("\n\n`r0_sig` / `frac_neg_sig` = share of trials with circular-null p < 0.05 (two-sided for r0, one-sided for frac_neg); "
              "with no channel (curtain + different music) these are false-positive rates, nominal 0.05.")
    md.append("\n\n## Ground truth 2: CoMPAS3D salsa pelvis translation (hand-hold partner dance)\n")
    g2 = CP.groupby("jitter_bl").agg(seqs=("r0", "size"), r0_mean=("r0", "mean"), r0_median=("r0", "median"), r0_null_mean=("r0_null_mean", "mean"),
                                     r0_sig=("r0_p", lambda p: (p < 0.05).mean()), frac_neg=("frac_neg", "mean"), frac_neg_null=("frac_neg_null_mean", "mean"),
                                     frac_neg_sig=("frac_neg_p", lambda p: (p < 0.05).mean()), frac_pos=("frac_pos", "mean"), frac_pos_null=("frac_pos_null_mean", "mean"))
    md.append(g2.round(3).to_markdown())
    md.append("\n\n### Same salsa performances through the video pipeline vs their own mocap (first 60 s)\n\n" + CV.round(3).to_markdown(index=False))
    (OUT / "report.md").write_text("\n".join(md)); print("\n".join(md[-12:]))

    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    x = np.arange(len(H))
    ax[0].bar(x - 0.2, H.contact_r0, 0.4, label="contact"); ax[0].bar(x + 0.2, H.apart_r0, 0.4, label="apart")
    ax[0].scatter(x - 0.2, H.contact_r0_null_mean, c="k", s=10, zorder=3, label="circular-null mean")
    ax[0].set_xticks(x); ax[0].set_xticklabels([v[:6] for v in H.video], rotation=60, fontsize=7); ax[0].axhline(0, c="k", lw=0.6)
    ax[0].set_ylabel("lag-0 r of d(v²)/dt"); ax[0].legend(fontsize=7); ax[0].set_title("CI duets (negative = hand-off)")
    data = [H.contact_r0.dropna(), B[(B.jitter_bl == 0) & (B.vision == 0) & (B.same_music == 0)].r0.dropna(),
            B[(B.jitter_bl == 0) & (B.vision == 1)].r0.dropna(), CP[CP.jitter_bl == 0].r0.dropna()]
    ax[1].boxplot(data, labels=["CI contact", "Bigand\nno channel", "Bigand\nvision", "salsa 3-D"]); ax[1].axhline(0, c="k", lw=0.6)
    ax[1].set_ylabel("lag-0 r of d(v²)/dt"); ax[1].set_title("Against ground truth")
    fig.tight_layout(); fig.savefig(OUT / "handoff.png", dpi=130)




# ----------------------------------------------------------------------------------------------- visual check
def check_sheet(n=8):
    """The most negative 2-s contact windows ("hand-offs") across duets: frames at start / middle / end with the pelvis
    speeds of both dancers, to judge by eye whether one dancer really slows while the other speeds up."""
    import glob
    import cv2
    from state_grammar import frame_states
    from describe_duets import draw
    cand = []; fps_of = {}
    for vid in C.ci_videos():
        tr = C.tracks(vid); fps = float(tr.meta["fps"]); fps_of[vid] = fps
        st = pd.Series(frame_states(vid)[0]).fillna("none").to_numpy(); m = np.isin(st, ["contact", "share"])
        kA, kB = C.pelvis_kin(tr, 0, fps), C.pelvis_kin(tr, 1, fps)
        a, b = np.where(m, C.normal_scores(kA["dke"]), np.nan), np.where(m, C.normal_scores(kB["dke"]), np.nan)
        w, s = int(WIN_S * fps), max(int(STEP_S * fps), 1)
        for i in range(0, len(a) - w, s):
            x, y = a[i:i + w], b[i:i + w]
            if np.isfinite(x).all() and np.isfinite(y).all():
                r = np.corrcoef(x, y)[0, 1]
                cand.append((r, vid, i, w, kA["speed"][i:i + w], kB["speed"][i:i + w]))
    cand.sort(key=lambda c: c[0])
    rows = []
    for r, vid, i, w, sa, sb in cand[:n]:
        vp = (sorted(glob.glob(f"videos/full/{vid}.*")) + sorted(glob.glob(f"videos/{vid}.*")) or [None])[0]
        tr = C.tracks(vid); tiles = []
        for fi in (i, i + w // 2, i + w - 1):
            cap = cv2.VideoCapture(vp); cap.set(1, int(fi)); ok, f = cap.read(); cap.release()
            if not ok:
                f = np.zeros((360, 480, 3), np.uint8)
            for j, col in ((0, (255, 160, 0)), (1, (0, 140, 255))):
                if tr.present[fi, j]:
                    draw(f, tr.kpts[fi, j], col)
            f = cv2.resize(f, (360, int(360 * f.shape[0] / f.shape[1])))
            k = fi - i
            cv2.putText(f, f"A {sa[k]:.2f} B {sb[k]:.2f} bl/s", (5, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            tiles.append(f)
        h = max(t.shape[0] for t in tiles); tiles = [cv2.copyMakeBorder(t, 0, h - t.shape[0], 0, 0, cv2.BORDER_CONSTANT) for t in tiles]
        row = np.hstack(tiles)
        cv2.putText(row, f"{vid[:8]} t={i / tr.meta['fps']:.1f}s r={r:.2f} (A blue-ish, B orange)", (5, h - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
        rows.append(row)
    W_ = max(r.shape[1] for r in rows)
    rows = [cv2.copyMakeBorder(r, 0, 0, 0, W_ - r.shape[1], cv2.BORDER_CONSTANT) for r in rows]
    cv2.imwrite(str(OUT / "check_handoff_windows.jpg"), np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 75])
    pd.DataFrame([dict(video=v, start_s=i / fps_of[v], r=r, A_speed_start=sa[0], A_speed_end=sa[-1], B_speed_start=sb[0], B_speed_end=sb[-1])
                  for r, v, i, w, sa, sb in cand[:n]]).to_csv(OUT / "check_handoff_windows.csv", index=False)
    print(f"[momentum] {len(cand)} contact windows; most negative r: {[round(c[0], 2) for c in cand[:n]]}")


if __name__ == "__main__":
    if "--check" in sys.argv:
        check_sheet()
    else:
        main(skip_external="--skip-external" in sys.argv)
