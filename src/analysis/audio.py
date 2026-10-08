"""
Audio envelope aligned to video frames, as a covariate for the music confound: two dancers who
both move with the music would correlate at lag 0 without attending to each other. Uses ffmpeg
only (no audio libraries). Note that many public clips have a soundtrack added in editing; then
the audio is not what the dancers heard and the control is uninformative (reported as such).
"""
from __future__ import annotations

import subprocess
from typing import Optional
import numpy as np

SR = 8000


def load_mono(video_path: str, sr: int = SR) -> Optional[np.ndarray]:
    try:
        raw = subprocess.run(["ffmpeg", "-v", "quiet", "-i", video_path, "-vn", "-ac", "1", "-ar", str(sr), "-f", "s16le", "-"],
                             capture_output=True, timeout=600).stdout
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None
    if len(raw) < sr:
        return None
    return np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0


def frame_envelopes(audio: np.ndarray, fps: float, n_frames: int, sr: int = SR):
    """Per video frame: log RMS energy and spectral-flux onset strength (half-wave rectified)."""
    hop = sr / fps; rms = np.full(n_frames, np.nan); flux = np.full(n_frames, np.nan); prev = None
    win = int(round(hop)); w = np.hanning(win)
    for i in range(n_frames):
        s = int(round(i * hop)); seg = audio[s: s + win]
        if len(seg) < win:
            break
        rms[i] = np.log(np.sqrt(np.mean(seg ** 2)) + 1e-6)
        mag = np.abs(np.fft.rfft(seg * w))
        if prev is not None:
            flux[i] = np.maximum(mag - prev, 0).sum()
        prev = mag
    if np.nanstd(rms) < 1e-3:   # silent / constant track
        return None, None
    return rms, flux
