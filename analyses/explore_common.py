"""
Shared helpers for the three exploratory analyses of 13 Oct (momentum.py, dimensionality.py, novelty.py).

  ci_videos / salsa_videos   the 10 verified CI duets (outputs/grammar/per_clip.csv) and the CoMPAS3D salsa renders
                             tracked with the same video pipeline
  pelvis_kin                 camera-compensated pelvis velocity / acceleration of one dancer in body lengths per second
                             (identity-swap jumps removed, gap-aware Savitzky-Golay derivatives, rolling 5 s trunk length
                             as the unit, so zoom/dolly do not scale the signal)
  camera_covariates          per-frame camera translation speed and zoom rate from the saved similarity transforms
  bigand_coco / project_2d   Bigand et al. (2024) 23-marker mocap mapped to a COCO-17-like skeleton, and a 2-D virtual
                             camera with keypoint jitter (what the video pipeline would see)
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
from scipy.signal import savgol_filter

from src.io.tracks import load_tracks
from src.analysis import describe as D
from src.features.kinematics import remove_teleports, compensate_camera, fill_small_gaps, valid_runs


def ci_videos():
    return pd.read_csv("outputs/grammar/per_clip.csv").video.tolist()


def salsa_videos():
    return sorted(p.parent.name for p in Path("outputs").glob("salsa_*/salsa_*_tracks.npz") if p.parent.name == p.name.replace("_tracks.npz", ""))


def tracks(vid):
    return load_tracks(f"outputs/{vid}/{vid}_tracks.npz")


def sg_window(fps: float, sec: float = 0.5) -> int:
    w = int(round(sec * fps)) | 1
    return max(w, 5)


def rolling_trunk(k: np.ndarray, fps: float, win_s: float = 5.0) -> np.ndarray:
    """Per-frame trunk length (px): rolling median over win_s, gaps filled with the clip median."""
    L = D.trunk_len(k)
    w = int(win_s * fps)
    R = pd.Series(L).rolling(w, center=True, min_periods=max(w // 5, 3)).median().to_numpy()
    med = np.nanmedian(L)
    R = pd.Series(R).ffill().bfill().to_numpy()
    R[~np.isfinite(R)] = med
    return R


def sg_runs(x: np.ndarray, fps: float, win: int, deriv: int) -> np.ndarray:
    """Savitzky-Golay derivative (order 3) on contiguous finite runs of an (N,d) array; run edges (half window) NaN."""
    out = np.full_like(x, np.nan, dtype=float); ok = np.isfinite(x).all(1)
    h = win // 2
    for s, e in valid_runs(ok):
        if e - s < win + 2:
            continue
        out[s:e] = savgol_filter(x[s:e], win, 3, deriv=deriv, delta=1 / fps, axis=0, mode="interp")
        if deriv:
            out[s:s + h] = np.nan; out[e - h:e] = np.nan
    return out


def pelvis_kin(tr, j: int, fps: float, extra_noise_px: np.ndarray | None = None, rng=None, compensate: bool = True):
    """One dancer's pelvis kinematics in body lengths (rolling trunk length) per second.
    Returns dict: v (N,2), a (N,2), speed (N,), dke = d(speed^2)/dt (N,), jitter_bl (N,) smoothing residual,
    L (N,) trunk px."""
    k = tr.kpts[:, j].astype(float)
    p = D.pelvis(k); p[~tr.present[:, j]] = np.nan
    L = rolling_trunk(k, fps)
    x, y, _ = remove_teleports(p[:, 0], p[:, 1], 1.0 * np.nanmedian(L))       # identity swaps / glitches
    x, _ = fill_small_gaps(x, 2); y, _ = fill_small_gaps(y, 2)
    P = np.c_[x, y]
    if extra_noise_px is not None:
        rng = rng or np.random.default_rng(0)
        P = P + rng.normal(0, 1, P.shape) * np.nan_to_num(extra_noise_px)[:, None]
    if compensate and tr.camera_M is not None:
        P, _ = compensate_camera(P, tr.camera_M)
    w = sg_window(fps)
    sm = sg_runs(P, fps, w, 0); v = sg_runs(P, fps, w, 1); a = sg_runs(P, fps, w, 2)
    resid = np.linalg.norm(P - sm, axis=1) / L
    v = v / L[:, None]; a = a / L[:, None]
    speed = np.linalg.norm(v, axis=1)
    speed[speed > 15] = np.nan                                                  # implausible: tracking error
    dke = 2 * np.einsum("ij,ij->i", v, a); dke[~np.isfinite(speed)] = np.nan
    return dict(v=v, a=a, speed=speed, dke=dke, jitter_bl=resid, L=L)


def camera_covariates(tr, L_shared: np.ndarray, fps: float) -> list:
    """Per-frame nuisance regressors: camera translation speed (bl/s) and its change, zoom rate, shared log
    trunk length change rate (depth / dolly)."""
    M = tr.camera_M
    if M is None:
        return []
    t = np.linalg.norm(M[:, :, 2], axis=1) / L_shared * fps
    z = np.log(np.sqrt(np.abs(np.linalg.det(M[:, :, :2]))) + 1e-12) * fps
    ls = np.log(L_shared); dls = np.r_[0, np.diff(ls)] * fps
    cov = [t, np.r_[0, np.diff(t)] * fps, z, np.abs(z), dls, np.abs(dls)]
    return [np.where(np.isfinite(c), c, np.nan) for c in cov]


def normal_scores(x: np.ndarray) -> np.ndarray:
    """Rank-based inverse-normal transform of the finite values (robust to spikes)."""
    from scipy.stats import norm, rankdata
    out = np.full(len(x), np.nan); m = np.isfinite(x)
    if m.sum() > 10:
        out[m] = norm.ppf((rankdata(x[m]) - 0.5) / m.sum())
    return out


# ---------------------------------------------------------------- Bigand et al. 2024 (no contact, free dance)
BIG = Path("data_external/bigand2024")
BMARK = ['LB Head', 'LF Head', 'RF Head', 'RB Head', 'Sternum', 'L Shoulder', 'R Shoulder', 'L Elbow', 'L Wrist', 'L Hand', 'R Elbow',
         'R Wrist', 'R Hand', 'Pelvis', 'L Hip', 'R Hip', 'L Knee', 'L Ankle', 'L Foot', 'R Knee', 'R Ankle', 'R Foot', 'Thigh']
_bi = BMARK.index
# COCO-17 order: nose, l/r eye, l/r ear, l/r shoulder, l/r elbow, l/r wrist, l/r hip, l/r knee, l/r ankle
COCO_FROM_BIGAND = [("LF Head", "RF Head"), ("LF Head",), ("RF Head",), ("LB Head",), ("RB Head",), ("L Shoulder",), ("R Shoulder",),
                    ("L Elbow",), ("R Elbow",), ("L Wrist",), ("R Wrist",), ("L Hip",), ("R Hip",), ("L Knee",), ("R Knee",),
                    ("L Ankle",), ("R Ankle",)]


def bigand_load(dyad: int, trial: int, side: str):
    p = BIG / f"Dyad_{dyad:02d}/subj_{side}/tr{trial:02d}.npz"
    if not p.exists():
        return None
    return np.load(p)["X"].astype(float)          # (T, 23, 3) mm at 25 Hz


def bigand_up_axis(X):
    d = np.nanmedian(X[:, 0, :] - X[:, _bi('L Foot'), :], axis=0)
    return int(np.argmax(np.abs(d)))


def bigand_coco(X):
    """(T,23,3) -> (T,17,3) COCO-17-like 3-D skeleton (head markers stand in for nose/eyes/ears)."""
    return np.stack([np.mean([X[:, _bi(m)] for m in ms], axis=0) for ms in COCO_FROM_BIGAND], axis=1)


def project_2d(K3: np.ndarray, up: int, view_axis: int, jitter_bl: float, rng, trunk_mm: float):
    """Orthographic 2-D virtual camera looking along view_axis (horizontal), image y downward, in px where 1 bl = 100 px;
    plus isotropic keypoint jitter (bl). Returns (T,17,3) with conf 1 (NaN-marker frames conf 0)."""
    horiz = [k for k in range(3) if k not in (up, view_axis)][0]
    P = np.stack([K3[..., horiz], -K3[..., up]], axis=-1) / trunk_mm * 100.0
    P = P + rng.normal(0, jitter_bl * 100.0, P.shape)
    conf = np.isfinite(P).all(-1).astype(float)
    return np.concatenate([np.nan_to_num(P), conf[..., None]], axis=-1)
