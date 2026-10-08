"""
Camera ego-motion estimation.

Kinematic derivatives are only meaningful if the camera is static. Per frame pair we track
sparse corners sampled outside the detected person boxes with Lucas-Kanade optical flow and
fit a similarity transform (translation + rotation + scale) with RANSAC. Bystanders and
dancers that were not masked become RANSAC outliers; a static camera gives a near-identity
transform with a high inlier fraction. The reported motion is the largest displacement the
transform induces at the image corners (so zoom and rotation count as motion), in
full-resolution pixels.
"""
from __future__ import annotations

from typing import Iterable, Optional, Tuple
import numpy as np
import cv2


class CameraMotionEstimator:
    def __init__(self, work_width: int = 640, max_corners: int = 500, min_points: int = 30, min_inlier_fraction: float = 0.3):
        self.work_width = work_width
        self.max_corners = max_corners
        self.min_points = min_points
        self.min_inlier_fraction = min_inlier_fraction
        self.prev_gray: Optional[np.ndarray] = None
        self.prev_mask: Optional[np.ndarray] = None
        self.scale = 1.0
        # Similarity transform (2x3, full-resolution px) mapping frame t-1 coordinates to frame t;
        # NaN when not measurable. Used by run_features.py to compensate dancer motion.
        self.last_M: np.ndarray = np.full((2, 3), np.nan)

    def _prepare(self, frame_bgr: np.ndarray, boxes: Iterable[np.ndarray]) -> Tuple[np.ndarray, np.ndarray]:
        h, w = frame_bgr.shape[:2]
        self.scale = w / float(self.work_width) if w > self.work_width else 1.0
        small = cv2.resize(frame_bgr, (int(round(w / self.scale)), int(round(h / self.scale)))) if self.scale != 1.0 else frame_bgr
        gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
        mask = np.full(gray.shape, 255, dtype=np.uint8)
        pad = int(0.05 * max(gray.shape))
        for b in boxes:
            b = np.asarray(b, dtype=float)
            if not np.all(np.isfinite(b)):
                continue
            x1, y1, x2, y2 = (b / self.scale).astype(int)
            cv2.rectangle(mask, (max(0, x1 - pad), max(0, y1 - pad)), (min(mask.shape[1] - 1, x2 + pad), min(mask.shape[0] - 1, y2 + pad)), 0, -1)
        return gray, mask

    def step(self, frame_bgr: np.ndarray, boxes: Iterable[np.ndarray]) -> Tuple[float, int]:
        """Returns (global motion in full-res px, number of RANSAC inliers). NaN when not measurable."""
        gray, mask = self._prepare(frame_bgr, boxes)
        result, n_in = float("nan"), 0
        self.last_M = np.full((2, 3), np.nan)
        if self.prev_gray is not None:
            joint = cv2.bitwise_and(mask, self.prev_mask) if self.prev_mask is not None else mask
            p0 = cv2.goodFeaturesToTrack(self.prev_gray, maxCorners=self.max_corners, qualityLevel=0.01, minDistance=7, mask=joint)
            if p0 is not None and len(p0) >= self.min_points:
                p1, st, _ = cv2.calcOpticalFlowPyrLK(self.prev_gray, gray, p0, None, winSize=(21, 21), maxLevel=3)
                ok = st.reshape(-1) == 1
                if ok.sum() >= self.min_points:
                    a, b = p0.reshape(-1, 2)[ok], p1.reshape(-1, 2)[ok]
                    M, inl = cv2.estimateAffinePartial2D(a, b, method=cv2.RANSAC, ransacReprojThreshold=1.0, maxIters=500)
                    if M is not None and inl is not None:
                        n_in = int(inl.sum())
                        if n_in >= self.min_points and n_in / ok.sum() >= self.min_inlier_fraction:
                            h, w = gray.shape
                            corners = np.array([[0, 0], [w, 0], [0, h], [w, h]], float)
                            moved = corners @ M[:, :2].T + M[:, 2]
                            result = float(np.max(np.linalg.norm(moved - corners, axis=1)) * self.scale)
                            # rescale the transform to full-resolution pixels: x_full = s * x_small
                            Mf = M.copy(); Mf[:, 2] *= self.scale
                            self.last_M = Mf
        self.prev_gray, self.prev_mask = gray, mask
        return result, n_in


def summarize_camera_motion(motion_px: np.ndarray, frame_width: int, thresh_frac_width: float = 0.003, max_moving_fraction: float = 0.05) -> dict:
    """A frame pair 'moves' if the global transform displaces an image corner by more than 0.3% of
    frame width (3.8 px at 1280). A video is static if at most 5% of measured frame pairs move."""
    m = np.asarray(motion_px, dtype=float)
    measured = np.isfinite(m)
    thr = thresh_frac_width * frame_width
    moving = measured & (m > thr)
    frac = float(moving.sum() / max(1, measured.sum()))
    return {
        "frames_measured": int(measured.sum()),
        "threshold_px": float(thr),
        "median_motion_px": float(np.nanmedian(m)) if measured.any() else None,
        "p95_motion_px": float(np.nanpercentile(m[measured], 95)) if measured.any() else None,
        "moving_fraction": frac,
        "camera_static": bool(measured.sum() > 0 and frac <= max_moving_fraction),
    }
