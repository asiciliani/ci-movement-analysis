"""
End-to-end runner (kept for backward compatibility with the old CLI):

    python run_analysis.py --video videos/x.mp4 [--annotations a.csv] [--output-dir outputs/x] [--no-video]

It chains the two stages (run_tracking.py -> run_features.py), then produces the dashboard,
trajectory plot, phase summary, annotated video and HTML report. Stage 1 is skipped when a
<stem>_tracks.npz already exists in the output dir, so features can be recomputed cheaply.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import numpy as np
import pandas as pd

from run_tracking import track_video
from run_features import run as run_features
from src.analysis.coordination import CrossCorrelationAnalysis, PhaseAnalysis, AnnotationManager
from src.visualization.plots import plot_trajectories, plot_movement_dynamics_dashboard, plot_phase_summary
from src.visualization.video_overlay import render_overlay_video
from src.visualization.report import generate_html_report


def process_ci_video(video_path: str, annotation_path: str | None = None, output_dir: str | None = None,
                     model_name: str = "yolov8n-pose.pt", render_video: bool = True, max_frames: int | None = None,
                     px_per_meter: float | None = None, tracker: str | None = None):
    video_path = Path(video_path)
    stem = video_path.stem
    out = Path(output_dir or f"outputs/{stem}"); out.mkdir(parents=True, exist_ok=True)
    tracks = out / f"{stem}_tracks.npz"
    if not tracks.exists() or max_frames:
        track_video(str(video_path), str(out), model_name=model_name, tracker_config=tracker, max_frames=max_frames)
    df, win, info = run_features(str(tracks), None, str(out), px_per_meter=px_per_meter)
    fps = info["fps"]

    annotation_mgr, df_phase = None, None
    if annotation_path and Path(annotation_path).exists():
        annotation_mgr = AnnotationManager(annotation_path)
        df_phase = annotation_mgr.summarize_phases(df, fps=fps)
        df_phase.to_csv(out / f"{stem}_phase_summary.csv", index=False)

    sA, sB = df["torso_A_speed_u"].to_numpy(), df["torso_B_speed_u"].to_numpy()
    global_xcorr = CrossCorrelationAnalysis.compute_xcorr(sA, sB, fps=fps, max_lag_sec=2.0)
    lags, corr, peak_lag, peak_corr = global_xcorr
    sur = CrossCorrelationAnalysis.surrogate_test(sA, sB, fps=fps, max_lag_sec=2.0)
    print(f"[analysis] peak lag {peak_lag:+.2f}s, r={peak_corr:.2f}, surrogate p={sur['p_value']:.3f} (null 95% |r| = {sur['null_95']:.2f})")
    rolling = CrossCorrelationAnalysis.compute_rolling_xcorr(sA, sB, fps=fps)
    _, plv = PhaseAnalysis.compute_phase_coherence(df["torso_A_y"].to_numpy(), df["torso_B_y"].to_numpy(), fps=fps)

    traj = out / f"{stem}_trajectories.png"; dash = out / f"{stem}_dashboard.png"
    plot_trajectories(df, title=f"Trajectories: {stem}", save_path=str(traj))
    plot_movement_dynamics_dashboard(df, global_xcorr=global_xcorr, rolling_xcorr=rolling, annotation_mgr=annotation_mgr,
                                     title=f"Movement & Coordination Dynamics: {stem}", save_path=str(dash))
    phase_img = None
    if df_phase is not None and not df_phase.empty:
        phase_img = str(out / f"{stem}_phase_comparison.png"); plot_phase_summary(df_phase, save_path=phase_img)

    annotated = None
    if render_video:
        from src.io.tracks import load_tracks
        tr = load_tracks(tracks)
        recs = {lab: [] for lab in "AB"}
        for i in range(tr.n_frames):
            for j, lab in enumerate("AB"):
                recs[lab].append({"present": bool(tr.present[i, j]), "keypoints": tr.kpts[i, j] if tr.present[i, j] else np.zeros((17, 3)),
                                  "bbox": tr.bbox[i, j], "torso_pos": df[[f"torso_{lab}_x", f"torso_{lab}_y"]].iloc[i].to_numpy()})
        annotated = out / f"{stem}_annotated.mp4"
        render_overlay_video(str(video_path), str(annotated), df, recs["A"], recs["B"], annotation_mgr=annotation_mgr)

    html = out / f"{stem}_report.html"
    generate_html_report(str(html), video_path.name, str(dash), str(traj), phase_img, df_phase,
                         {"peak_lag": peak_lag, "peak_corr": peak_corr, "surrogate_p": sur["p_value"]}, annotated.name if annotated else None)
    print(f"[analysis] report: {html}")
    return {"df_features": df, "df_windows": win, "info": info, "df_phase_summary": df_phase, "global_xcorr": global_xcorr,
            "surrogate": sur, "plv": plv, "html_report_path": html}


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Contact Improvisation movement analysis (tracking + features + report)")
    ap.add_argument("--video", required=True); ap.add_argument("--annotations", default=None); ap.add_argument("--output-dir", default=None)
    ap.add_argument("--max-frames", type=int, default=None); ap.add_argument("--no-video", action="store_true")
    ap.add_argument("--px-per-meter", type=float, default=None); ap.add_argument("--tracker", default=None); ap.add_argument("--model", default="yolov8n-pose.pt")
    a = ap.parse_args()
    process_ci_video(a.video, a.annotations, a.output_dir, a.model, not a.no_video, a.max_frames, a.px_per_meter, a.tracker)
