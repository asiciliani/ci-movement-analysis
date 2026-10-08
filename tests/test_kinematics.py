"""Synthetic tests that pin down the behaviours the audit found broken. Run: .venv/bin/python -m pytest tests -q"""
import numpy as np
import pandas as pd
from src.features.kinematics import (differentiate_runs, dancer_kinematics, jerk_noise_floor, fill_small_gaps,
                                     build_frame_table, build_window_table, remove_teleports)
from src.features.smoothness import sparc, ldlj
from src.analysis.coordination import CrossCorrelationAnalysis

FPS = 30.0


def test_no_derivatives_across_gaps():
    t = np.arange(600) / FPS
    x = 100 * np.sin(2 * np.pi * 0.5 * t); y = np.zeros_like(x)
    x[200:260] = np.nan  # 2 s dropout, far longer than max_fill
    d = differentiate_runs(x, y, FPS)
    assert np.all(np.isnan(d["jx"][200:260]))
    assert np.all(np.isnan(d["jx"][195:200])) and np.all(np.isnan(d["jx"][260:265]))  # edges trimmed
    assert np.isfinite(d["jx"][100]) and np.isfinite(d["jx"][400])


def test_small_gap_filled_and_flagged():
    x = np.arange(100, dtype=float); x[50:52] = np.nan
    xf, filled = fill_small_gaps(x, 2)
    assert np.allclose(xf[50:52], [50, 51]) and filled[50:52].all() and filled.sum() == 2
    x[10:14] = np.nan
    xf, filled = fill_small_gaps(x, 2)
    assert np.isnan(xf[10:14]).all()


def test_jerk_of_clean_sinusoid_matches_theory():
    t = np.arange(900) / FPS; A, w = 100.0, 2 * np.pi * 0.5
    d = differentiate_runs(A * np.sin(w * t), np.zeros_like(t), FPS)
    jx = d["jx"][100:-100]
    assert abs(np.nanmax(np.abs(jx)) - A * w ** 3) / (A * w ** 3) < 0.05


def test_noise_floor_matches_simulation():
    rng = np.random.default_rng(0)
    sigma = 1.0
    d = differentiate_runs(500 + rng.normal(0, sigma, 5000), 500 + rng.normal(0, sigma, 5000), FPS)
    j = np.hypot(d["jx"], d["jy"])
    assert abs(np.nanmean(j) - jerk_noise_floor(sigma, FPS)) / jerk_noise_floor(sigma, FPS) < 0.1


def test_scale_invariance_of_calibrated_units():
    t = np.arange(900) / FPS
    base = np.column_stack([100 * np.sin(2 * np.pi * 0.5 * t), 50 * np.cos(2 * np.pi * 0.7 * t)])
    k1 = dancer_kinematics(base, FPS, scale_px=50.0)
    k2 = dancer_kinematics(base * 3, FPS, scale_px=150.0)
    assert np.allclose(np.nanmedian(k1["jerk"] / 50.0), np.nanmedian(k2["jerk"] / 150.0), rtol=1e-6)


def test_teleport_removed_not_clipped():
    x = np.arange(100, dtype=float); y = np.zeros(100); x[60] += 500
    xr, yr, n = remove_teleports(x, y, 10.0)
    assert n >= 1 and np.isnan(xr[60])


def test_xcorr_lag_sign_and_surrogate():
    rng = np.random.default_rng(1)
    a = np.convolve(rng.normal(size=3000), np.ones(15) / 15, mode="same")
    b = np.roll(a, 15) + 0.3 * rng.normal(size=3000)  # A precedes B by 0.5 s
    _, _, lag, r = CrossCorrelationAnalysis.compute_xcorr(a, b, FPS, 2.0)
    assert abs(lag - 0.5) < 0.05 and r > 0.5
    s = CrossCorrelationAnalysis.surrogate_test(a, b, FPS, 2.0, n_surrogates=50)
    assert s["p_value"] < 0.05
    s2 = CrossCorrelationAnalysis.surrogate_test(a, rng.normal(size=3000), FPS, 2.0, n_surrogates=50)
    assert s2["p_value"] > 0.05


def test_sparc_dimensionless():
    t = np.arange(300) / FPS
    v = np.exp(-((t - 5) ** 2) / 2)
    assert abs(sparc(v, FPS) - sparc(v * 1000, FPS)) < 1e-9
    assert abs(ldlj(np.column_stack([v, v]), FPS) - ldlj(np.column_stack([v, v]) * 1000, FPS)) < 1e-6


def test_frame_and_window_tables_build():
    n = 900; t = np.arange(n) / FPS
    pos = {}
    for lab, off in (("A", 0), ("B", 60)):
        xy = np.column_stack([300 + off + 80 * np.sin(2 * np.pi * 0.4 * t), 300 + 40 * np.cos(2 * np.pi * 0.4 * t)])
        for part in ("torso", "pelvis", "body"):
            pos[f"{part}_{lab}"] = xy + (0 if part == "torso" else 30)
    present = np.ones((n, 2), bool)
    cmd = np.full(n, 10.0); cmd[400:] = 200.0
    df, info = build_frame_table(pos, present, FPS, 640, 480, 60.0, 60.0, "bl", contact_min_dist=cmd)
    assert "torso_A_jerk_u" in df and df["contact_state"].iloc[100] == 1.0 and df["contact_state"].iloc[800] == 0.0
    w = build_window_table(df, FPS)
    assert len(w) > 10 and w["sparc_A"].notna().mean() > 0.8


def test_camera_compensation_removes_pan():
    from src.features.kinematics import compensate_camera
    n = 300; t = np.arange(n) / FPS
    true = np.column_stack([200 + 50 * np.sin(2 * np.pi * 0.5 * t), 300 + np.zeros(n)])
    pan = np.cumsum(np.full(n, 3.0))  # camera pans 3 px/frame to the right -> content shifts left
    observed = true.copy(); observed[:, 0] -= pan
    M = np.zeros((n, 2, 3)); M[:, 0, 0] = 1; M[:, 1, 1] = 1; M[:, 0, 2] = -3.0  # frame t-1 -> t: x' = x - 3
    q, info = compensate_camera(observed, M)
    assert info["compensated_fraction"] > 0.99
    assert np.allclose(np.diff(q[:, 0]), np.diff(true[:, 0]), atol=1e-6)
