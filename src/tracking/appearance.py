"""
Clothing-colour appearance model for the two-dancer layer.

BoT-SORT's ReID works on whole-person crops and is tuned for pedestrians; in CI the two bodies
invert, fold and overlap, and its ids churn (dozens of switches per minute on the benchmark clip).
The two-dancer assignment layer therefore gets its own, much simpler appearance cue: an HSV colour
histogram of the torso region (shoulders-hips quadrilateral) of each dancer, learnt from the frames
where the dancers are clearly separated, and compared with every new detection.

Used in two places:
  * TwoDancerTracker cost matrix (optional): a detection whose torso colours match the other
    dancer's model is penalised.
  * audit_identity.py: an after-the-fact consistency check of saved tracks (how often does the
    dancer labelled A look like B?), which gives a swap-rate estimate without manual annotation,
    plus contact sheets for manual verification.
"""
from __future__ import annotations

from typing import Optional, Tuple
import numpy as np
import cv2

from src.pose.pose_detector import KEYPOINT_INDEX

I = KEYPOINT_INDEX
H_BINS, S_BINS = 16, 8


def torso_histogram(frame_bgr: np.ndarray, kpts: np.ndarray, conf_thresh: float = 0.3) -> Optional[np.ndarray]:
    """Normalised HSV (hue x saturation) histogram of the torso quadrilateral; None if torso not confident."""
    pts = kpts[[I["left_shoulder"], I["right_shoulder"], I["right_hip"], I["left_hip"]]]
    if (pts[:, 2] < conf_thresh).any():
        return None
    h, w = frame_bgr.shape[:2]
    poly = np.round(pts[:, :2]).astype(np.int32)
    x1, y1 = np.clip(poly.min(axis=0) - 2, 0, [w - 1, h - 1]); x2, y2 = np.clip(poly.max(axis=0) + 2, 0, [w - 1, h - 1])
    if x2 - x1 < 4 or y2 - y1 < 4:
        return None
    crop = frame_bgr[y1:y2, x1:x2]
    mask = np.zeros(crop.shape[:2], np.uint8)
    cv2.fillConvexPoly(mask, poly - [x1, y1], 255)
    if mask.sum() < 255 * 30:
        return None
    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
    hist = cv2.calcHist([hsv], [0, 1], mask, [H_BINS, S_BINS], [0, 180, 0, 256]).astype(np.float64)
    s = hist.sum()
    return (hist / s).ravel() if s > 0 else None


def hist_distance(a: np.ndarray, b: np.ndarray) -> float:
    """Bhattacharyya distance in [0, 1]; 0 = identical."""
    bc = float(np.sum(np.sqrt(a * b)))
    return float(np.sqrt(max(0.0, 1.0 - bc)))


class AppearanceModel:
    """Running colour model for one dancer: exponential average of torso histograms."""
    def __init__(self, alpha: float = 0.02):
        self.alpha = alpha
        self.hist: Optional[np.ndarray] = None
        self.n = 0

    def update(self, h: Optional[np.ndarray]):
        if h is None:
            return
        self.hist = h.copy() if self.hist is None else (1 - self.alpha) * self.hist + self.alpha * h
        self.n += 1

    def distance(self, h: Optional[np.ndarray]) -> float:
        if h is None or self.hist is None:
            return float("nan")
        return hist_distance(self.hist, h)


def separability(model_a: AppearanceModel, model_b: AppearanceModel) -> float:
    """Distance between the two dancers' colour models; below ~0.2 the cue is uninformative (same clothes)."""
    if model_a.hist is None or model_b.hist is None:
        return float("nan")
    return hist_distance(model_a.hist, model_b.hist)
