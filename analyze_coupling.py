"""
Coupling analysis with controls (the primary thesis result). Reads outputs/dataset/ and the human
content registry videos/curation.csv; writes outputs/coupling/coupling_report.md, per-clip and
per-source tables, and a figure.

Unit of inference = source group (one recording session / event), not clip: several clips can
come from the same performance and would otherwise be counted as independent replications.

Sets (from the visual pair audit in videos/curation.csv, column pair_ok):
  primary     the tracked pair is verified to be the dancing pair (pair_ok == yes)
  secondary   also clips with frequent A/B swaps but the right two people (pair_ok == partial)
  failed      clips where the tracked "pair" is wrong (spectators, a shadow, a montage): a negative
              demonstration of what the statistic does on garbage input
  all         every included CI clip, audited or not (what an unaudited pipeline would report)
"""
from __future__ import annotations

import json
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.analysis.coupling_controls import peak, shift_null, bandpass_runs, partial_out, resample
from src.analysis.audio import load_mono, frame_envelopes
from src.io.tracks import load_tracks
from src.features.scale import trunk_length_per_frame

OUT = Path("outputs/coupling")
N_SURR = 500
MIN_FRAMES_STATE = 300          # ~10-12 s of frames for a masked test
DIST_BINS = [(0.35, 1.0), (1.0, 2.0), (2.0, np.inf)]   # nearest-keypoint distance, body lengths
BANDS = {"low_<0.5Hz": (None, 0.5), "mid_0.5-1.5Hz": (0.5, 1.5), "high_>1.5Hz": (1.5, None)}


def clip_tests(args):
    vid, f, fps, video_path = args
    a = f["torso_A_speed_u"].to_numpy(float); b = f["torso_B_speed_u"].to_numpy(float)
    cs = f["contact_state"].to_numpy(float); d = f["contact_proxy_min_dist_u"].to_numpy(float)
    cam = f["camera_motion_px"].to_numpy(float) if "camera_motion_px" in f else np.full(len(a), np.nan)
    row = {"video": vid, "n_frames": int((np.isfinite(a) & np.isfinite(b)).sum()), "contact_frac": float(np.nanmean(cs == 1))}
    # apparent-scale confound: zoom, dolly, or both dancers approaching the lens multiply BOTH speeds
    # (in fixed body lengths) by the same factor. Per-frame trunk length from the saved tracks.
    tp = Path(f"outputs/{vid}/{vid}_tracks.npz")
    if tp.exists():
        tr = load_tracks(tp); idx = f["frame"].to_numpy(int)
        w = int(5 * fps)
        LA = pd.Series(trunk_length_per_frame(tr.kpts[:, 0])[idx]).rolling(w, center=True, min_periods=w // 5).median().to_numpy()
        LB = pd.Series(trunk_length_per_frame(tr.kpts[:, 1])[idx]).rolling(w, center=True, min_periods=w // 5).median().to_numpy()
        shared = np.log(np.nanmean(np.vstack([LA, LB]), axis=0))
        row["scale_range_log"] = float(np.nanpercentile(shared, 95) - np.nanpercentile(shared, 5))  # 0.69 = scale doubles
        row["scale_AB_corr"] = float(pd.Series(LA).corr(pd.Series(LB)))
        a_loc = f["torso_A_speed"].to_numpy(float) / LA; b_loc = f["torso_B_speed"].to_numpy(float) / LB
    else:
        shared = a_loc = b_loc = None

    def put(name, res, n=None):
        for k in ("r_obs", "p", "z"):
            row[f"{name}_{k}"] = res.get(k, np.nan)
        if n is not None:
            row[f"{name}_n"] = n

    lag, r, r0 = peak(a, b, fps); row.update(peak_lag_s=lag, peak_r=r, r_lag0=r0)
    put("circ", shift_null(a, b, fps, n=N_SURR))
    put("local", shift_null(a, b, fps, shift_range_s=(3.0, 10.0), n=N_SURR))
    for name, (lo, hi) in BANDS.items():
        put(name, shift_null(bandpass_runs(a, fps, lo, hi), bandpass_runs(b, fps, lo, hi), fps, n=N_SURR))
    if shared is not None and np.isfinite(shared).sum() > 0.5 * len(shared):
        cov = [shared, np.r_[0, np.diff(shared)]]
        put("scale_partial", shift_null(partial_out(a, cov), partial_out(b, cov), fps, n=N_SURR))
        put("local_bl", shift_null(a_loc, b_loc, fps, n=N_SURR))
        if int(((cs == 0) & np.isfinite(a_loc) & np.isfinite(b_loc)).sum()) >= MIN_FRAMES_STATE:
            put("free_local_bl", shift_null(a_loc, b_loc, fps, mask=cs == 0, n=N_SURR))
    if np.isfinite(cam).sum() > 0.5 * len(cam) and np.nanstd(cam) > 0:
        cov = [cam, np.abs(np.r_[0, np.diff(cam)])]
        put("cam_partial", shift_null(partial_out(a, cov), partial_out(b, cov), fps, n=N_SURR))
    for name, m in (("free", cs == 0), ("contact", cs == 1)):
        n = int((m & np.isfinite(a) & np.isfinite(b)).sum())
        if n >= MIN_FRAMES_STATE:
            res = shift_null(a, b, fps, mask=m, n=N_SURR)
            put(name, res, n)
            lag_m, _, _ = peak(np.where(m, a, np.nan), np.where(m, b, np.nan), fps)
            row[f"{name}_lag_s"] = lag_m
            if name == "free":
                put("free_local", shift_null(a, b, fps, mask=m, shift_range_s=(3.0, 10.0), n=N_SURR))
        else:
            row[f"{name}_n"] = n
    # music confound: does each dancer follow the sound, and does coupling survive removing it?
    audio = load_mono(video_path) if video_path else None
    rms, flux = frame_envelopes(audio, fps, len(a)) if audio is not None else (None, None)
    row["has_audio"] = rms is not None
    if rms is not None:
        flux_s = pd.Series(flux).rolling(int(fps), center=True, min_periods=1).mean().to_numpy()
        for lab, x in (("A", a), ("B", b)):
            res = shift_null(x, flux_s, fps, n=N_SURR); row[f"audio_{lab}_r"] = res["r_obs"]; row[f"audio_{lab}_p"] = res["p"]
        cov = [rms, flux_s, pd.Series(rms).rolling(int(2 * fps), center=True, min_periods=1).mean().to_numpy()]
        ar, br = partial_out(a, cov), partial_out(b, cov)
        put("audio_partial", shift_null(ar, br, fps, n=N_SURR))
        m = cs == 0
        if int((m & np.isfinite(ar) & np.isfinite(br)).sum()) >= MIN_FRAMES_STATE:
            put("free_audio_partial", shift_null(ar, br, fps, mask=m, n=N_SURR))
    # vertical "bounce" velocity (image y, body lengths/s): the signal that carried the partner effect on
    # the Bigand et al. mocap with a known null (AUDIT 34). Positive image y is down; |r| is sign-free.
    if "torso_A_vy" in f and "scale_A_px" in f:
        va = f["torso_A_vy"].to_numpy(float) / f["scale_A_px"].iloc[0]; vb = f["torso_B_vy"].to_numpy(float) / f["scale_B_px"].iloc[0]
        put("bounce_circ", shift_null(va, vb, fps, n=N_SURR))
        n = int(((cs == 0) & np.isfinite(va) & np.isfinite(vb)).sum())
        if n >= MIN_FRAMES_STATE:
            put("bounce_free", shift_null(va, vb, fps, mask=cs == 0, n=N_SURR), n)
    for lo, hi in DIST_BINS:
        m = (cs == 0) & (d >= lo) & (d < hi); n = int((m & np.isfinite(a) & np.isfinite(b)).sum())
        name = f"dist_{lo:g}-{hi:g}bl"
        if n >= MIN_FRAMES_STATE:
            put(name, shift_null(a, b, fps, mask=m, n=N_SURR), n)
        else:
            row[f"{name}_n"] = n
    return row


def pseudo_pairs(series: dict, groups: dict, fps_map: dict):
    """Percentile of each true pair's peak |r| among pseudo-pairs (A_i,B_j), (A_j,B_i), j from another source."""
    rs = {v: (resample(a, fps_map[v]), resample(b, fps_map[v])) for v, (a, b) in series.items()}
    rows = []
    for i, (ai, bi) in rs.items():
        true = abs(peak(ai, bi, 25.0)[1]); null = []
        for j, (aj, bj) in rs.items():
            if groups[j] == groups[i]:
                continue
            for x, y in ((ai, bj), (aj, bi)):
                L = min(len(x), len(y)); null.append(abs(peak(x[:L], y[:L], 25.0)[1]))
        null = np.array([x for x in null if np.isfinite(x)])
        rows.append({"video": i, "true_abs_r": true, "pseudo_median": float(np.median(null)), "pseudo_95": float(np.percentile(null, 95)),
                     "p_pseudo": float((np.sum(null >= true) + 1) / (len(null) + 1)), "n_pseudo": int(len(null))})
    return pd.DataFrame(rows)


def by_source(per_clip: pd.DataFrame, test: str) -> dict:
    """Stouffer within source group (z from each clip's surrogate p), then across groups.
    Also: how many groups have a combined p < 0.05, against Binomial(G, 0.05)."""
    col = f"{test}_p"
    if col not in per_clip:
        return {"n_groups": 0}
    t = per_clip.dropna(subset=[col])
    if t.empty:
        return {"n_groups": 0}
    z = stats.norm.isf(t[col].clip(1e-12, 1 - 1e-12))
    g = pd.DataFrame({"g": t["source_group"], "z": z}).groupby("g")["z"].agg(lambda s: s.sum() / np.sqrt(len(s)))
    G = len(g); zc = float(g.sum() / np.sqrt(G)); sig = int((g > stats.norm.isf(0.05)).sum())
    return {"n_clips": int(len(t)), "n_groups": G, "groups_sig": sig, "stouffer_z": zc, "p_stouffer": float(stats.norm.sf(zc)),
            "p_binom_groups": float(stats.binomtest(sig, G, 0.05, alternative="greater").pvalue),
            "median_r": float(t[f"{test}_r_obs"].abs().median()) if f"{test}_r_obs" in t else np.nan}


SETS = {"primary": ("yes",), "secondary": ("yes", "partial"), "failed": ("no",), "all": None}


def main(sets=("primary", "secondary", "failed", "all"), reuse: bool = False):
    OUT.mkdir(parents=True, exist_ok=True)
    videos = pd.read_csv("outputs/dataset/videos.csv").set_index("video")
    cur = pd.read_csv("videos/curation.csv").set_index("video")
    if reuse:   # recompute the summaries from the saved per-clip tests (e.g. after editing the curation)
        per_clip = pd.read_csv(OUT / "coupling_per_clip.csv").drop(columns=["setting", "source_group", "pair_ok"], errors="ignore")
        per_clip = per_clip.join(cur[["setting", "source_group", "pair_ok"]], on="video")
        return summarize(per_clip, sets)
    frames = pd.read_csv("outputs/dataset/frames.csv", low_memory=False)
    inc = [v for v in videos.index[videos.included] if v in cur.index and cur.loc[v, "content"] == "ci_dance"]
    missing = [v for v in videos.index[videos.included] if v not in cur.index]
    if missing:
        print(f"[coupling] WARNING: included but not curated (ignored): {missing}")
    import glob
    frames = frames.merge(videos[["scale_A_px", "scale_B_px"]], left_on="video", right_index=True, how="left")
    jobs = [(v, frames[frames.video == v].reset_index(drop=True), float(videos.loc[v, "fps"]), (sorted(glob.glob(f"videos/{v}.*")) or [None])[0]) for v in inc]
    with ProcessPoolExecutor(4) as ex:
        per_clip = pd.DataFrame(list(ex.map(clip_tests, jobs)))
    per_clip = per_clip.join(cur[["setting", "source_group", "pair_ok"]], on="video")
    series = {v: (f["torso_A_speed_u"].to_numpy(float), f["torso_B_speed_u"].to_numpy(float)) for v, f, _, _ in jobs}
    pp = pseudo_pairs(series, cur["source_group"].to_dict(), videos["fps"].to_dict())
    per_clip = per_clip.merge(pp, on="video", how="left")
    per_clip.to_csv(OUT / "coupling_per_clip.csv", index=False)
    return summarize(per_clip, sets)


def summarize(per_clip: pd.DataFrame, sets):

    tests = ["circ", "local", *BANDS, "cam_partial", "scale_partial", "local_bl", "free_local_bl", "audio_partial", "contact", "free", "free_local", "free_audio_partial", "bounce_circ", "bounce_free", *[f"dist_{lo:g}-{hi:g}bl" for lo, hi in DIST_BINS], "pseudo"]
    summary = {}
    md = ["# Coupling with controls\n",
          "Statistic: peak |r| of torso speeds (body lengths/s) within ±2 s. Each test compares it with a null; "
          "`p` per clip, combined by Stouffer within source group and then across groups (groups are the unit of inference).\n",
          "| test | what it rules out |\n|---|---|",
          "| circ | chance alignment of autocorrelated series (circular shifts ≥ 5 s) |",
          "| local | slow shared modulation only (shifts 3-10 s keep it, break moment-to-moment alignment) |",
          "| low/mid/high band | high-frequency shared jitter or compression artifacts |",
          "| cam_partial | residual camera ego-motion (speeds regressed on camera motion first) |",
          "| scale_partial / local_bl | zoom, dolly or depth changes that scale both dancers' speeds together (shared log trunk length regressed out / speeds in each dancer's own rolling 5 s trunk length) |",
          "| audio_partial | both dancers following the music (speeds regressed on the audio energy / onset envelopes first) |",
          "| contact / free | rigid-body coupling while touching / coupling without touch |",
          "| dist_x-y bl | keypoint mixing between overlapping bodies (free frames binned by nearest-keypoint distance) |",
          "| pseudo | generic CI movement statistics (A of one clip vs B of a clip from another source) |\n"]
    for name in sets:
        keep = SETS[name]
        pc = (per_clip if keep is None else per_clip[per_clip.pair_ok.isin(keep)]).copy()
        if pc.empty:
            continue
        pc["pseudo_p"] = pc["p_pseudo"]; pc["pseudo_r_obs"] = pc["true_abs_r"]
        s = {t: by_source(pc, t) for t in tests}; summary[name] = s
        md.append(f"\n## {name} set: {len(pc)} clips, {pc.source_group.nunique()} source groups (pair_ok: {keep or 'any'})\n")
        tab = pd.DataFrame(s).T.reset_index().rename(columns={"index": "test"})
        md.append(tab.round(4).to_markdown(index=False))
        free_lags = pc.dropna(subset=["free_p"])
        if len(free_lags):
            md.append(f"\n\nPeak lag in free (no-contact) frames: median {free_lags.free_lag_s.median():+.2f} s, "
                      f"|lag| <= 0.2 s in {int((free_lags.free_lag_s.abs() <= 0.2).sum())} of {len(free_lags)} clips.\n")
    md.append("\n## Per clip\n")
    cols = ["video", "source_group", "pair_ok", "n_frames", "contact_frac", "scale_range_log", "peak_lag_s", "peak_r", "circ_p", "local_p",
            "mid_0.5-1.5Hz_p", "high_>1.5Hz_p", "cam_partial_p", "scale_partial_p", "local_bl_p", "free_local_bl_p", "free_n", "free_r_obs", "free_p", "free_lag_s", "audio_A_p", "audio_B_p", "audio_partial_p", "free_audio_partial_p", "bounce_circ_p", "bounce_free_r_obs", "bounce_free_p", "dist_1-2bl_p", "dist_2-infbl_p", "p_pseudo"]
    md.append(per_clip[[c for c in cols if c in per_clip]].round(3).to_markdown(index=False))
    (OUT / "coupling_report.md").write_text("\n".join(md))
    json.dump(summary, open(OUT / "coupling_summary.json", "w"), indent=2, default=float)

    pc = per_clip[per_clip.pair_ok == "yes"]
    fig, ax = plt.subplots(figsize=(8, 4))
    show = ["circ", "local", "low_<0.5Hz", "mid_0.5-1.5Hz", "high_>1.5Hz", "cam_partial", "free", "dist_1-2bl", "dist_2-infbl"]
    for i, t in enumerate(show):
        if f"{t}_p" in pc:
            p = pc[f"{t}_p"].dropna()
            ax.scatter(np.full(len(p), i) + np.random.default_rng(i).uniform(-.15, .15, len(p)), -np.log10(p), s=14)
    ax.axhline(-np.log10(0.05), color="k", ls="--", lw=0.8); ax.set_xticks(range(len(show))); ax.set_xticklabels(show, rotation=30, ha="right", fontsize=8)
    ax.set_ylabel("-log10 p (per clip)"); ax.set_title("Coupling under each control (primary set)")
    fig.tight_layout(); fig.savefig(OUT / "coupling_controls.png", dpi=150)
    print("\n".join(md[:60]))


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(); ap.add_argument("--reuse", action="store_true", help="only re-summarise saved per-clip tests")
    main(reuse=ap.parse_args().reuse)
