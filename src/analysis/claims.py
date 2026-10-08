"""
Within-video statistical tests for the thesis hypotheses.

Every test here is designed so that between-video confounds (camera distance, resolution,
dancer size, style) cannot produce the effect: comparisons are made *inside* each video and
then combined across videos (sign test / Wilcoxon on per-video effects, and a mixed-effects
model with video as a random intercept).

H1  "State-dependent smoothness": windows in which the dancers are in contact have different
    smoothness (SPARC, LDLJ, jerk in body units) than windows without contact.
H2  "Momentum transfer": in contact windows, KE-transfer correlation (d/dt KE_A vs d/dt KE_B)
    is negative more often than in surrogate data.
H3  "Coupling": the peak cross-correlation between the dancers' speeds exceeds the circular
    shift null (surrogate test).
"""
from __future__ import annotations

from typing import Dict, Any, List
import numpy as np
import pandas as pd
from scipy import stats


def per_video_contrast(windows: pd.DataFrame, metric: str, contact_col: str = "contact_fraction",
                       hi: float = 0.8, lo: float = 0.2, min_windows: int = 5) -> pd.DataFrame:
    """For each video: median metric in contact windows (contact_fraction >= hi) minus
    median in no-contact windows (<= lo), using both dancers. NaN metrics are ignored."""
    rows = []
    for vid, w in windows.groupby("video"):
        c = w[w[contact_col] >= hi]; n = w[w[contact_col] <= lo]
        vals_c = pd.concat([c[f"{metric}_A"], c[f"{metric}_B"]]).dropna()
        vals_n = pd.concat([n[f"{metric}_A"], n[f"{metric}_B"]]).dropna()
        if len(vals_c) >= min_windows and len(vals_n) >= min_windows:
            rows.append({"video": vid, "n_contact": len(vals_c), "n_free": len(vals_n),
                         "median_contact": vals_c.median(), "median_free": vals_n.median(),
                         "diff": vals_c.median() - vals_n.median(),
                         "cliffs_delta": cliffs_delta(vals_c.to_numpy(), vals_n.to_numpy())})
    return pd.DataFrame(rows)


def cliffs_delta(a: np.ndarray, b: np.ndarray) -> float:
    """Effect size in [-1, 1]: P(a > b) - P(a < b). Scale-free, robust."""
    a, b = np.asarray(a), np.asarray(b)
    if len(a) == 0 or len(b) == 0:
        return float("nan")
    gt = (a[:, None] > b[None, :]).mean(); lt = (a[:, None] < b[None, :]).mean()
    return float(gt - lt)


def combine_across_videos(pv: pd.DataFrame) -> Dict[str, Any]:
    """Sign test + Wilcoxon on per-video differences. Each video is one observation."""
    d = pv["diff"].dropna().to_numpy()
    if len(d) < 3:
        return {"n_videos": int(len(d)), "note": "fewer than 3 videos"}
    n_pos = int((d > 0).sum()); n_neg = int((d < 0).sum())
    sign_p = float(stats.binomtest(n_pos, n_pos + n_neg, 0.5).pvalue) if n_pos + n_neg > 0 else float("nan")
    try:
        w_p = float(stats.wilcoxon(d).pvalue)
    except ValueError:
        w_p = float("nan")
    return {"n_videos": int(len(d)), "videos_positive": n_pos, "videos_negative": n_neg, "median_diff": float(np.median(d)),
            "median_cliffs_delta": float(pv["cliffs_delta"].median()), "sign_test_p": sign_p, "wilcoxon_p": w_p}


def mixed_model(windows: pd.DataFrame, metric: str, contact_col: str = "contact_fraction") -> Dict[str, Any]:
    """Within-group estimator: metric ~ contact with a fixed effect per (video, dancer) group,
    i.e. both variables demeaned inside each group, OLS on the residuals, cluster-robust standard
    errors by group. This is the fixed-effects counterpart of `y ~ contact + (1|group)`; it cannot
    be driven by between-video differences and does not depend on a random-effects fit converging."""
    try:
        import statsmodels.api as sm
    except ImportError:
        return {"note": "statsmodels not installed"}
    long = pd.concat([windows[["video", contact_col, f"{metric}_A"]].rename(columns={f"{metric}_A": "y"}).assign(dancer="A"),
                      windows[["video", contact_col, f"{metric}_B"]].rename(columns={f"{metric}_B": "y"}).assign(dancer="B")])
    long = long.dropna(subset=["y", contact_col])
    long = long[(long[contact_col] >= 0.8) | (long[contact_col] <= 0.2)].copy()
    long["contact"] = (long[contact_col] >= 0.8).astype(float)
    long["group"] = long["video"] + "_" + long["dancer"]
    # keep groups that have both states
    ok = long.groupby("group")["contact"].transform(lambda c: 0 < c.mean() < 1)
    long = long[ok]
    if long.group.nunique() < 3 or len(long) < 50:
        return {"note": "not enough groups with both states", "n_obs": int(len(long))}
    yd = long["y"] - long.groupby("group")["y"].transform("mean")
    xd = long["contact"] - long.groupby("group")["contact"].transform("mean")
    m = sm.OLS(yd.to_numpy(), xd.to_numpy()[:, None]).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(long["group"])[0]})
    return {"estimator": "within-group OLS, cluster-robust SE", "n_obs": int(len(long)), "n_groups": int(long.group.nunique()),
            "beta_contact": float(m.params[0]), "se": float(m.bse[0]), "p": float(m.pvalues[0]),
            "grand_mean": float(long["y"].mean())}


def noise_floor_table(videos: pd.DataFrame) -> pd.DataFrame:
    v = videos.copy()
    v["jerk_over_noise_floor"] = v["median_jerk_A_u"] / v["noise_floor_A_u"]
    return v[["video", "unit", "scale_A_px", "jitter_A_px", "noise_floor_A_u", "median_jerk_A_u", "jerk_over_noise_floor", "camera_static", "included"]]


def ke_transfer_summary(windows: pd.DataFrame, contact_col: str = "contact_fraction") -> pd.DataFrame:
    rows = []
    for vid, w in windows.groupby("video"):
        c = w[w[contact_col] >= 0.8]["ke_transfer_r"].dropna(); n = w[w[contact_col] <= 0.2]["ke_transfer_r"].dropna()
        if len(c) >= 5 and len(n) >= 5:
            rows.append({"video": vid, "n_contact": len(c), "n_free": len(n), "median_r_contact": c.median(), "median_r_free": n.median(),
                         "frac_negative_contact": float((c < -0.2).mean()), "frac_negative_free": float((n < -0.2).mean())})
    return pd.DataFrame(rows)


def coupling_by_state(frames: pd.DataFrame, fps: float, n_surrogates: int = 100, min_frames: int = 600) -> Dict[str, Any]:
    """Cross-correlation of speeds restricted to frames WITHOUT contact (and, separately, with contact).
    While in contact two bodies move as one, so correlation there is the null expectation; the
    no-contact test is the one that speaks to anticipation / 'physical listening'. Frames are masked
    (NaN) and compute_xcorr drops them jointly; the surrogate null is built the same way."""
    from src.analysis.coordination import CrossCorrelationAnalysis as C
    out = {}
    a = frames["torso_A_speed_u"].to_numpy(dtype=float); b = frames["torso_B_speed_u"].to_numpy(dtype=float)
    cs = frames["contact_state"].to_numpy(dtype=float) if "contact_state" in frames else np.full(len(a), np.nan)
    for name, mask in (("no_contact", cs == 0.0), ("contact", cs == 1.0)):
        aa, bb = a.copy(), b.copy(); aa[~mask] = np.nan; bb[~mask] = np.nan
        n = int(np.isfinite(aa).sum() & np.isfinite(bb).sum()) if False else int((np.isfinite(aa) & np.isfinite(bb)).sum())
        if n < min_frames:
            out[name] = {"n_frames": n, "note": "too few frames"}; continue
        _, _, lag, r = C.compute_xcorr(aa, bb, fps, 2.0)
        s = C.surrogate_test(aa, bb, fps, 2.0, n_surrogates=n_surrogates)
        out[name] = {"n_frames": n, "peak_lag_s": float(lag), "peak_r": float(r), "null_95": s["null_95"], "p": s["p_value"]}
    return out
