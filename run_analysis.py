"""
Main pipeline execution script for Contact Improvisation movement analysis.
Processes a video, tracks two dancers, extracts features, analyzes coordination,
and produces plots, video overlays, and an HTML report.
"""

import sys
import argparse
from typing import Optional, Dict, Any
from pathlib import Path
import numpy as np
import pandas as pd
import cv2

from src.pose.pose_detector import PoseDetector
from src.tracking.dancer_tracker import TwoDancerTracker
from src.features.kinematics import extract_features_timeseries
from src.analysis.coordination import CrossCorrelationAnalysis, PhaseAnalysis, AnnotationManager
from src.visualization.plots import (
    plot_trajectories,
    plot_movement_dynamics_dashboard,
    plot_phase_summary
)
from src.visualization.video_overlay import render_overlay_video
from src.visualization.report import generate_html_report


def process_ci_video(
    video_path: str,
    annotation_path: Optional[str] = None,
    output_dir: str = "outputs",
    model_name: str = "yolov8n-pose.pt",
    render_video: bool = True,
    max_frames: Optional[int] = None
) -> Dict[str, Any]:
    """Runs end-to-end CI movement analysis on a video file."""
    video_path = Path(video_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    video_stem = video_path.stem

    print(f"==================================================")
    print(f"Analyzing CI Video: {video_path.name}")
    print(f"==================================================")

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise FileNotFoundError(f"Cannot open video: {video_path}")

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if max_frames:
        total_frames = min(total_frames, max_frames)
    dt = 1.0 / fps

    print(f"Resolution: {width}x{height} | FPS: {fps:.2f} | Frames to process: {total_frames}")

    # Initialize Detector & Tracker
    detector = PoseDetector(model_name=model_name)
    tracker = TwoDancerTracker(max_match_distance=width * 0.45)

    records_A = []
    records_B = []

    frame_idx = 0
    while True:
        ret, frame = cap.read()
        if not ret or (max_frames and frame_idx >= max_frames):
            break

        # Pose detection with tracking
        detections = detector.detect_frame(frame, track=True)

        # 2-Dancer persistent association
        det_A, det_B = tracker.step(detections, dt=dt)

        # Dancer A record
        if det_A is not None:
            records_A.append({
                "present": True,
                "pelvis_pos": det_A.pelvis_center,
                "torso_pos": det_A.torso_center,
                "body_pos": det_A.body_center,
                "keypoints": det_A.keypoints,
                "bbox": det_A.bbox,
                "conf": det_A.bbox_conf
            })
        else:
            records_A.append({
                "present": False,
                "pelvis_pos": np.array([np.nan, np.nan]),
                "torso_pos": np.array([np.nan, np.nan]),
                "body_pos": np.array([np.nan, np.nan]),
                "keypoints": np.zeros((17, 3)),
                "bbox": np.zeros(4),
                "conf": 0.0
            })

        # Dancer B record
        if det_B is not None:
            records_B.append({
                "present": True,
                "pelvis_pos": det_B.pelvis_center,
                "torso_pos": det_B.torso_center,
                "body_pos": det_B.body_center,
                "keypoints": det_B.keypoints,
                "bbox": det_B.bbox,
                "conf": det_B.bbox_conf
            })
        else:
            records_B.append({
                "present": False,
                "pelvis_pos": np.array([np.nan, np.nan]),
                "torso_pos": np.array([np.nan, np.nan]),
                "body_pos": np.array([np.nan, np.nan]),
                "keypoints": np.zeros((17, 3)),
                "bbox": np.zeros(4),
                "conf": 0.0
            })

        frame_idx += 1
        if frame_idx % 60 == 0 or frame_idx == total_frames:
            print(f"  Processed {frame_idx}/{total_frames} frames ({(frame_idx/total_frames)*100:.1f}%)")

    cap.release()

    # Feature extraction
    print("\nExtracting interpersonal movement features...")
    df_features = extract_features_timeseries(
        records_A, records_B, fps=fps, frame_width=width, frame_height=height
    )
    features_csv_path = output_dir / f"{video_stem}_features.csv"
    df_features.to_csv(features_csv_path, index=False)
    print(f"  Features saved to: {features_csv_path}")

    # Manual Annotations
    annotation_mgr = None
    df_phase_summary = None
    if annotation_path and Path(annotation_path).exists():
        print(f"\nLoading manual annotations from: {annotation_path}")
        annotation_mgr = AnnotationManager(annotation_path)
        df_phase_summary = annotation_mgr.summarize_phases(df_features, fps=fps)
        phase_csv_path = output_dir / f"{video_stem}_phase_summary.csv"
        df_phase_summary.to_csv(phase_csv_path, index=False)
        print(f"  Phase summary saved to: {phase_csv_path}")

    # Coordination Analysis: Cross-Correlation
    print("\nComputing time-lagged cross-correlation...")
    global_xcorr = CrossCorrelationAnalysis.compute_xcorr(
        df_features["torso_A_speed"].to_numpy(),
        df_features["torso_B_speed"].to_numpy(),
        fps=fps,
        max_lag_sec=2.0
    )
    lags, corr, peak_lag, peak_corr = global_xcorr
    print(f"  Peak Lag (τ*): {peak_lag:+.2f}s | Peak R: {peak_corr:.2f}")
    if peak_lag > 0.05:
        print(f"  Coupling: Dancer A movement precedes Dancer B by {peak_lag:.2f}s")
    elif peak_lag < -0.05:
        print(f"  Coupling: Dancer B movement precedes Dancer A by {abs(peak_lag):.2f}s")
    else:
        print(f"  Coupling: Simultaneous / synchronized movement (peak lag ~ 0s)")

    # Rolling Cross-Correlation
    rolling_xcorr = CrossCorrelationAnalysis.compute_rolling_xcorr(
        df_features["torso_A_speed"].to_numpy(),
        df_features["torso_B_speed"].to_numpy(),
        fps=fps,
        window_sec=4.0,
        step_sec=0.5,
        max_lag_sec=2.0
    )

    # Phase coherence
    phase_diff, plv = PhaseAnalysis.compute_phase_coherence(
        df_features["torso_A_y"].to_numpy(),
        df_features["torso_B_y"].to_numpy(),
        fps=fps
    )
    print(f"  Vertical level phase locking value (PLV): {plv:.2f}")

    # Plots
    print("\nGenerating visualization figures...")
    traj_path = output_dir / f"{video_stem}_trajectories.png"
    plot_trajectories(df_features, title=f"Trajectories: {video_stem}", save_path=str(traj_path))

    dash_path = output_dir / f"{video_stem}_dashboard.png"
    plot_movement_dynamics_dashboard(
        df_features,
        global_xcorr=global_xcorr,
        rolling_xcorr=rolling_xcorr,
        annotation_mgr=annotation_mgr,
        title=f"Movement & Coordination Dynamics: {video_stem}",
        save_path=str(dash_path)
    )

    phase_img_path = None
    if df_phase_summary is not None and not df_phase_summary.empty:
        phase_img_path = str(output_dir / f"{video_stem}_phase_comparison.png")
        plot_phase_summary(df_phase_summary, save_path=phase_img_path)

    # Annotated Video
    annotated_video_path = None
    if render_video:
        print("\nRendering annotated video with skeleton overlays and metrics HUD...")
        annotated_video_path = output_dir / f"{video_stem}_annotated.mp4"
        render_overlay_video(
            input_video_path=str(video_path),
            output_video_path=str(annotated_video_path),
            df_features=df_features,
            records_A=records_A,
            records_B=records_B,
            annotation_mgr=annotation_mgr
        )
        print(f"  Annotated video rendered: {annotated_video_path}")

    # HTML Report
    html_report_path = output_dir / f"{video_stem}_report.html"
    generate_html_report(
        output_html_path=str(html_report_path),
        video_name=video_path.name,
        dashboard_img_path=str(dash_path),
        trajectory_img_path=str(traj_path),
        phase_summary_img_path=phase_img_path,
        df_phase_summary=df_phase_summary,
        global_xcorr_info={"peak_lag": peak_lag, "peak_corr": peak_corr},
        video_annotated_relpath=annotated_video_path.name if annotated_video_path else None
    )
    print(f"\nHTML Report generated: {html_report_path}")
    print("==================================================")
    print("Analysis complete!\n")

    return {
        "df_features": df_features,
        "df_phase_summary": df_phase_summary,
        "global_xcorr": global_xcorr,
        "rolling_xcorr": rolling_xcorr,
        "plv": plv,
        "dash_path": dash_path,
        "traj_path": traj_path,
        "html_report_path": html_report_path,
        "annotated_video_path": annotated_video_path
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Contact Improvisation Movement Analysis")
    parser.add_argument("--video", type=str, required=True, help="Path to input MP4 video")
    parser.add_argument("--annotations", type=str, default=None, help="Path to CSV/JSON annotations file")
    parser.add_argument("--output-dir", type=str, default="outputs", help="Directory to save outputs")
    parser.add_argument("--max-frames", type=int, default=None, help="Max frames to process for quick testing")
    parser.add_argument("--no-video", action="store_true", help="Skip rendering annotated MP4 video")
    args = parser.parse_args()

    process_ci_video(
        video_path=args.video,
        annotation_path=args.annotations,
        output_dir=args.output_dir,
        render_video=not args.no_video,
        max_frames=args.max_frames
    )
