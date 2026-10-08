"""
Smoothness and coupling metrics taken from the motor-control / dance-analysis literature.

All metrics here are *dimensionless* (invariant to movement amplitude and pixel scale),
so they can be compared across videos recorded at different resolutions and camera
distances. Raw pixel jerk / kinetic energy cannot.

References
----------
- Hogan & Sternad (2009). Sensitivity of smoothness measures to movement duration,
  amplitude, and arrests. J. Motor Behavior.  -> LDLJ
- Balasubramanian, Melendez-Calderon, Roby-Brami & Burdet (2015). On the analysis of
  movement smoothness. J. NeuroEngineering and Rehabilitation.  -> SPARC
"""
from __future__ import annotations

import numpy as np
from scipy.signal import savgol_filter


def smooth_positions(xy: np.ndarray, fs: float, window_s: float = 0.3, poly: int = 3) -> np.ndarray:
    """Savitzky-Golay smoothing of an (N, 2) trajectory. Pose jitter otherwise dominates jerk."""
    win = max(poly + 2, int(round(window_s * fs)) | 1)  # odd, > poly
    if len(xy) <= win:
        return xy
    return savgol_filter(xy, win, poly, axis=0)


def velocity(xy: np.ndarray, fs: float) -> np.ndarray:
    return np.gradient(xy, 1.0 / fs, axis=0)


def ldlj(vel: np.ndarray, fs: float) -> float:
    """Log Dimensionless Jerk (velocity-based). Higher (closer to 0) = smoother.

    LDLJ = -ln( T^3 / v_peak^2 * integral |d^2 v / dt^2|^2 dt )
    """
    dt = 1.0 / fs
    n = len(vel)
    if n < 5:
        return np.nan
    T = n * dt
    speed = np.linalg.norm(vel, axis=1)
    vpeak = speed.max()
    if vpeak <= 1e-9:
        return np.nan
    jerk = np.gradient(np.gradient(vel, dt, axis=0), dt, axis=0)
    integral = np.sum(np.linalg.norm(jerk, axis=1) ** 2) * dt
    if integral <= 0:
        return np.nan
    return float(-np.log((T ** 3 / vpeak ** 2) * integral))


def sparc(speed: np.ndarray, fs: float, padlevel: int = 4, fc: float = 6.0, amp_th: float = 0.05) -> float:
    """Spectral Arc Length of a speed profile. Higher (closer to 0) = smoother.

    fc defaults to 6 Hz (below Nyquist of ~25-30 fps pose data; human gross movement < 6 Hz).
    """
    if len(speed) < 8 or np.allclose(speed, 0):
        return np.nan
    nfft = int(2 ** (np.ceil(np.log2(len(speed))) + padlevel))
    f = np.arange(0, fs, fs / nfft)
    Mf = np.abs(np.fft.fft(speed, nfft))
    Mf = Mf / Mf.max()
    sel = f <= fc
    f_sel, Mf_sel = f[sel], Mf[sel]
    idx = np.nonzero(Mf_sel >= amp_th)[0]
    if len(idx) < 2:
        return np.nan
    f_sel = f_sel[idx[0]: idx[-1] + 1]
    Mf_sel = Mf_sel[idx[0]: idx[-1] + 1]
    df = np.diff(f_sel) / (f_sel[-1] - f_sel[0])
    return float(-np.sum(np.sqrt(df ** 2 + np.diff(Mf_sel) ** 2)))


def ke_transfer_r(speed_a: np.ndarray, speed_b: np.ndarray, fs: float) -> float:
    """Pearson r between d(KE_A)/dt and d(KE_B)/dt (equal mass assumed, so KE ~ v^2).

    Negative r = one dancer decelerates while the other accelerates -> momentum hand-off.
    Positive r = both speed up / slow down together -> co-moving as one unit.
    Scale-invariant because it is a correlation.
    """
    dka = np.gradient(speed_a ** 2, 1.0 / fs)
    dkb = np.gradient(speed_b ** 2, 1.0 / fs)
    if np.std(dka) < 1e-9 or np.std(dkb) < 1e-9:
        return np.nan
    return float(np.corrcoef(dka, dkb)[0, 1])
