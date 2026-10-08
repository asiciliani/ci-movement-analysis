"""
Pose Detector module using YOLOv8-Pose for multi-person keypoint extraction.
Extracts COCO 17-keypoint skeleton landmarks with confidence scores.
"""

from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import cv2
from pathlib import Path


# COCO 17 Keypoint mapping
KEYPOINT_NAMES = [
    "nose",          # 0
    "left_eye",      # 1
    "right_eye",     # 2
    "left_ear",      # 3
    "right_ear",     # 4
    "left_shoulder", # 5
    "right_shoulder",# 6
    "left_elbow",    # 7
    "right_elbow",   # 8
    "left_wrist",    # 9
    "right_wrist",   # 10
    "left_hip",      # 11
    "right_hip",     # 12
    "left_knee",     # 13
    "right_knee",    # 14
    "left_ankle",    # 15
    "right_ankle",   # 16
]

KEYPOINT_INDEX = {name: i for i, name in enumerate(KEYPOINT_NAMES)}

# Standard skeleton connections for visualization
SKELETON_EDGES = [
    (0, 1), (0, 2), (1, 3), (2, 4),           # Facial landmarks
    (5, 6),                                   # Shoulder span
    (5, 7), (7, 9),                           # Left arm
    (6, 8), (8, 10),                          # Right arm
    (5, 11), (6, 12),                         # Torso sides
    (11, 12),                                 # Pelvis span
    (11, 13), (13, 15),                       # Left leg
    (12, 14), (14, 16),                       # Right leg
]


class PoseDetection:
    """Represents a single detected person in a frame."""
    def __init__(
        self,
        keypoints: np.ndarray,
        bbox: np.ndarray,
        bbox_conf: float,
        track_id: Optional[int] = None
    ):
        """
        Args:
            keypoints: (17, 3) array [x, y, confidence]
            bbox: [x1, y1, x2, y2]
            bbox_conf: confidence score of person detection
            track_id: optional tracking ID assigned by tracker
        """
        self.keypoints = keypoints  # shape (17, 3)
        self.bbox = bbox            # [x1, y1, x2, y2]
        self.bbox_conf = bbox_conf
        self.track_id = track_id

    @property
    def pelvis_center(self) -> np.ndarray:
        """Midpoint between left and right hips."""
        lh = self.keypoints[KEYPOINT_INDEX["left_hip"]]
        rh = self.keypoints[KEYPOINT_INDEX["right_hip"]]
        return (lh[:2] + rh[:2]) / 2.0

    @property
    def torso_center(self) -> np.ndarray:
        """Center of mass of torso: shoulders and hips."""
        ls = self.keypoints[KEYPOINT_INDEX["left_shoulder"]]
        rs = self.keypoints[KEYPOINT_INDEX["right_shoulder"]]
        lh = self.keypoints[KEYPOINT_INDEX["left_hip"]]
        rh = self.keypoints[KEYPOINT_INDEX["right_hip"]]
        return (ls[:2] + rs[:2] + lh[:2] + rh[:2]) / 4.0

    @property
    def body_center(self) -> np.ndarray:
        """Bounding box center."""
        x1, y1, x2, y2 = self.bbox
        return np.array([(x1 + x2) / 2.0, (y1 + y2) / 2.0])


class PoseDetector:
    """Wrapper around YOLOv8-pose with optional tracker."""
    DEFAULT_TRACKER = str(Path(__file__).resolve().parents[2] / "configs" / "botsort_reid.yaml")

    def __init__(self, model_name: str = "yolov8n-pose.pt", conf_thresh: float = 0.25, tracker_config: Optional[str] = None):
        from ultralytics import YOLO
        self.model = YOLO(model_name)
        self.conf_thresh = conf_thresh
        # BoT-SORT with ReID by default (see configs/botsort_reid.yaml). Pass "bytetrack.yaml"
        # or "botsort.yaml" to use the Ultralytics built-ins.
        self.tracker_config = tracker_config or self.DEFAULT_TRACKER

    def detect_frame(
        self,
        frame: np.ndarray,
        track: bool = True,
        tracker_config: Optional[str] = None
    ) -> List[PoseDetection]:
        """
        Runs pose estimation on a single BGR image.
        Returns a list of PoseDetection objects.
        """
        if track:
            results = self.model.track(
                frame,
                persist=True,
                tracker=tracker_config or self.tracker_config,
                conf=self.conf_thresh,
                verbose=False
            )
        else:
            results = self.model(frame, conf=self.conf_thresh, verbose=False)

        detections = []
        if len(results) == 0 or results[0].boxes is None:
            return detections

        res = results[0]
        boxes = res.boxes
        if len(boxes) == 0:
            return detections

        kpts_data = res.keypoints.data.cpu().numpy() if res.keypoints is not None else None
        boxes_xyxy = boxes.xyxy.cpu().numpy()
        confs = boxes.conf.cpu().numpy()
        track_ids = boxes.id.int().cpu().tolist() if boxes.id is not None else [None] * len(boxes)

        for i in range(len(boxes)):
            bbox = boxes_xyxy[i]
            bbox_conf = float(confs[i])
            tid = track_ids[i] if i < len(track_ids) else None

            if kpts_data is not None and i < len(kpts_data):
                kpts = kpts_data[i] # shape (17, 3) or (17, 2)
                if kpts.shape[1] == 2:
                    # Append dummy confidence of 1.0 if not provided
                    kpts = np.hstack([kpts, np.ones((17, 1))])
            else:
                kpts = np.zeros((17, 3))

            detections.append(PoseDetection(
                keypoints=kpts,
                bbox=bbox,
                bbox_conf=bbox_conf,
                track_id=tid
            ))

        return detections
