import numpy as np
from src.analysis.coupling_controls import lagged_corr, peak, shift_null, bandpass_runs, partial_out


def _ar1(n, phi=0.95, seed=0):
    rng = np.random.default_rng(seed); x = np.zeros(n)
    for t in range(1, n):
        x[t] = phi * x[t - 1] + rng.normal()
    return x


def test_lag_sign_convention_a_leads():
    a = _ar1(3000); b = np.roll(a, 10) + 0.1 * np.random.default_rng(1).normal(size=3000)  # B follows A by 10 frames
    lag, r, _ = peak(a, b, fps=25, max_lag_s=2)
    assert abs(lag - 0.4) < 1e-9 and r > 0.9


def test_gaps_are_not_concatenated():
    a = _ar1(2000); b = a.copy(); a[500:600] = np.nan
    c = lagged_corr(a, b, 5)
    assert np.isclose(c[5], 1.0)          # lag 0 is perfect despite the gap


def test_independent_series_not_significant():
    ps = [shift_null(_ar1(2500, seed=s), _ar1(2500, seed=s + 100), 25, n=100, seed=s)["p"] for s in range(20)]
    assert np.mean(np.array(ps) < 0.05) <= 0.2   # roughly nominal false-positive rate


def test_coupled_series_significant_and_mask_respected():
    a = _ar1(3000); b = 0.6 * a + 0.8 * _ar1(3000, seed=7)
    mask = np.zeros(3000, bool); mask[::2] = True
    s = shift_null(a, b, 25, mask=mask, n=100)
    assert s["p"] < 0.05


def test_bandpass_runs_and_partial_out():
    t = np.arange(2000) / 25; x = np.sin(2 * np.pi * 0.2 * t) + np.sin(2 * np.pi * 3 * t); x[1000:1010] = np.nan
    lo = bandpass_runs(x, 25, None, 1.0)
    assert np.isnan(lo[1005]) and np.nanstd(lo) < 0.9
    cam = np.random.default_rng(0).normal(size=2000); y = 2 * cam + 0.01 * np.random.default_rng(1).normal(size=2000)
    assert np.nanstd(partial_out(y, [cam])) < 0.05


def test_fft_lagged_corr_matches_bruteforce():
    rng = np.random.default_rng(3); a = _ar1(800); b = np.roll(a, 3) + rng.normal(size=800)
    a[rng.random(800) < 0.2] = np.nan; b[100:180] = np.nan
    c = lagged_corr(a, b, 10)
    for i, k in enumerate(range(-10, 11)):
        x, y = (a[: 800 - k], b[k:]) if k >= 0 else (a[-k:], b[: 800 + k])
        m = np.isfinite(x) & np.isfinite(y)
        assert np.isclose(c[i], np.corrcoef(x[m], y[m])[0, 1], atol=1e-8)
