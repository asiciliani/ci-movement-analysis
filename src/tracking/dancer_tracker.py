"""
Dancer Tracker module for Contact Improvisation.
Maintains continuous identity for Dancer A and Dancer B across occlusions,
close contact, and tracker ID reassignments.
"""

from typing import List, Dict, Optional, Tuple
import numpy as np
import pandas as pd
from scipy.optimize import linear_sum_assignment
from src.pose.pose_detector import PoseDetection, KEYPOINT_NAMES, KEYPOINT_INDEX


class DancerState:
    """Maintains trajectory and state for one tracked dancer."""
    def __init__(self, dancer_id: str, label: str):
        self.dancer_id = dancer_id      # e.g. "dancer_A" or "dancer_B"
        self.label = label              # "A" or "B"
        self.last_torso_pos: Optional[np.ndarray] = None
        self.last_pelvis_pos: Optional[np.ndarray] = None
        self.last_bbox_area: float = 0.0
        self.velocity: np.ndarray = np.zeros(2)
        self.missing_streak: int = 0
        self.associated_track_ids: Dict[int, int] = {} # track_id -> frequency count

    def update(self, detection: PoseDetection, dt: float = 1.0 / 30.0):
        new_torso = detection.torso_center
        new_pelvis = detection.pelvis_center
        x1, y1, x2, y2 = detection.bbox
        self.last_bbox_area = max(1.0, float((x2 - x1) * (y2 - y1)))

        if self.last_torso_pos is not None and dt > 0:
            self.velocity = (new_torso - self.last_torso_pos) / dt

        self.last_torso_pos = new_torso
        self.last_pelvis_pos = new_pelvis
        self.missing_streak = 0

        if detection.track_id is not None:
            self.associated_track_ids[detection.track_id] = (
                self.associated_track_ids.get(detection.track_id, 0) + 1
            )

    def mark_missing(self):
        self.missing_streak += 1
        # Dampen velocity during missing streak
        self.velocity *= 0.8


class TwoDancerTracker:
    """
    Maintains persistent tracking for exactly two dancers (Dancer A & Dancer B).
    Uses spatial proximity, motion continuity, and tracklet consistency.
    Filters out background bystanders/spectators by prioritizing foreground scale.
    """
    def __init__(
        self,
        max_match_distance: float = 350.0,
        use_normalized: bool = False
    ):
        """
        Args:
            max_match_distance: Max pixel (or normalized) distance to associate detection with dancer.
            use_normalized: If True, operates on [0, 1] normalized coordinates.
        """
        self.dancer_A = DancerState("dancer_A", "A")
        self.dancer_B = DancerState("dancer_B", "B")
        self.max_match_distance = max_match_distance
        self.use_normalized = use_normalized
        self.initialized = False

    @staticmethod
    def _bbox_area(det: PoseDetection) -> float:
        x1, y1, x2, y2 = det.bbox
        return float(max(0.0, (x2 - x1) * (y2 - y1)))

    def _initialize_dancers(self, detections: List[PoseDetection]):
        """Initialize dancers on first frame with >= 2 detections, picking the 2 largest foreground people."""
        # Sort by bounding box area descending to get foreground dancers
        sorted_by_area = sorted(detections, key=self._bbox_area, reverse=True)
        top_two = sorted_by_area[:2]

        # Order top two by x-coordinate: left is Dancer A, right is Dancer B
        sorted_dets = sorted(top_two, key=lambda d: d.torso_center[0])
        self.dancer_A.update(sorted_dets[0])
        self.dancer_B.update(sorted_dets[1])
        self.initialized = True

    def step(
        self,
        detections: List[PoseDetection],
        dt: float = 1.0 / 30.0
    ) -> Tuple[Optional[PoseDetection], Optional[PoseDetection]]:
        """
        Assign detections in the current frame to Dancer A and Dancer B.
        Returns (det_A, det_B). Either can be None if not found/detected.
        """
        if not self.initialized:
            if len(detections) >= 2:
                self._initialize_dancers(detections)
                sorted_by_area = sorted(detections, key=self._bbox_area, reverse=True)[:2]
                sorted_dets = sorted(sorted_by_area, key=lambda d: d.torso_center[0])
                return sorted_dets[0], sorted_dets[1]
            return None, None

        if len(detections) == 0:
            self.dancer_A.mark_missing()
            self.dancer_B.mark_missing()
            return None, None

        # Filter out background spectators if we have candidate dancers
        ref_area = max(self.dancer_A.last_bbox_area, self.dancer_B.last_bbox_area)
        candidate_dets = []
        for det in detections:
            area = self._bbox_area(det)
            is_known_id = (
                det.track_id is not None and (
                    det.track_id in self.dancer_A.associated_track_ids or
                    det.track_id in self.dancer_B.associated_track_ids
                )
            )
            # Retain if it matches known track ID or is at least 20% of foreground size
            if is_known_id or ref_area <= 0 or area >= 0.20 * ref_area:
                candidate_dets.append(det)

        if not candidate_dets:
            candidate_dets = detections

        # Predict positions using current velocity
        pred_A = (
            self.dancer_A.last_torso_pos + self.dancer_A.velocity * dt
            if self.dancer_A.last_torso_pos is not None else np.zeros(2)
        )
        pred_B = (
            self.dancer_B.last_torso_pos + self.dancer_B.velocity * dt
            if self.dancer_B.last_torso_pos is not None else np.zeros(2)
        )

        cost_matrix = np.zeros((2, len(candidate_dets)))
        for j, det in enumerate(candidate_dets):
            pos = det.torso_center
            cost_matrix[0, j] = np.linalg.norm(pos - pred_A)
            cost_matrix[1, j] = np.linalg.norm(pos - pred_B)

            # Bonus affinity if detection matches historically assigned track_id
            if det.track_id is not None:
                if det.track_id in self.dancer_A.associated_track_ids:
                    cost_matrix[0, j] -= 40.0
                if det.track_id in self.dancer_B.associated_track_ids:
                    cost_matrix[1, j] -= 40.0

        row_ind, col_ind = linear_sum_assignment(cost_matrix)

        assigned_A: Optional[PoseDetection] = None
        assigned_B: Optional[PoseDetection] = None

        for r, c in zip(row_ind, col_ind):
            cost = cost_matrix[r, c]
            if cost < self.max_match_distance:
                if r == 0:
                    assigned_A = candidate_dets[c]
                elif r == 1:
                    assigned_B = candidate_dets[c]

        # Update states
        if assigned_A is not None:
            self.dancer_A.update(assigned_A, dt)
        else:
            self.dancer_A.mark_missing()

        if assigned_B is not None:
            self.dancer_B.update(assigned_B, dt)
        else:
            self.dancer_B.mark_missing()

        return assigned_A, assigned_B
