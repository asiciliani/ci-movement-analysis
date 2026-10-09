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


# ---------------------------------------------------------------------------------------------------
# Rolling point of contact: where on each body the contact is, in that body's own reference frame
# ---------------------------------------------------------------------------------------------------
ALL_SEGMENTS = [(r, a, b) for r, segs in SEGMENTS.items() for a, b in segs if a != b]


def _closest_points(p1, p2, q1, q2):
    """Approximate closest points between segments p1p2 and q1q2 (arrays (N,2)) by sampling 11 points
    on each segment; returns (point_on_p, point_on_q, distance)."""
    t = np.linspace(0, 1, 11)
    P = p1[:, None, :] + t[None, :, None] * (p2 - p1)[:, None, :]          # (N,11,2)
    Q = q1[:, None, :] + t[None, :, None] * (q2 - q1)[:, None, :]
    d = np.linalg.norm(P[:, :, None, :] - Q[:, None, :, :], axis=-1)        # (N,11,11)
    flat = d.reshape(len(d), -1).argmin(1); i, j = flat // 11, flat % 11
    n = np.arange(len(d))
    return P[n, i], Q[n, j], d[n, i, j]


def contact_points(kA: np.ndarray, kB: np.ndarray):
    """Per frame: the closest pair of points between any segment of A and any segment of B.
    Returns (ptA (N,2), ptB (N,2), dist_px (N,), regionA (N,), regionB (N,))."""
    N = len(kA); best = np.full(N, np.inf); pA = np.full((N, 2), np.nan); pB = np.full((N, 2), np.nan)
    rA = np.full(N, None, dtype=object); rB = np.full(N, None, dtype=object)
    for ra, a1, a2 in ALL_SEGMENTS:
        for rb, b1, b2 in ALL_SEGMENTS:
            ok = (kA[:, [a1, a2], 2] >= CONF).all(1) & (kB[:, [b1, b2], 2] >= CONF).all(1)
            if not ok.any():
                continue
            x, y, d = _closest_points(kA[ok, a1, :2], kA[ok, a2, :2], kB[ok, b1, :2], kB[ok, b2, :2])
            idx = np.flatnonzero(ok); better = d < best[idx]; ii = idx[better]
            best[ii] = d[better]; pA[ii] = x[better]; pB[ii] = y[better]; rA[ii] = ra; rB[ii] = rb
    best[~np.isfinite(best)] = np.nan
    return pA, pB, best, rA, rB


def body_frame(k: np.ndarray, pts: np.ndarray, scale) -> np.ndarray:
    """Express image points in the dancer's own frame: origin at the pelvis, +y along the trunk
    (pelvis -> shoulders), x perpendicular; units of body length. A point that stays at the same place
    on the body keeps the same coordinates however the body moves or turns in the image."""
    hp = (k[:, 11, :2] + k[:, 12, :2]) / 2; sh = (k[:, 5, :2] + k[:, 6, :2]) / 2
    ok = (k[:, [5, 6, 11, 12], 2] >= CONF).all(1)
    u = sh - hp; L = np.linalg.norm(u, axis=1, keepdims=True); u = u / np.maximum(L, 1e-6)
    v = np.stack([u[:, 1], -u[:, 0]], axis=1)                        # perpendicular
    rel = pts - hp
    out = np.stack([np.einsum("ij,ij->i", rel, v), np.einsum("ij,ij->i", rel, u)], axis=1) / scale
    out[~ok] = np.nan
    return out


def contact_centroids(kA: np.ndarray, kB: np.ndarray, thresh_px: np.ndarray | float):
    """Stable contact location: the weighted mean of the closest points of ALL segment pairs closer than
    thresh_px (weight = thresh - d), instead of the single closest pair, whose argmin flips between
    neighbouring segments frame to frame. Also returns, per frame, the region of A and of B carrying the
    largest weight. Returns (cA (N,2), cB (N,2), regA, regB)."""
    N = len(kA); th = np.broadcast_to(np.asarray(thresh_px, float), (N,))
    sA = np.zeros((N, 2)); sB = np.zeros((N, 2)); W = np.zeros(N)
    wr_A = {r: np.zeros(N) for r in REGIONS}; wr_B = {r: np.zeros(N) for r in REGIONS}
    for ra, a1, a2 in ALL_SEGMENTS:
        for rb, b1, b2 in ALL_SEGMENTS:
            ok = (kA[:, [a1, a2], 2] >= CONF).all(1) & (kB[:, [b1, b2], 2] >= CONF).all(1)
            if not ok.any():
                continue
            idx = np.flatnonzero(ok)
            x, y, d = _closest_points(kA[idx, a1, :2], kA[idx, a2, :2], kB[idx, b1, :2], kB[idx, b2, :2])
            w = np.clip(th[idx] - d, 0, None)
            sA[idx] += w[:, None] * x; sB[idx] += w[:, None] * y; W[idx] += w
            wr_A[ra][idx] += w; wr_B[rb][idx] += w
    has = W > 0
    cA = np.full((N, 2), np.nan); cB = np.full((N, 2), np.nan)
    cA[has] = sA[has] / W[has, None]; cB[has] = sB[has] / W[has, None]
    MA = np.stack([wr_A[r] for r in REGIONS], 1); MB = np.stack([wr_B[r] for r in REGIONS], 1)
    regA = np.array([REGIONS[i] for i in MA.argmax(1)], dtype=object); regB = np.array([REGIONS[i] for i in MB.argmax(1)], dtype=object)
    regA[~has] = None; regB[~has] = None
    return cA, cB, regA, regB
