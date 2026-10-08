"""
Shape-type descriptors loosely inspired by Laban Movement Analysis (Shape: contraction/expansion).

NOTE: the former `calculate_effort_weight = jerk * kinetic_energy` was removed. It had units of
px^3/s^5, no mass term, and does not correspond to how Weight Effort is operationalised in the
automated-LMA literature (acceleration/deceleration peaks, mass-weighted energy). Smoothness
("Flow") is covered by SPARC / LDLJ in smoothness.py.
"""
from __future__ import annotations
import numpy as np


def contraction_index(kpts: np.ndarray, scale_px: float, conf_thresh: float = 0.3) -> np.ndarray:
    """(N,17,3) -> (N,) mean distance of confident keypoints to their centroid, in body lengths."""
    xy = kpts[:, :, :2].astype(float).copy()
    ok = kpts[:, :, 2] >= conf_thresh
    xy[~ok] = np.nan
    import warnings
    with np.errstate(all="ignore"), warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        cen = np.nanmean(xy, axis=1, keepdims=True)
        d = np.linalg.norm(xy - cen, axis=2)
        enough = ok.sum(axis=1) >= 5
        out = np.nanmean(d, axis=1) / scale_px
    out[~enough] = np.nan
    return out


def bounding_area(kpts: np.ndarray, scale_px: float, conf_thresh: float = 0.3) -> np.ndarray:
    xy = kpts[:, :, :2].astype(float).copy()
    ok = kpts[:, :, 2] >= conf_thresh
    xy[~ok] = np.nan
    import warnings
    with np.errstate(all="ignore"), warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        a = (np.nanmax(xy[:, :, 0], axis=1) - np.nanmin(xy[:, :, 0], axis=1)) * (np.nanmax(xy[:, :, 1], axis=1) - np.nanmin(xy[:, :, 1], axis=1))
    a = a / scale_px ** 2
    a[ok.sum(axis=1) < 5] = np.nan
    return a
