"""
Coordination analysis module for Contact Improvisation.
Provides time-lagged cross-correlation, rolling temporal coupling,
movement phase/rhythm analysis, and manual annotation integration.
"""

from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.signal import correlate, correlation_lags, hilbert, butter, filtfilt


class CrossCorrelationAnalysis:
    """Computes global and windowed time-lagged cross-correlation between dancers' signals."""

    @staticmethod
    def compute_xcorr(
        signal_A: np.ndarray,
        signal_B: np.ndarray,
        fps: float,
        max_lag_sec: float = 2.0
    ) -> Tuple[np.ndarray, np.ndarray, float, float]:
        """
        Computes normalized cross-correlation between two 1D movement signals.
        Returns:
            lags_sec: array of lag values in seconds (-max_lag to +max_lag)
            xcorr_norm: normalized correlation values in [-1, 1]
            peak_lag_sec: lag at which correlation is maximized
            peak_corr: correlation value at peak lag

        Lag Convention:
            Positive lag (tau > 0): Signal A precedes Signal B (B shifted forward to match A).
            Negative lag (tau < 0): Signal B precedes Signal A.
            tau ~ 0: Simultaneous / synchronized movement.
        """
        valid = ~(np.isnan(signal_A) | np.isnan(signal_B))
        s_A = signal_A[valid]
        s_B = signal_B[valid]

        if len(s_A) < int(fps * 1.0):
            # Not enough data
            return np.array([0]), np.array([0]), 0.0, 0.0

        # Mean-center and normalize
        s_A_norm = (s_A - np.mean(s_A))
        std_A = np.std(s_A)
        s_B_norm = (s_B - np.mean(s_B))
        std_B = np.std(s_B)

        if std_A < 1e-6 or std_B < 1e-6:
            return np.array([0]), np.array([0]), 0.0, 0.0

        s_A_norm = s_A_norm / std_A
        s_B_norm = s_B_norm / std_B

        n = len(s_A_norm)
        max_lag_frames = int(round(max_lag_sec * fps))

        corr = correlate(s_B_norm, s_A_norm, mode='full') / n
        lags_frames = correlation_lags(n, n, mode='full')

        # Crop to [-max_lag_frames, max_lag_frames]
        mask = (lags_frames >= -max_lag_frames) & (lags_frames <= max_lag_frames)
        lags_crop = lags_frames[mask]
        corr_crop = corr[mask]

        lags_sec = lags_crop / fps

        # Find peak correlation
        best_idx = np.argmax(np.abs(corr_crop))
        peak_lag_sec = float(lags_sec[best_idx])
        peak_corr = float(corr_crop[best_idx])

        return lags_sec, corr_crop, peak_lag_sec, peak_corr

    @staticmethod
    def compute_rolling_xcorr(
        signal_A: np.ndarray,
        signal_B: np.ndarray,
        fps: float,
        window_sec: float = 4.0,
        step_sec: float = 0.5,
        max_lag_sec: float = 2.0
    ) -> Dict[str, Any]:
        """
        Computes time-resolved (rolling) cross-correlation matrix.
        Reveals dynamic shifts in coupling and precedence over time.
        """
        n_samples = len(signal_A)
        window_frames = int(round(window_sec * fps))
        step_frames = max(1, int(round(step_sec * fps)))
        max_lag_frames = int(round(max_lag_sec * fps))

        time_centers = []
        xcorr_matrix = []
        peak_lags = []
        peak_corrs = []

        ref_lags = np.arange(-max_lag_frames, max_lag_frames + 1) / fps

        for start in range(0, n_samples - window_frames + 1, step_frames):
            end = start + window_frames
            center_t = (start + end) / 2.0 / fps

            seg_A = signal_A[start:end]
            seg_B = signal_B[start:end]

            lags_sec, corr, peak_lag, peak_val = CrossCorrelationAnalysis.compute_xcorr(
                seg_A, seg_B, fps, max_lag_sec
            )

            # Interpolate to common lag grid if lengths differ
            if len(lags_sec) > 1:
                corr_interp = np.interp(ref_lags, lags_sec, corr, left=0.0, right=0.0)
            else:
                corr_interp = np.zeros_like(ref_lags)

            time_centers.append(center_t)
            xcorr_matrix.append(corr_interp)
            peak_lags.append(peak_lag)
            peak_corrs.append(peak_val)

        return {
            "time_centers": np.array(time_centers),
            "lags_sec": ref_lags,
            "xcorr_matrix": np.array(xcorr_matrix).T if xcorr_matrix else np.empty((0, 0)),
            "peak_lags": np.array(peak_lags),
            "peak_corrs": np.array(peak_corrs),
        }


class PhaseAnalysis:
    """Simple rhythm / phase coordination metrics via Hilbert transform."""

    @staticmethod
    def compute_phase_coherence(
        signal_A: np.ndarray,
        signal_B: np.ndarray,
        fps: float,
        lowcut: float = 0.2,
        highcut: float = 2.5
    ) -> Tuple[np.ndarray, float]:
        """
        Filters movement signals (e.g. vertical torso position or speed oscillations)
        and extracts instantaneous phase via analytic signal (Hilbert transform).
        Returns:
            phase_diff: array of phase differences wrapped in [-pi, pi]
            plv: Phase Locking Value in [0, 1] (1 = perfect constant phase relation)
        """
        valid = ~(np.isnan(signal_A) | np.isnan(signal_B))
        s_A = signal_A.copy()
        s_B = signal_B.copy()
        s_A[~valid] = 0
        s_B[~valid] = 0

        # Bandpass filter for typical human movement rhythms (0.2 Hz - 2.5 Hz)
        nyq = 0.5 * fps
        low = max(0.01, lowcut / nyq)
        high = min(0.99, highcut / nyq)
        if high <= low:
            return np.zeros_like(signal_A), 0.0

        b, a = butter(2, [low, high], btype='band')
        filtered_A = filtfilt(b, a, s_A)
        filtered_B = filtfilt(b, a, s_B)

        phase_A = np.angle(hilbert(filtered_A))
        phase_B = np.angle(hilbert(filtered_B))

        phase_diff = np.mod(phase_A - phase_B + np.pi, 2 * np.pi) - np.pi
        phase_diff[~valid] = np.nan

        # Phase Locking Value (PLV)
        valid_diff = phase_diff[valid]
        if len(valid_diff) > 0:
            plv = float(np.abs(np.mean(np.exp(1j * valid_diff))))
        else:
            plv = 0.0

        return phase_diff, plv


class AnnotationManager:
    """Manages manual intervals and compares features across interaction phases."""

    def __init__(self, annotation_file: Optional[str] = None):
        self.intervals: List[Dict[str, Any]] = []
        if annotation_file is not None:
            self.load(annotation_file)

    @staticmethod
    def _parse_time_str(time_val: Any) -> float:
        """Parses MM:SS, M:SS or numeric float/int seconds into float seconds."""
        if isinstance(time_val, (int, float)):
            return float(time_val)
        time_str = str(time_val).strip()
        if ":" in time_str:
            parts = time_str.split(":")
            if len(parts) == 2:
                return float(parts[0]) * 60.0 + float(parts[1])
            elif len(parts) == 3:
                return float(parts[0]) * 3600.0 + float(parts[1]) * 60.0 + float(parts[2])
        return float(time_str)

    def load(self, filepath: str):
        """Loads annotations from CSV or JSON."""
        import json
        p = Path(filepath) if not isinstance(filepath, Path) else filepath
        if p.suffix.lower() == ".json":
            with open(p, "r") as f:
                data = json.load(f)
            self.intervals = [
                {
                    "start_time": self._parse_time_str(item["start_time"]),
                    "end_time": self._parse_time_str(item["end_time"]),
                    "label": item["label"],
                    "notes": item.get("notes", "")
                }
                for item in data
            ]
        else:
            # Default to CSV
            df = pd.read_csv(p)
            self.intervals = []
            for _, row in df.iterrows():
                self.intervals.append({
                    "start_time": self._parse_time_str(row["start_time"]),
                    "end_time": self._parse_time_str(row["end_time"]),
                    "label": str(row["label"]),
                    "notes": str(row.get("notes", ""))
                })

    def add_interval(self, start_time: Any, end_time: Any, label: str, notes: str = ""):
        self.intervals.append({
            "start_time": self._parse_time_str(start_time),
            "end_time": self._parse_time_str(end_time),
            "label": label,
            "notes": notes
        })

    def get_phase_at_time(self, t_sec: float) -> Optional[str]:
        for inv in self.intervals:
            if inv["start_time"] <= t_sec <= inv["end_time"]:
                return inv["label"]
        return None

    def summarize_phases(self, df_features: pd.DataFrame, fps: float) -> pd.DataFrame:
        """
        Computes summary statistics for each annotated phase to inspect whether
        computational measures change systematically across interaction phases.
        """
        summary_rows = []
        for inv in self.intervals:
            t0, t1, label = inv["start_time"], inv["end_time"], inv["label"]
            sub = df_features[(df_features["time_sec"] >= t0) & (df_features["time_sec"] <= t1)]

            if len(sub) == 0:
                continue

            # Compute cross-correlation peak in this interval
            s_A = sub["torso_A_speed"].to_numpy()
            s_B = sub["torso_B_speed"].to_numpy()
            _, _, peak_lag, peak_corr = CrossCorrelationAnalysis.compute_xcorr(s_A, s_B, fps, max_lag_sec=2.0)

            summary_rows.append({
                "phase": label,
                "start_sec": t0,
                "end_sec": t1,
                "duration_sec": t1 - t0,
                "mean_dist_torso": float(sub["dist_torso"].mean()),
                "median_dist_torso": float(sub["dist_torso"].median()),
                "mean_dist_pelvis": float(sub["dist_pelvis"].mean()),
                "mean_contact_proxy_min": float(sub["contact_proxy_min_dist"].mean()),
                "mean_speed_A": float(sub["torso_A_speed"].mean()),
                "mean_speed_B": float(sub["torso_B_speed"].mean()),
                "mean_dir_similarity": float(sub["dir_sim_torso"].mean()),
                "peak_lag_sec": peak_lag,
                "peak_xcorr": peak_corr,
                "notes": inv.get("notes", "")
            })

        return pd.DataFrame(summary_rows)
