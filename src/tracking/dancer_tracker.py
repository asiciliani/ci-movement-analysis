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
from src.tracking.appearance import AppearanceModel, torso_histogram, separability


def _iou(a: np.ndarray, b: np.ndarray) -> float:
    x1, y1 = max(a[0], b[0]), max(a[1], b[1]); x2, y2 = min(a[2], b[2]), min(a[3], b[3])
    inter = max(0.0, x2 - x1) * max(0.0, y2 - y1)
    ua = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return float(inter / ua) if ua > 0 else 0.0


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
        # Diagnostics (reported in tracking_quality.json)
        self.last_track_id: Optional[int] = None
        self.n_id_switches: int = 0        # frames where the underlying tracker id changed
        self.n_dropouts: int = 0           # number of missing streaks started
        self.n_missing_frames: int = 0
        self.n_assigned_frames: int = 0
        self.appearance = AppearanceModel()

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

        self.n_assigned_frames += 1
        if detection.track_id is not None:
            self.associated_track_ids[detection.track_id] = (
                self.associated_track_ids.get(detection.track_id, 0) + 1
            )
            if self.last_track_id is not None and detection.track_id != self.last_track_id:
                self.n_id_switches += 1
            self.last_track_id = detection.track_id

    def mark_missing(self):
        if self.missing_streak == 0:
            self.n_dropouts += 1
        self.n_missing_frames += 1
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
        use_normalized: bool = False,
        appearance_weight: float = 0.0,
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
        self.n_frames: int = 0
        self.n_suspected_swaps: int = 0   # A and B exchanged their underlying tracker ids between consecutive frames
        self.n_extra_people_frames: int = 0  # frames with >2 candidate (foreground-sized) detections
        # Appearance term: cost += appearance_weight * (d_same - d_other) * max_match_distance.
        # 0 disables it. Set from run_tracking.py (default 0.5); only applied once both colour
        # models exist and are separable (distance between them > 0.2).
        self.appearance_weight = appearance_weight
        self.n_appearance_overrides: int = 0  # frames where appearance changed the geometric assignment

    @staticmethod
    def _bbox_area(det: PoseDetection) -> float:
        x1, y1, x2, y2 = det.bbox
        return float(max(0.0, (x2 - x1) * (y2 - y1)))

    def _initialize_dancers(self, detections: List[PoseDetection]) -> bool:
        """Initialize dancers on first frame with >= 2 detections, picking the 2 largest foreground people."""
        if len(detections) < 2:
            return False
        # Sort by bounding box area descending to get foreground dancers
        sorted_by_area = sorted(detections, key=self._bbox_area, reverse=True)
        top_two = sorted_by_area[:2]
        area_0 = self._bbox_area(top_two[0])
        area_1 = self._bbox_area(top_two[1])

        # Both must be substantial foreground detections, not a foreground dancer + distant spectator
        if area_0 > 0 and (area_1 / area_0 < 0.35):
            return False

        # Order top two by x-coordinate: left is Dancer A, right is Dancer B
        sorted_dets = sorted(top_two, key=lambda d: d.torso_center[0])
        self.dancer_A.update(sorted_dets[0])
        self.dancer_B.update(sorted_dets[1])
        self.initialized = True
        return True

    def step(
        self,
        detections: List[PoseDetection],
        dt: float = 1.0 / 30.0,
        frame: Optional[np.ndarray] = None,
    ) -> Tuple[Optional[PoseDetection], Optional[PoseDetection]]:
        """
        Assign detections in the current frame to Dancer A and Dancer B.
        Returns (det_A, det_B). Either can be None if not found/detected.
        """
        self.n_frames += 1
        if not self.initialized:
            if self._initialize_dancers(detections):
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
            # Retain if it matches known track ID or is at least 35% of foreground size
            if is_known_id or ref_area <= 0 or area >= 0.35 * ref_area:
                candidate_dets.append(det)

        if not candidate_dets:
            self.dancer_A.mark_missing()
            self.dancer_B.mark_missing()
            return None, None

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
            area = self._bbox_area(det)
            
            # Spatial distance cost
            cost_matrix[0, j] = np.linalg.norm(pos - pred_A)
            cost_matrix[1, j] = np.linalg.norm(pos - pred_B)
            
            # Bounding box area difference penalty (background people are much smaller/larger)
            if self.dancer_A.last_bbox_area > 0:
                area_ratio_A = max(area, self.dancer_A.last_bbox_area) / min(area, self.dancer_A.last_bbox_area)
                cost_matrix[0, j] += area_ratio_A * 10.0  # Add distance penalty for size mismatch
                
            if self.dancer_B.last_bbox_area > 0:
                area_ratio_B = max(area, self.dancer_B.last_bbox_area) / min(area, self.dancer_B.last_bbox_area)
                cost_matrix[1, j] += area_ratio_B * 10.0

            # Bonus affinity if detection matches historically assigned track_id
            if det.track_id is not None:
                if det.track_id in self.dancer_A.associated_track_ids:
                    cost_matrix[0, j] -= 40.0
                if det.track_id in self.dancer_B.associated_track_ids:
                    cost_matrix[1, j] -= 40.0

        # Appearance term (clothing colour), only when informative
        hists = [None] * len(candidate_dets)
        use_app = (self.appearance_weight > 0 and frame is not None and self.dancer_A.appearance.n >= 15
                   and self.dancer_B.appearance.n >= 15 and separability(self.dancer_A.appearance, self.dancer_B.appearance) > 0.2)
        geo_assign = None
        if use_app:
            r0, c0 = linear_sum_assignment(cost_matrix)
            geo_assign = set(zip(r0, c0))
            boxes = np.array([d.bbox for d in candidate_dets], dtype=float)
            for j, det in enumerate(candidate_dets):
                hists[j] = torso_histogram(frame, det.keypoints)
                if hists[j] is None:
                    continue
                # torso crops that overlap another candidate's box are contaminated: no appearance term
                if len(boxes) > 1 and max(_iou(boxes[j], boxes[k]) for k in range(len(boxes)) if k != j) > 0.3:
                    continue
                dA = self.dancer_A.appearance.distance(hists[j]); dB = self.dancer_B.appearance.distance(hists[j])
                if np.isfinite(dA) and np.isfinite(dB):
                    cost_matrix[0, j] += self.appearance_weight * (dA - dB) * self.max_match_distance
                    cost_matrix[1, j] += self.appearance_weight * (dB - dA) * self.max_match_distance
                    # hard gate: clothes clearly belong to the other dancer (or to nobody) -> forbid
                    if dA > 0.45 and dA > dB + 0.15:
                        cost_matrix[0, j] = 1e9
                    if dB > 0.45 and dB > dA + 0.15:
                        cost_matrix[1, j] = 1e9
                    if dA > 0.6 and dB > 0.6:   # looks like neither dancer (a bystander)
                        cost_matrix[0, j] = 1e9; cost_matrix[1, j] = 1e9
        elif frame is not None and self.appearance_weight > 0:
            for j, det in enumerate(candidate_dets):
                hists[j] = torso_histogram(frame, det.keypoints)

        row_ind, col_ind = linear_sum_assignment(cost_matrix)
        if geo_assign is not None and set(zip(row_ind, col_ind)) != geo_assign:
            self.n_appearance_overrides += 1

        assigned_A: Optional[PoseDetection] = None
        assigned_B: Optional[PoseDetection] = None

        hist_A = hist_B = None
        for r, c in zip(row_ind, col_ind):
            cost = cost_matrix[r, c]
            if cost < self.max_match_distance:
                if r == 0:
                    assigned_A = candidate_dets[c]; hist_A = hists[c]
                elif r == 1:
                    assigned_B = candidate_dets[c]; hist_B = hists[c]
        # Learn colours only when the two dancers are clearly apart (no shared pixels in the torso crops)
        if assigned_A is not None and assigned_B is not None and frame is not None:
            apart = np.linalg.norm(assigned_A.torso_center - assigned_B.torso_center) > 0.6 * max(
                assigned_A.bbox[3] - assigned_A.bbox[1], assigned_B.bbox[3] - assigned_B.bbox[1])
            if apart:
                self.dancer_A.appearance.update(hist_A); self.dancer_B.appearance.update(hist_B)

        # Swap diagnostic: if A takes B's previous id and B takes A's previous id, flag it.
        prev_A, prev_B = self.dancer_A.last_track_id, self.dancer_B.last_track_id
        if (assigned_A is not None and assigned_B is not None and prev_A is not None and prev_B is not None
                and assigned_A.track_id == prev_B and assigned_B.track_id == prev_A and prev_A != prev_B):
            self.n_suspected_swaps += 1
        if len(candidate_dets) > 2:
            self.n_extra_people_frames += 1

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


    def quality_report(self) -> Dict[str, object]:
        """Tracking diagnostics for the whole video. No ground truth: these are proxies, not accuracy."""
        n = max(1, self.n_frames)
        return {
            "n_frames": self.n_frames,
            "initialized": self.initialized,
            "detected_fraction_A": self.dancer_A.n_assigned_frames / n,
            "detected_fraction_B": self.dancer_B.n_assigned_frames / n,
            "dropouts_A": self.dancer_A.n_dropouts,
            "dropouts_B": self.dancer_B.n_dropouts,
            "tracker_id_switches_A": self.dancer_A.n_id_switches,
            "tracker_id_switches_B": self.dancer_B.n_id_switches,
            "suspected_identity_swaps": self.n_suspected_swaps,
            "frames_with_extra_people": self.n_extra_people_frames,
            "distinct_tracker_ids_A": len(self.dancer_A.associated_track_ids),
            "distinct_tracker_ids_B": len(self.dancer_B.associated_track_ids),
            "appearance_weight": self.appearance_weight,
            "appearance_separability": separability(self.dancer_A.appearance, self.dancer_B.appearance),
            "appearance_overrides": self.n_appearance_overrides,
        }
