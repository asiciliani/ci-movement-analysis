"""
Stage 1: video -> raw tracks.

Runs YOLOv8-pose + BoT-SORT(ReID) once, assigns the two foreground dancers with the
persistent TwoDancerTracker, estimates camera ego-motion on the background, and writes:

  outputs/<stem>/<stem>_tracks.npz            raw per-frame keypoints of dancer A/B
  outputs/<stem>/<stem>_detections.csv        every detection in every frame (for group/jam analysis)
  outputs/<stem>/<stem>_tracking_quality.json detection rates, dropouts, id switches, camera motion

Nothing kinematic is computed here; see run_features.py.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
import numpy as np
import pandas as pd
import cv2

from src.pose.pose_detector import PoseDetector
from src.tracking.dancer_tracker import TwoDancerTracker
from src.tracking.camera_motion import CameraMotionEstimator, summarize_camera_motion
from src.io.tracks import Tracks, save_tracks


def track_video(video_path: str, output_dir: str, model_name: str = "yolov8n-pose.pt", tracker_config: str | None = None,
                max_frames: int | None = None, camera_motion: bool = True, imgsz: int = 640, appearance_weight: float = 0.5) -> dict:
    video_path = Path(video_path)
    out = Path(output_dir); out.mkdir(parents=True, exist_ok=True)
    stem = video_path.stem

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise FileNotFoundError(video_path)
    width, height = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if max_frames:
        total = min(total, max_frames)
    print(f"[track] {video_path.name}: {width}x{height} @ {fps:.2f} fps, {total} frames")

    detector = PoseDetector(model_name=model_name, tracker_config=tracker_config)
    tracker = TwoDancerTracker(max_match_distance=width * 0.45, appearance_weight=appearance_weight)
    cam = CameraMotionEstimator() if camera_motion else None

    kpts = np.full((total, 2, 17, 3), np.nan, np.float32)
    bbox = np.full((total, 2, 4), np.nan, np.float32)
    present = np.zeros((total, 2), bool)
    track_id = np.full((total, 2), -1, np.int32)
    conf = np.zeros((total, 2), np.float32)
    cam_motion = np.full(total, np.nan, np.float32)
    cam_M = np.full((total, 2, 3), np.nan, np.float32)
    det_rows = []

    t0 = time.time()
    i = 0
    while i < total:
        ret, frame = cap.read()
        if not ret:
            break
        dets = detector.detect_frame(frame, track=True)
        for d in dets:
            det_rows.append([i, -1 if d.track_id is None else int(d.track_id), float(d.bbox_conf), *map(float, d.bbox), *d.keypoints.reshape(-1).tolist()])
        det_A, det_B = tracker.step(dets, dt=1.0 / fps, frame=frame)
        for j, d in enumerate((det_A, det_B)):
            if d is not None:
                kpts[i, j] = d.keypoints; bbox[i, j] = d.bbox; present[i, j] = True
                track_id[i, j] = -1 if d.track_id is None else int(d.track_id); conf[i, j] = d.bbox_conf
        if cam is not None:
            cam_motion[i], _ = cam.step(frame, [d.bbox for d in dets])
            cam_M[i] = cam.last_M
        i += 1
        if i % 300 == 0 or i == total:
            el = time.time() - t0
            print(f"  {i}/{total} ({i / el:.1f} fps, eta {(total - i) / max(i / el, 1e-6) / 60:.1f} min)")
    cap.release()
    n = i
    kpts, bbox, present, track_id, conf, cam_motion, cam_M = kpts[:n], bbox[:n], present[:n], track_id[:n], conf[:n], cam_motion[:n], cam_M[:n]

    cam_summary = summarize_camera_motion(cam_motion, width) if camera_motion else {"camera_static": None}
    quality = {"video": video_path.name, "width": width, "height": height, "fps": fps, "n_frames": n,
               "model": model_name, "tracker": detector.tracker_config, **tracker.quality_report(), "camera_motion": cam_summary}

    meta = {"video": video_path.name, "fps": fps, "width": width, "height": height, "n_frames": n, "model": model_name, "tracker": detector.tracker_config}
    save_tracks(out / f"{stem}_tracks.npz", Tracks(kpts, bbox, present, track_id, conf, cam_motion, meta, camera_M=cam_M))
    kp_cols = [f"kp{k}_{c}" for k in range(17) for c in "xyc"]
    pd.DataFrame(det_rows, columns=["frame", "track_id", "conf", "x1", "y1", "x2", "y2", *kp_cols]).to_csv(out / f"{stem}_detections.csv", index=False)
    with open(out / f"{stem}_tracking_quality.json", "w") as f:
        json.dump(quality, f, indent=2)
    print(f"[track] done: detected A {quality['detected_fraction_A']:.0%}, B {quality['detected_fraction_B']:.0%}, "
          f"suspected swaps {quality['suspected_identity_swaps']}, camera static: {cam_summary.get('camera_static')}")
    return quality


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Stage 1: pose + tracking -> raw tracks")
    ap.add_argument("--video", required=True)
    ap.add_argument("--output-dir", default=None, help="default: outputs/<video stem>")
    ap.add_argument("--model", default="yolov8n-pose.pt")
    ap.add_argument("--tracker", default=None, help="tracker yaml (default configs/botsort_reid.yaml)")
    ap.add_argument("--max-frames", type=int, default=None)
    ap.add_argument("--no-camera-motion", action="store_true")
    ap.add_argument("--appearance-weight", type=float, default=0.5, help="clothing-colour term in the 2-dancer assignment (0 = off)")
    a = ap.parse_args()
    track_video(a.video, a.output_dir or f"outputs/{Path(a.video).stem}", a.model, a.tracker, a.max_frames, not a.no_camera_motion, appearance_weight=a.appearance_weight)
