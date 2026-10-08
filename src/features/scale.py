"""
Body-scale estimation.

Every pixel quantity in this project depends on how large the dancer is in the frame,
which depends on camera distance, lens and resolution. Without a metric calibration we
normalise by a per-dancer *body scale*: the trunk length (shoulder midpoint to hip
midpoint) in pixels, taken as the median over all frames where the four keypoints are
confidently detected. Units derived from it are called "body lengths" (bl).

If a floor-plane calibration is available (pixels per metre), prefer that.
"""
from __future__ import annotations

import numpy as np

from src.pose.pose_detector import KEYPOINT_INDEX

_LS, _RS = KEYPOINT_INDEX["left_shoulder"], KEYPOINT_INDEX["right_shoulder"]
_LH, _RH = KEYPOINT_INDEX["left_hip"], KEYPOINT_INDEX["right_hip"]


def trunk_length_per_frame(kpts: np.ndarray, conf_thresh: float = 0.3) -> np.ndarray:
    """kpts: (N, 17, 3). Returns (N,) trunk length in px, NaN where not measurable."""
    kpts = np.asarray(kpts, dtype=np.float64)
    conf_ok = (kpts[:, [_LS, _RS, _LH, _RH], 2] >= conf_thresh).all(axis=1)
    sh = (kpts[:, _LS, :2] + kpts[:, _RS, :2]) / 2.0
    hp = (kpts[:, _LH, :2] + kpts[:, _RH, :2]) / 2.0
    L = np.linalg.norm(sh - hp, axis=1)
    L[~conf_ok] = np.nan
    L[L <= 1.0] = np.nan
    return L


def body_scale(kpts: np.ndarray, bbox: np.ndarray | None = None, min_frames: int = 30) -> tuple[float, str]:
    """
    Median trunk length in px for one dancer across a video.
    Falls back to 0.3 * median bbox height when too few trunk measurements exist.
    Returns (scale_px, method).
    """
    L = trunk_length_per_frame(kpts)
    n = int(np.sum(np.isfinite(L)))
    if n >= min_frames:
        return float(np.nanmedian(L)), "trunk_median"
    if bbox is not None:
        h = bbox[:, 3] - bbox[:, 1]
        h = h[np.isfinite(h) & (h > 1)]
        if len(h) >= min_frames:
            return float(0.3 * np.median(h)), "bbox_height_0.3"
    return float("nan"), "unavailable"
