"""
Descriptive characterisation of a CI duet from 2-D keypoints (no causal claims).

Everything here is computed from the geometry of each frame (where one body is relative to the other in
the same image), so camera panning matters much less than for velocity-based coupling. Units are body
lengths (bl = the dancer's median trunk length). Image y grows downward.

  contact_regions   which body regions of A and B are closest when they touch (the "rolling point of contact")
  levels            standing / middle / floor, from pelvis height above the dancer's own lowest foot
  aerial_support    one dancer's feet clearly above the partner's feet while in contact (lift / carried weight)
  events            contiguous episodes (contact bouts, lifts, descents to the floor) with durations
  pose_features     camera-light per-frame descriptors (joint angles, trunk tilt, level) for a vocabulary
"""
from __future__ import annotations

from typing import Dict, List, Tuple
import numpy as np
import pandas as pd

KP = dict(nose=0, leye=1, reye=2, lear=3, rear=4, lsh=5, rsh=6, lel=7, rel=8, lwr=9, rwr=10, lhip=11, rhip=12,
          lkn=13, rkn=14, lank=15, rank=16)
# body segments (pairs of keypoints) grouped into regions; the head is a short segment ear-to-ear
SEGMENTS: Dict[str, List[Tuple[int, int]]] = {
    "head": [(3, 4), (0, 0)],
    "torso": [(5, 6), (11, 12), (5, 11), (6, 12)],
    "arm": [(5, 7), (6, 8)],
    "hand": [(7, 9), (8, 10)],
    "leg": [(11, 13), (12, 14)],
    "foot": [(13, 15), (14, 16)],
}
REGIONS = list(SEGMENTS)
CONF = 0.3


def trunk_len(k: np.ndarray) -> np.ndarray:
    """k: (N,17,3) -> (N,) shoulder-mid to hip-mid distance, NaN when not confident."""
    ok = (k[:, [5, 6, 11, 12], 2] >= CONF).all(1)
    L = np.linalg.norm((k[:, 5, :2] + k[:, 6, :2]) / 2 - (k[:, 11, :2] + k[:, 12, :2]) / 2, axis=1)
    L[~ok] = np.nan
    return L


def _seg_dist(p1, p2, q1, q2) -> np.ndarray:
    """Vectorised minimum distance between 2-D segments p1p2 and q1q2 (arrays (N,2))."""
    def pt_seg(p, a, b):
        ab = b - a; t = np.clip(np.einsum("ij,ij->i", p - a, ab) / np.maximum(np.einsum("ij,ij->i", ab, ab), 1e-9), 0, 1)
        return np.linalg.norm(p - (a + t[:, None] * ab), axis=1)
    return np.min(np.vstack([pt_seg(p1, q1, q2), pt_seg(p2, q1, q2), pt_seg(q1, p1, p2), pt_seg(q2, p1, p2)]), axis=0)


def contact_regions(kA: np.ndarray, kB: np.ndarray, scale: float, thresh_bl: float = 0.25):
    """Per frame: minimum distance (bl) between any body segments of A and B, and the (regionA, regionB)
    pair achieving it. Returns (dist_bl (N,), regA (N,) object, regB (N,) object, region_dist (N,6,6))."""
    N = len(kA); R = len(REGIONS)
    rd = np.full((N, R, R), np.inf)
    for i, ra in enumerate(REGIONS):
        for j, rb in enumerate(REGIONS):
            for a1, a2 in SEGMENTS[ra]:
                for b1, b2 in SEGMENTS[rb]:
                    ok = (kA[:, [a1, a2], 2] >= CONF).all(1) & (kB[:, [b1, b2], 2] >= CONF).all(1)
                    d = np.full(N, np.inf)
                    if ok.any():
                        d[ok] = _seg_dist(kA[ok, a1, :2], kA[ok, a2, :2], kB[ok, b1, :2], kB[ok, b2, :2]) / scale
                    rd[:, i, j] = np.minimum(rd[:, i, j], d)
    flat = rd.reshape(N, -1); idx = np.argmin(flat, axis=1); dmin = flat[np.arange(N), idx]
    regA = np.array([REGIONS[i // R] for i in idx], dtype=object); regB = np.array([REGIONS[i % R] for i in idx], dtype=object)
    none = ~np.isfinite(dmin)
    dmin[none] = np.nan; regA[none] = None; regB[none] = None
    return dmin, regA, regB, rd


def lowest_foot_y(k: np.ndarray) -> np.ndarray:
    y = np.where(k[:, [15, 16], 2] >= CONF, k[:, [15, 16], 1], np.nan)
    return np.nanmax(y, axis=1)   # image y grows downward: max = lowest point


def pelvis(k: np.ndarray) -> np.ndarray:
    p = (k[:, 11, :2] + k[:, 12, :2]) / 2
    p[~(k[:, [11, 12], 2] >= CONF).all(1)] = np.nan
    return p


def level(k: np.ndarray, scale: float) -> np.ndarray:
    """Pelvis height above the dancer's own lowest foot, in bl (standing ~1.6-2, crouch ~1, floor < 0.6)."""
    return (lowest_foot_y(k) - pelvis(k)[:, 1]) / scale


def level_class(lv: np.ndarray) -> np.ndarray:
    out = np.full(len(lv), None, dtype=object)
    out[lv >= 1.2] = "standing"; out[(lv >= 0.6) & (lv < 1.2)] = "middle"; out[lv < 0.6] = "floor"
    return out


def _knee_y(k):
    y = np.where(k[:, [13, 14], 2] >= CONF, k[:, [13, 14], 1], np.nan)
    return np.nanmean(y, axis=1)


def _x_extent(k):
    x = np.where(k[:, :, 2] >= CONF, k[:, :, 0], np.nan)
    return np.nanmin(x, axis=1), np.nanmax(x, axis=1)


def _shoulder_y(k):
    y = np.where(k[:, [5, 6], 2] >= CONF, k[:, [5, 6], 1], np.nan)
    return np.nanmean(y, axis=1)


def aerial_support(kA, kB, scaleA, scaleB, in_contact, margin_bl: float = 0.0):
    """+1 when A is carried by B, -1 for the reverse, 0 otherwise, NaN unknown. A is carried when, in
    contact, A's pelvis is above B's shoulder line (plus margin) and horizontally over B's body.
    Feet are not used: a carried dancer's legs often hang along the supporter's body and the pose
    model misplaces the ankles of inverted bodies (checked on lift frames). The horizontal-overlap
    condition rejects a dancer standing further from the camera."""
    pA, pB = pelvis(kA), pelvis(kB); shA, shB = _shoulder_y(kA), _shoulder_y(kB)
    xa0, xa1 = _x_extent(kA); xb0, xb1 = _x_extent(kB); s = (scaleA + scaleB) / 2
    a_up = ((shB - pA[:, 1]) / s > margin_bl) & (pA[:, 0] > xb0) & (pA[:, 0] < xb1)
    b_up = ((shA - pB[:, 1]) / s > margin_bl) & (pB[:, 0] > xa0) & (pB[:, 0] < xa1)
    out = np.zeros(len(pA)); out[a_up & in_contact] = 1; out[b_up & in_contact] = -1
    out[~np.isfinite(pA[:, 1]) | ~np.isfinite(pB[:, 1]) | ~np.isfinite(shA) | ~np.isfinite(shB)] = np.nan
    return out


def same_depth(kA, kB, scaleA, scaleB, max_gap_bl: float = 0.35):
    """2-D overlap is only plausible contact if both bodies are at a similar depth. When both stand
    (level >= 0.6) their feet must be at a similar image height; not applied on the floor or when one
    pelvis is above the other's shoulders (a lift lifts the feet too)."""
    s = (scaleA + scaleB) / 2
    gap = np.abs(lowest_foot_y(kA) - lowest_foot_y(kB)) / s
    upright = (level(kA, scaleA) >= 0.6) & (level(kB, scaleB) >= 0.6)
    high = (pelvis(kA)[:, 1] < _shoulder_y(kB)) | (pelvis(kB)[:, 1] < _shoulder_y(kA))
    return ~upright | high | ~np.isfinite(gap) | (gap < max_gap_bl)


def episodes(mask: np.ndarray, fps: float, min_s: float = 0.0, merge_gap_s: float = 0.2) -> List[Tuple[int, int]]:
    """Contiguous True runs (start, end_exclusive), gaps <= merge_gap merged, runs < min_s dropped."""
    m = np.asarray(mask, bool); edges = np.flatnonzero(np.diff(np.r_[0, m.astype(int), 0]))
    runs = list(zip(edges[::2], edges[1::2])); out = []
    for s, e in runs:
        if out and s - out[-1][1] <= merge_gap_s * fps:
            out[-1] = (out[-1][0], e)
        else:
            out.append((s, e))
    return [(s, e) for s, e in out if (e - s) >= min_s * fps]


def _angle(a, b, c):
    """Angle at b (degrees) of the triangle a-b-c, arrays (N,2)."""
    v1, v2 = a - b, c - b
    cos = np.einsum("ij,ij->i", v1, v2) / np.maximum(np.linalg.norm(v1, axis=1) * np.linalg.norm(v2, axis=1), 1e-9)
    return np.degrees(np.arccos(np.clip(cos, -1, 1)))


def pose_features(k: np.ndarray, scale: float) -> pd.DataFrame:
    """Per-frame descriptors that do not depend on image position or scale: joint angles, trunk tilt
    from vertical, head-below-pelvis (inversion), level, arm elevation."""
    P = k[:, :, :2]; ok = k[:, :, 2] >= CONF
    def pt(i):
        x = P[:, i].copy(); x[~ok[:, i]] = np.nan; return x
    sh = (pt(5) + pt(6)) / 2; hp = (pt(11) + pt(12)) / 2; head = pt(0)
    trunk = sh - hp
    tilt = np.degrees(np.arctan2(np.abs(trunk[:, 0]), -trunk[:, 1]))          # 0 upright, 90 horizontal, 180 inverted
    f = {
        "trunk_tilt": tilt,
        "inverted": ((head[:, 1] - hp[:, 1]) / scale),                      # > 0: head below pelvis
        "knee_L": _angle(pt(11), pt(13), pt(15)), "knee_R": _angle(pt(12), pt(14), pt(16)),
        "hip_L": _angle(pt(5), pt(11), pt(13)), "hip_R": _angle(pt(6), pt(12), pt(14)),
        "elbow_L": _angle(pt(5), pt(7), pt(9)), "elbow_R": _angle(pt(6), pt(8), pt(10)),
        "arm_up_L": (sh[:, 1] - pt(9)[:, 1]) / scale, "arm_up_R": (sh[:, 1] - pt(10)[:, 1]) / scale,
        "level": level(k, scale),
        "stance_width": np.abs(pt(15)[:, 0] - pt(16)[:, 0]) / scale,
    }
    return pd.DataFrame(f)
