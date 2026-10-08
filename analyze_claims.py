"""
Run the thesis hypothesis tests on outputs/dataset/ and write outputs/claims/claims_report.md
plus figures. Replaces the pooled boxplots of the former meta_analysis_MAs.py.
"""
from __future__ import annotations

import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.analysis.claims import per_video_contrast, combine_across_videos, mixed_model, noise_floor_table, ke_transfer_summary, coupling_by_state
from src.analysis.coordination import CrossCorrelationAnalysis

OUT = Path("outputs/claims"); OUT.mkdir(parents=True, exist_ok=True)


def main(dataset_dir: str = "outputs/dataset", include_moving_camera: bool = False):
    videos = pd.read_csv(f"{dataset_dir}/videos.csv")
    windows = pd.read_csv(f"{dataset_dir}/windows.csv")
    frames = pd.read_csv(f"{dataset_dir}/frames.csv", low_memory=False)
    inc = videos[videos.included].video.tolist()
    if include_moving_camera:
        inc = videos[videos.exclusion_reason.fillna("").isin(["", "moving_camera"])].video.tolist()
    windows = windows[windows.video.isin(inc)]; frames = frames[frames.video.isin(inc)]
    md = [f"# Hypothesis tests ({len(inc)} videos included)\n", f"Inclusion: {videos.included.sum()} of {len(videos)} videos; "
          f"exclusions: {videos[~videos.included].exclusion_reason.value_counts().to_dict()}\n"]

    md.append("\n## 0. Is jerk above the estimator noise floor?\n")
    nf = noise_floor_table(videos).round(2)
    md.append(nf.to_markdown(index=False))
    md.append(f"\n\nMedian ratio (median jerk / noise floor) across included videos: "
              f"{nf[nf.included].jerk_over_noise_floor.median():.2f}. Below ~3 the per-frame jerk is mostly keypoint jitter.\n")

    md.append("\n## H1. State-dependent smoothness (contact vs no-contact windows, within video)\n")
    results = {}
    for metric, nice in (("sparc", "SPARC (higher = smoother)"), ("ldlj", "LDLJ (higher = smoother)"), ("median_jerk_u", "median jerk [bl/s^3] (lower = smoother)")):
        pv = per_video_contrast(windows, metric)
        comb = combine_across_videos(pv) if len(pv) else {"n_videos": 0}
        mm = mixed_model(windows, metric)
        results[metric] = {"per_video": pv.to_dict("records"), "combined": comb, "mixed_model": mm}
        md.append(f"\n### {nice}\n")
        if len(pv):
            md.append(pv.round(3).to_markdown(index=False))
        md.append(f"\n\nCombined: {json.dumps(comb, default=float)}\n\nMixed model (y ~ contact + (1|video:dancer)): {json.dumps(mm, default=float)}\n")
        if len(pv):
            fig, ax = plt.subplots(figsize=(7, 4))
            ax.axhline(0, color="k", lw=0.8)
            ax.bar(range(len(pv)), pv["diff"], color=np.where(pv["diff"] > 0, "#E66100", "#008080"))
            ax.set_xticks(range(len(pv))); ax.set_xticklabels(pv.video, rotation=90, fontsize=7)
            ax.set_ylabel(f"{metric}: contact - free (per video)"); ax.set_title(f"H1 per-video contrast: {nice}")
            fig.tight_layout(); fig.savefig(OUT / f"h1_{metric}_per_video.png", dpi=150); plt.close(fig)

    md.append("\n## H2. Momentum transfer (KE-transfer correlation in contact windows)\n")
    ket = ke_transfer_summary(windows)
    results["ke_transfer"] = ket.to_dict("records")
    md.append(ket.round(3).to_markdown(index=False) if len(ket) else "not enough windows")

    md.append("\n\n## H3. Coupling: peak |xcorr| of speeds vs circular-shift surrogates\n")
    rows = []
    for vid, f in frames.groupby("video"):
        fps = videos.set_index("video").loc[vid, "fps"]
        a, b = f["torso_A_speed_u"].to_numpy(), f["torso_B_speed_u"].to_numpy()
        _, _, lag, r = CrossCorrelationAnalysis.compute_xcorr(a, b, fps, 2.0)
        s = CrossCorrelationAnalysis.surrogate_test(a, b, fps, 2.0, n_surrogates=100)
        rows.append({"video": vid, "peak_lag_s": lag, "peak_r": r, "null_95": s["null_95"], "p": s["p_value"], "at_window_edge": abs(abs(lag) - 2.0) < 0.05})
    h3 = pd.DataFrame(rows); results["coupling"] = h3.to_dict("records")
    md.append(h3.round(3).to_markdown(index=False))
    md.append(f"\n\nVideos with p < 0.05: {(h3.p < 0.05).sum()} of {len(h3)}; peaks sitting at the ±2 s window edge (artifact-prone): {int(h3.at_window_edge.sum())}\n")

    md.append("\n\n## H3b. Coupling outside contact (removes the rigid-body null) vs inside contact\n")
    rows = []
    for vid, f in frames.groupby("video"):
        fps = videos.set_index("video").loc[vid, "fps"]
        cb = coupling_by_state(f, fps)
        rows.append({"video": vid, **{f"{k}_{kk}": vv for k, d in cb.items() for kk, vv in d.items() if kk in ("n_frames", "peak_lag_s", "peak_r", "p")}})
    h3b = pd.DataFrame(rows); results["coupling_by_state"] = h3b.to_dict("records")
    md.append(h3b.round(3).to_markdown(index=False))
    if "no_contact_p" in h3b:
        md.append(f"\n\nNo-contact coupling significant (p < 0.05): {int((h3b.no_contact_p < 0.05).sum())} of {int(h3b.no_contact_p.notna().sum())} videos with enough frames.\n")

    (OUT / "claims_report.md").write_text("\n".join(md))
    with open(OUT / "claims_results.json", "w") as fh:
        json.dump(results, fh, indent=2, default=float)
    print("\n".join(md))


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(); ap.add_argument("--include-moving-camera", action="store_true"); a = ap.parse_args()
    main(include_moving_camera=a.include_moving_camera)
