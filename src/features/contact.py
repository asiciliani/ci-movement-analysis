"""Contact proxies from two 17-keypoint skeletons (px)."""
from __future__ import annotations
import numpy as np
from src.pose.pose_detector import KEYPOINT_INDEX


def min_keypoint_distance(kA: np.ndarray, kB: np.ndarray, conf_thresh: float = 0.3) -> np.ndarray:
    """kA, kB: (N,17,3). Minimum distance between any confident keypoint pair, per frame."""
    mA = kA[:, :, 2] >= conf_thresh
    mB = kB[:, :, 2] >= conf_thresh
    diffs = kA[:, :, None, :2] - kB[:, None, :, :2]
    d = np.linalg.norm(diffs, axis=-1)
    d[~(mA[:, :, None] & mB[:, None, :])] = np.nan
    with np.errstate(all="ignore"):
        return np.nanmin(d.reshape(len(d), -1), axis=1)


def hand_to_hip_distance(kA: np.ndarray, kB: np.ndarray, conf_thresh: float = 0.25) -> np.ndarray:
    def sd(p, q):
        d = np.linalg.norm(p[:, :2] - q[:, :2], axis=1)
        d[(p[:, 2] < conf_thresh) | (q[:, 2] < conf_thresh)] = np.nan
        return d
    I = KEYPOINT_INDEX
    c = np.column_stack([sd(kA[:, I["left_wrist"]], kB[:, I["left_hip"]]), sd(kA[:, I["right_wrist"]], kB[:, I["right_hip"]]),
                         sd(kB[:, I["left_wrist"]], kA[:, I["left_hip"]]), sd(kB[:, I["right_wrist"]], kA[:, I["right_hip"]])])
    with np.errstate(all="ignore"):
        return np.nanmin(c, axis=1)
