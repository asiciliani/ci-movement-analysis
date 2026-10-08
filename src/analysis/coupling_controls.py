"""
Controls for the coupling result (H3 / H3b). Each function answers one alternative explanation
for "the two dancers' speeds are correlated":

  circular-shift null    the series are autocorrelated, so some |r| is expected by chance
  local-shift null       only slow co-modulation (both speed up during a lively section, e.g. the
                         music) -> shifts of 3-10 s keep that but break moment-to-moment alignment
  pseudo-pairs           generic movement statistics of CI -> dancer A of one clip vs dancer B of
                         another clip (different source)
  frequency bands        shared keypoint jitter / compression artifacts live at high frequency;
                         body-level coupling should appear at < 1.5 Hz
  camera partialling     residual ego-motion after compensation moves both dancers at once
  distance dose-response keypoint mixing between overlapping bodies -> coupling must survive when the
                         dancers are >= 1-2 body lengths apart

All correlations are gap-aware: for lag k, sample t of A is paired with sample t+k of B on the
original timeline and only pairs where both are finite are used (no concatenation across gaps).
Positive lag = A leads B.
"""
from __future__ import annotations

from typing import Dict, Optional, Sequence
import numpy as np
from scipy.signal import butter, sosfiltfilt, fftconvolve


def lagged_corr(a: np.ndarray, b: np.ndarray, max_lag: int, min_pairs: int = 50) -> np.ndarray:
    """Pearson r(A_t, B_{t+k}) for k in [-max_lag, max_lag], each lag on its own valid pairs."""
    # All per-lag sums over jointly valid pairs via FFT cross-correlations (exact, O(n log n)).
    n = len(a)
    ma, mb = np.isfinite(a).astype(float), np.isfinite(b).astype(float)
    x, y = np.where(ma > 0, a, 0.0), np.where(mb > 0, b, 0.0)
    mu = (np.nansum(a) / max(ma.sum(), 1), np.nansum(b) / max(mb.sum(), 1))   # centre first for numerical stability
    x, y = (x - mu[0]) * ma, (y - mu[1]) * mb

    def xc(u, v):  # c[k] = sum_t u[t] v[t+k], k = -max_lag..max_lag
        c = fftconvolve(v, u[::-1], mode="full")[n - 1 - max_lag: n + max_lag]
        return c
    N = xc(ma, mb); Sx = xc(x, mb); Sy = xc(ma, y); Sxx = xc(x * x, mb); Syy = xc(ma, y * y); Sxy = xc(x, y)
    with np.errstate(invalid="ignore", divide="ignore"):
        N = np.round(N)
        cov = Sxy - Sx * Sy / N; vx = Sxx - Sx ** 2 / N; vy = Syy - Sy ** 2 / N
        r = cov / np.sqrt(vx * vy)
    r[(N < min_pairs) | ~(vx > 1e-12) | ~(vy > 1e-12)] = np.nan
    return np.clip(r, -1, 1)


def peak(a: np.ndarray, b: np.ndarray, fps: float, max_lag_s: float = 2.0):
    L = int(round(max_lag_s * fps)); c = lagged_corr(a, b, L)
    if not np.isfinite(c).any():
        return float("nan"), float("nan"), float("nan")
    i = int(np.nanargmax(np.abs(c)))
    return float((i - L) / fps), float(c[i]), float(c[L])  # peak lag [s], peak r, r at lag 0


def shift_null(a: np.ndarray, b: np.ndarray, fps: float, mask: Optional[np.ndarray] = None, max_lag_s: float = 2.0,
               shift_range_s: Sequence[float] = (5.0, None), n: int = 200, seed: int = 0) -> Dict[str, float]:
    """Peak |r| of (A, roll(B, k)) with |k| in shift_range_s. B is rolled on the full timeline and then
    the original mask is applied, so every surrogate uses exactly the frames of the observed test."""
    rng = np.random.default_rng(seed); T = len(a)
    m = np.ones(T, bool) if mask is None else mask.astype(bool)
    aa = np.where(m, a, np.nan)
    _, r_obs, r0 = peak(aa, np.where(m, b, np.nan), fps, max_lag_s)
    lo = int(shift_range_s[0] * fps); hi = int(shift_range_s[1] * fps) if shift_range_s[1] else T - lo
    if hi <= lo or not np.isfinite(r_obs):
        return {"r_obs": r_obs, "p": float("nan"), "z": float("nan"), "null_95": float("nan")}
    null = []
    for _ in range(n):
        k = int(rng.integers(lo, hi + 1)) * (1 if rng.random() < 0.5 else -1)
        null.append(abs(peak(aa, np.where(m, np.roll(b, k), np.nan), fps, max_lag_s)[1]))
    null = np.array([x for x in null if np.isfinite(x)])
    if len(null) < 20:
        return {"r_obs": r_obs, "p": float("nan"), "z": float("nan"), "null_95": float("nan")}
    return {"r_obs": r_obs, "r_lag0": r0, "p": float((np.sum(null >= abs(r_obs)) + 1) / (len(null) + 1)),
            "z": float((abs(r_obs) - null.mean()) / (null.std() + 1e-12)), "null_95": float(np.percentile(null, 95))}


def bandpass_runs(x: np.ndarray, fps: float, lo: Optional[float], hi: Optional[float], min_run_s: float = 4.0) -> np.ndarray:
    """Zero-phase Butterworth filter applied separately to each contiguous finite run (>= min_run_s)."""
    nyq = fps / 2
    if lo and hi:
        sos = butter(2, [lo / nyq, hi / nyq], btype="band", output="sos")
    elif hi:
        sos = butter(2, hi / nyq, btype="low", output="sos")
    else:
        sos = butter(2, lo / nyq, btype="high", output="sos")
    out = np.full(len(x), np.nan); f = np.isfinite(x)
    edges = np.flatnonzero(np.diff(np.r_[0, f.astype(int), 0]))
    for s, e in zip(edges[::2], edges[1::2]):
        if e - s >= int(min_run_s * fps):
            out[s:e] = sosfiltfilt(sos, x[s:e])
    return out


def partial_out(x: np.ndarray, covariates: Sequence[np.ndarray]) -> np.ndarray:
    """Residual of x after OLS on covariates (and intercept), on frames where all are finite."""
    X = np.column_stack([np.ones(len(x))] + list(covariates)); m = np.isfinite(x) & np.isfinite(X).all(1)
    out = np.full(len(x), np.nan)
    if m.sum() > X.shape[1] + 10:
        beta, *_ = np.linalg.lstsq(X[m], x[m], rcond=None); out[m] = x[m] - X[m] @ beta
    return out


def resample(x: np.ndarray, fps: float, target_fps: float = 25.0) -> np.ndarray:
    """Nearest-sample resampling onto a common time grid (keeps NaN), for pseudo-pairs across clips."""
    t = np.arange(0, len(x) / fps, 1 / target_fps)
    return x[np.minimum((t * fps).round().astype(int), len(x) - 1)]
