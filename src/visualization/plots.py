"""
Visualization module for Contact Improvisation movement analysis.
Generates multi-panel time-series figures, 2D trajectory maps,
lagged cross-correlation plots, and manual annotation overlays.
"""

from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.patches import Patch


# Consistent color palette
COLOR_A = "#008080"       # Teal for Dancer A
COLOR_B = "#E66100"       # Amber / Vermillion for Dancer B
COLOR_DIST = "#5E3C99"    # Purple for distance
COLOR_DIR = "#2B83BA"     # Blue for directional similarity
COLOR_CONTACT = "#D7191C" # Crimson for contact proxy

# Phase colors for manual annotations
PHASE_COLORS = {
    "separate": "#E0E0E0",
    "approaching": "#B2DF8A",
    "contact": "#FDBF6F",
    "shared_weight": "#FB9A99",
    "transition": "#CAB2D6",
    "default": "#ECE7F2"
}


def _add_annotation_spans(ax: plt.Axes, annotation_mgr: Any, ymin: float = 0.0, ymax: float = 1.0):
    """Draws colored vertical spans for annotated phases across the time axis."""
    if annotation_mgr is None or not hasattr(annotation_mgr, "intervals") or not annotation_mgr.intervals:
        return

    added_labels = set()
    for inv in annotation_mgr.intervals:
        label = inv["label"]
        color = PHASE_COLORS.get(label.lower(), PHASE_COLORS["default"])
        legend_label = label if label not in added_labels else None
        added_labels.add(label)

        ax.axvspan(
            inv["start_time"],
            inv["end_time"],
            alpha=0.25,
            color=color,
            label=legend_label,
            zorder=0
        )


def _clean_path_for_plot(x: pd.Series, y: pd.Series, max_step: float = 90.0) -> Tuple[np.ndarray, np.ndarray]:
    """Inserts NaNs into path where jump exceeds max_step to prevent spurious slash lines."""
    px = x.to_numpy().copy()
    py = y.to_numpy().copy()
    for i in range(1, len(px)):
        if not (np.isnan(px[i]) or np.isnan(px[i-1]) or np.isnan(py[i]) or np.isnan(py[i-1])):
            if np.sqrt((px[i] - px[i-1])**2 + (py[i] - py[i-1])**2) > max_step:
                px[i] = np.nan
                py[i] = np.nan
    return px, py


def plot_trajectories(
    df: pd.DataFrame,
    title: str = "Dancer Trajectories (Torso Center)",
    save_path: Optional[str] = None
) -> plt.Figure:
    """Plots 2D spatial paths of Dancer A and Dancer B."""
    fig, ax = plt.subplots(figsize=(8, 7))

    # Dancer A path
    clean_Ax, clean_Ay = _clean_path_for_plot(df["torso_A_x"], df["torso_A_y"])
    ax.plot(
        clean_Ax, clean_Ay,
        color=COLOR_A, alpha=0.75, linewidth=2, label="Dancer A Path"
    )
    # Start and End markers
    valid_A = df.dropna(subset=["torso_A_x", "torso_A_y"])
    if not valid_A.empty:
        first_A = valid_A.iloc[0]
        last_A = valid_A.iloc[-1]
        ax.scatter(first_A["torso_A_x"], first_A["torso_A_y"], color=COLOR_A, s=100, marker="o", edgecolors="black", label="Dancer A Start")
        ax.scatter(last_A["torso_A_x"], last_A["torso_A_y"], color=COLOR_A, s=120, marker="X", edgecolors="black", label="Dancer A End")

    # Dancer B path
    clean_Bx, clean_By = _clean_path_for_plot(df["torso_B_x"], df["torso_B_y"])
    ax.plot(
        clean_Bx, clean_By,
        color=COLOR_B, alpha=0.75, linewidth=2, label="Dancer B Path"
    )
    valid_B = df.dropna(subset=["torso_B_x", "torso_B_y"])
    if not valid_B.empty:
        first_B = valid_B.iloc[0]
        last_B = valid_B.iloc[-1]
        ax.scatter(first_B["torso_B_x"], first_B["torso_B_y"], color=COLOR_B, s=100, marker="o", edgecolors="black", label="Dancer B Start")
        ax.scatter(last_B["torso_B_x"], last_B["torso_B_y"], color=COLOR_B, s=120, marker="X", edgecolors="black", label="Dancer B End")

    ax.set_title(title, fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("X coordinate (pixels)", fontsize=11)
    ax.set_ylabel("Y coordinate (pixels)", fontsize=11)
    ax.invert_yaxis() # Image coordinate convention (0,0 at top-left)
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend(loc="upper right", framealpha=0.9, fontsize=9)
    plt.tight_layout()

    if save_path:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_path, dpi=300)

    return fig


def plot_movement_dynamics_dashboard(
    df: pd.DataFrame,
    global_xcorr: Tuple[np.ndarray, np.ndarray, float, float],
    rolling_xcorr: Optional[Dict[str, Any]] = None,
    annotation_mgr: Optional[Any] = None,
    title: str = "Contact Improvisation Interpersonal Movement Analysis",
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Comprehensive multi-panel time-series dashboard displaying:
    1. Inter-dancer distances (Torso & Pelvis) + annotations
    2. Velocity magnitudes (|v_A| vs |v_B|)
    3. Directional coordination (Cosine similarity)
    4. Contact proxy (Minimum keypoint distance)
    5. Global time-lagged cross-correlation
    6. Rolling time-lagged cross-correlation heatmap
    """
    has_rolling = rolling_xcorr is not None and rolling_xcorr["xcorr_matrix"].size > 0
    n_rows = 6 if has_rolling else 5

    fig = plt.figure(figsize=(14, 2.8 * n_rows))
    gs = fig.add_gridspec(n_rows, 1, hspace=0.35)

    time_sec = df["time_sec"]

    # 1. Inter-Dancer Distances
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.plot(time_sec, df["dist_torso"], color=COLOR_DIST, linewidth=2, label="Torso Distance")
    ax1.plot(time_sec, df["dist_pelvis"], color="#9970AB", linewidth=1.5, linestyle="--", label="Pelvis Distance")
    _add_annotation_spans(ax1, annotation_mgr)
    ax1.set_ylabel("Distance (px)", fontsize=10, fontweight="bold")
    ax1.set_title(title, fontsize=14, fontweight="bold", pad=15)
    ax1.legend(loc="upper right", fontsize=9, framealpha=0.9)
    ax1.grid(True, linestyle=":", alpha=0.5)

    # 2. Velocity / Speed
    ax2 = fig.add_subplot(gs[1, 0], sharex=ax1)
    ax2.plot(time_sec, df["torso_A_speed"], color=COLOR_A, linewidth=1.8, label="Dancer A Speed |v_A|")
    ax2.plot(time_sec, df["torso_B_speed"], color=COLOR_B, linewidth=1.8, label="Dancer B Speed |v_B|")
    _add_annotation_spans(ax2, annotation_mgr)
    ax2.set_ylabel("Speed (px/s)", fontsize=10, fontweight="bold")
    # Robust y-limit scaling to ignore rare flicker spikes
    all_speeds = np.concatenate([df["torso_A_speed"].dropna().to_numpy(), df["torso_B_speed"].dropna().to_numpy()])
    if len(all_speeds) > 0:
        max_spd = float(np.percentile(all_speeds, 98.5)) * 1.3
        ax2.set_ylim(0, max(250.0, max_spd))
    ax2.legend(loc="upper right", fontsize=9, framealpha=0.9)
    ax2.grid(True, linestyle=":", alpha=0.5)

    # 3. Directional Coordination (Cosine Similarity)
    ax3 = fig.add_subplot(gs[2, 0], sharex=ax1)
    ax3.plot(time_sec, df["dir_sim_torso"], color=COLOR_DIR, linewidth=1.5, alpha=0.7, label="Instantaneous Cosine Sim")
    # Smoothed trend
    trend = df["dir_sim_torso"].rolling(window=15, min_periods=3, center=True).mean()
    ax3.plot(time_sec, trend, color="#08519C", linewidth=2.2, label="Smoothed Trend")
    ax3.axhline(0, color="gray", linestyle="--", alpha=0.6)
    ax3.axhline(1, color="green", linestyle=":", alpha=0.4, label="Same direction (+1)")
    ax3.axhline(-1, color="red", linestyle=":", alpha=0.4, label="Opposite direction (-1)")
    _add_annotation_spans(ax3, annotation_mgr)
    ax3.set_ylim(-1.1, 1.1)
    ax3.set_ylabel("Cosine Sim", fontsize=10, fontweight="bold")
    ax3.legend(loc="upper right", fontsize=8, framealpha=0.9, ncol=2)
    ax3.grid(True, linestyle=":", alpha=0.5)

    # 4. Contact Proxy Proximity
    ax4 = fig.add_subplot(gs[3, 0], sharex=ax1)
    ax4.plot(time_sec, df["contact_proxy_min_dist"], color=COLOR_CONTACT, linewidth=2, label="Min Keypoint Distance")
    if "contact_proxy_hand_torso" in df.columns:
        ax4.plot(time_sec, df["contact_proxy_hand_torso"], color="#FDAE61", linewidth=1.5, linestyle="--", label="Hand-to-Torso Dist")
    _add_annotation_spans(ax4, annotation_mgr)
    ax4.set_ylabel("Proximity (px)", fontsize=10, fontweight="bold")
    ax4.legend(loc="upper right", fontsize=9, framealpha=0.9)
    ax4.grid(True, linestyle=":", alpha=0.5)

    # 5. Global Lagged Cross-Correlation
    ax5 = fig.add_subplot(gs[4, 0])
    lags, corr, peak_lag, peak_val = global_xcorr
    ax5.plot(lags, corr, color="#252525", linewidth=2, label="Global Cross-Correlation R(τ)")
    ax5.axvline(0, color="black", linestyle="--", alpha=0.5, label="Simultaneous (τ = 0)")
    ax5.axvline(peak_lag, color="red", linestyle="-", linewidth=1.8, label=f"Peak Lag: {peak_lag:+.2f}s (R={peak_val:.2f})")
    ax5.scatter([peak_lag], [peak_val], color="red", s=60, zorder=5)

    # Interpretation text
    lead_text = "Simultaneous Coupling"
    if peak_lag > 0.05:
        lead_text = f"Dancer A precedes Dancer B by {peak_lag:.2f}s"
    elif peak_lag < -0.05:
        lead_text = f"Dancer B precedes Dancer A by {abs(peak_lag):.2f}s"

    ax5.set_title(f"Time-Lagged Coordination: {lead_text}", fontsize=11, fontweight="bold")
    ax5.set_xlabel("Time Lag τ (seconds)   [Negative: B leads | Positive: A leads]", fontsize=10)
    ax5.set_ylabel("Correlation R(τ)", fontsize=10, fontweight="bold")
    ax5.set_xlim(min(lags), max(lags))
    ax5.set_ylim(-1.0, 1.0)
    ax5.legend(loc="upper right", fontsize=8, framealpha=0.9)
    ax5.grid(True, linestyle=":", alpha=0.5)

    # 6. Optional Rolling Cross-Correlation Heatmap
    if has_rolling:
        ax6 = fig.add_subplot(gs[5, 0], sharex=ax1)
        tc = rolling_xcorr["time_centers"]
        lg = rolling_xcorr["lags_sec"]
        mat = rolling_xcorr["xcorr_matrix"]

        im = ax6.pcolormesh(
            tc, lg, mat,
            cmap="coolwarm", vmin=-1.0, vmax=1.0, shading="gouraud"
        )
        # Overlay rolling peak lag trajectory
        ax6.plot(tc, rolling_xcorr["peak_lags"], color="black", linewidth=1.5, linestyle="-", label="Dynamic Peak Lag")
        ax6.axhline(0, color="white", linestyle="--", alpha=0.7)
        ax6.set_ylabel("Lag τ (s)", fontsize=10, fontweight="bold")
        ax6.set_xlabel("Video Time (seconds)", fontsize=10, fontweight="bold")
        ax6.set_title("Rolling Lagged Coupling (Dynamic Precedence Heatmap)", fontsize=11, fontweight="bold")
        ax6.legend(loc="upper right", fontsize=8, framealpha=0.9)
        cbar = fig.colorbar(im, ax=ax6, orientation="vertical", pad=0.01)
        cbar.set_label("R(t, τ)", fontsize=9)
    else:
        ax4.set_xlabel("Video Time (seconds)", fontsize=10, fontweight="bold")

    plt.tight_layout()

    if save_path:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_path, dpi=300)

    return fig


def plot_phase_summary(
    df_summary: pd.DataFrame,
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Plots bar charts comparing mean kinematic metrics across manually annotated phases.
    Tests the question: Do computational measures change systematically across phases?
    """
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))

    phases = df_summary["phase"].tolist()
    colors = [PHASE_COLORS.get(p.lower(), "#999999") for p in phases]

    # 1. Mean Distance
    axes[0].bar(phases, df_summary["mean_dist_torso"], color=colors, edgecolor="black", alpha=0.85)
    axes[0].set_title("Mean Torso Distance by Phase", fontweight="bold", fontsize=11)
    axes[0].set_ylabel("Distance (pixels)", fontsize=10)
    axes[0].grid(axis="y", linestyle=":", alpha=0.6)

    # 2. Mean Speeds (Dancer A vs Dancer B)
    x = np.arange(len(phases))
    w = 0.35
    axes[1].bar(x - w/2, df_summary["mean_speed_A"], width=w, color=COLOR_A, label="Dancer A", edgecolor="black")
    axes[1].bar(x + w/2, df_summary["mean_speed_B"], width=w, color=COLOR_B, label="Dancer B", edgecolor="black")
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(phases)
    axes[1].set_title("Dancer Speeds by Phase", fontweight="bold", fontsize=11)
    axes[1].set_ylabel("Speed (px/s)", fontsize=10)
    axes[1].legend(fontsize=9)
    axes[1].grid(axis="y", linestyle=":", alpha=0.6)

    # 3. Directional Similarity
    axes[2].bar(phases, df_summary["mean_dir_similarity"], color=colors, edgecolor="black", alpha=0.85)
    axes[2].axhline(0, color="gray", linestyle="--")
    axes[2].set_ylim(-1, 1)
    axes[2].set_title("Directional Similarity by Phase", fontweight="bold", fontsize=11)
    axes[2].set_ylabel("Cosine Similarity", fontsize=10)
    axes[2].grid(axis="y", linestyle=":", alpha=0.6)

    plt.tight_layout()
    if save_path:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_path, dpi=300)

    return fig
