"""
Video Overlay module for Contact Improvisation movement analysis.
Draws tracked skeletons, trajectory trails, and a real-time metrics HUD
directly onto the video frames.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import numpy as np
import pandas as pd
import cv2
from src.pose.pose_detector import SKELETON_EDGES, KEYPOINT_INDEX


# Colors in BGR for OpenCV
BGR_A = (128, 128, 0)      # Teal (B=128, G=128, R=0) -> or (200, 160, 0)
BGR_A_PRIMARY = (180, 150, 0)   # Teal/Cyan tone
BGR_B = (0, 140, 240)      # Amber / Orange (B=0, G=140, R=240)
BGR_TRAIL_A = (220, 200, 50)
BGR_TRAIL_B = (30, 180, 255)


def draw_skeleton(
    img: np.ndarray,
    keypoints: np.ndarray,
    color: tuple,
    conf_thresh: float = 0.25,
    thickness: int = 2
):
    """Draws keypoints and bones of a dancer on the image."""
    for p1_idx, p2_idx in SKELETON_EDGES:
        pt1 = keypoints[p1_idx]
        pt2 = keypoints[p2_idx]
        if pt1[2] >= conf_thresh and pt2[2] >= conf_thresh:
            c1 = (int(round(pt1[0])), int(round(pt1[1])))
            c2 = (int(round(pt2[0])), int(round(pt2[1])))
            cv2.line(img, c1, c2, color, thickness, cv2.LINE_AA)

    for i in range(len(keypoints)):
        pt = keypoints[i]
        if pt[2] >= conf_thresh:
            center = (int(round(pt[0])), int(round(pt[1])))
            cv2.circle(img, center, 4, color, -1, cv2.LINE_AA)
            cv2.circle(img, center, 5, (255, 255, 255), 1, cv2.LINE_AA)


def render_overlay_video(
    input_video_path: str,
    output_video_path: str,
    df_features: pd.DataFrame,
    records_A: List[Dict[str, Any]],
    records_B: List[Dict[str, Any]],
    annotation_mgr: Optional[Any] = None,
    trail_length: int = 25
):
    """
    Renders an annotated MP4 video with skeleton overlays, motion trails,
    and a synchronous kinematics HUD.
    """
    cap = cv2.VideoCapture(input_video_path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open video {input_video_path}")

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    Path(output_video_path).parent.mkdir(parents=True, exist_ok=True)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

    trails_A = []
    trails_B = []

    frame_idx = 0
    while True:
        ret, frame = cap.read()
        if not ret or frame_idx >= len(df_features):
            break

        row = df_features.iloc[frame_idx]
        t_sec = row["time_sec"]

        rec_A = records_A[frame_idx] if frame_idx < len(records_A) else {}
        rec_B = records_B[frame_idx] if frame_idx < len(records_B) else {}

        # Draw Trajectory Trails
        if not np.isnan(row["torso_A_x"]):
            pos_A = (int(round(row["torso_A_x"])), int(round(row["torso_A_y"])))
            trails_A.append(pos_A)
            if len(trails_A) > trail_length:
                trails_A.pop(0)

        if not np.isnan(row["torso_B_x"]):
            pos_B = (int(round(row["torso_B_x"])), int(round(row["torso_B_y"])))
            trails_B.append(pos_B)
            if len(trails_B) > trail_length:
                trails_B.pop(0)

        for i in range(1, len(trails_A)):
            cv2.line(frame, trails_A[i-1], trails_A[i], BGR_TRAIL_A, 2, cv2.LINE_AA)
        for i in range(1, len(trails_B)):
            cv2.line(frame, trails_B[i-1], trails_B[i], BGR_TRAIL_B, 2, cv2.LINE_AA)

        # Draw Skeletons
        kpts_A = rec_A.get("keypoints")
        if kpts_A is not None and rec_A.get("present", False):
            draw_skeleton(frame, kpts_A, BGR_A_PRIMARY, thickness=2)
            if not np.isnan(row["torso_A_x"]):
                cv2.putText(
                    frame, "Dancer A",
                    (int(row["torso_A_x"]) - 35, int(row["torso_A_y"]) - 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, BGR_A_PRIMARY, 2, cv2.LINE_AA
                )

        kpts_B = rec_B.get("keypoints")
        if kpts_B is not None and rec_B.get("present", False):
            draw_skeleton(frame, kpts_B, BGR_B, thickness=2)
            if not np.isnan(row["torso_B_x"]):
                cv2.putText(
                    frame, "Dancer B",
                    (int(row["torso_B_x"]) - 35, int(row["torso_B_y"]) - 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, BGR_B, 2, cv2.LINE_AA
                )

        # Draw connection line between torso centers
        if not (np.isnan(row["torso_A_x"]) or np.isnan(row["torso_B_x"])):
            pA = (int(round(row["torso_A_x"])), int(round(row["torso_A_y"])))
            pB = (int(round(row["torso_B_x"])), int(round(row["torso_B_y"])))
            cv2.line(frame, pA, pB, (200, 200, 200), 1, cv2.LINE_AA)

        # Draw HUD bar at the top
        hud_h = 55
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (width, hud_h), (25, 25, 25), -1)
        cv2.addWeighted(overlay, 0.75, frame, 0.25, 0, frame)

        # HUD Text
        cur_phase = annotation_mgr.get_phase_at_time(t_sec) if annotation_mgr else None
        phase_str = f"Phase: {cur_phase}" if cur_phase else "Phase: Unannotated"

        dist_val = f"Dist: {row['dist_torso']:.0f}px" if not np.isnan(row['dist_torso']) else "Dist: --"
        spdA_val = f"v_A: {row['torso_A_speed']:.0f}px/s" if not np.isnan(row['torso_A_speed']) else "v_A: --"
        spdB_val = f"v_B: {row['torso_B_speed']:.0f}px/s" if not np.isnan(row['torso_B_speed']) else "v_B: --"
        dir_val = f"CosSim: {row['dir_sim_torso']:+.2f}" if not np.isnan(row['dir_sim_torso']) else "CosSim: --"

        hud_text = f"Time: {t_sec:05.2f}s | {phase_str} | {dist_val} | {spdA_val} | {spdB_val} | {dir_val}"
        cv2.putText(
            frame, hud_text, (15, 34),
            cv2.FONT_HERSHEY_SIMPLEX, 0.60, (255, 255, 255), 2, cv2.LINE_AA
        )

        out.write(frame)
        frame_idx += 1

    cap.release()
    out.release()
