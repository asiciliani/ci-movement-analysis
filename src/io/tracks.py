"""
Raw track storage. Stage 1 (run_tracking.py) writes one .npz per video with the
per-frame keypoints of the two dancers plus camera-motion; stage 2 (run_features.py)
rebuilds every feature from it without re-running the pose model.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, Optional
import numpy as np


@dataclass
class Tracks:
    kpts: np.ndarray          # (N, 2, 17, 3) float32, NaN where dancer absent
    bbox: np.ndarray          # (N, 2, 4)
    present: np.ndarray       # (N, 2) bool
    track_id: np.ndarray      # (N, 2) int, -1 when absent
    conf: np.ndarray          # (N, 2) float
    camera_motion: np.ndarray # (N,) float px, NaN when not measured
    meta: Dict[str, Any] = field(default_factory=dict)
    camera_M: Optional[np.ndarray] = None  # (N, 2, 3) similarity transform frame t-1 -> t, NaN when not measured

    @property
    def n_frames(self) -> int:
        return int(self.present.shape[0])


def save_tracks(path: str | Path, tr: Tracks) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        path,
        kpts=tr.kpts.astype(np.float32), bbox=tr.bbox.astype(np.float32), present=tr.present.astype(bool),
        track_id=tr.track_id.astype(np.int32), conf=tr.conf.astype(np.float32),
        camera_motion=tr.camera_motion.astype(np.float32), meta=json.dumps(tr.meta),
        camera_M=(tr.camera_M if tr.camera_M is not None else np.full((tr.n_frames, 2, 3), np.nan)).astype(np.float32),
    )


def load_tracks(path: str | Path) -> Tracks:
    z = np.load(Path(path), allow_pickle=False)
    return Tracks(
        kpts=z["kpts"], bbox=z["bbox"], present=z["present"], track_id=z["track_id"], conf=z["conf"],
        camera_motion=z["camera_motion"], meta=json.loads(str(z["meta"])),
        camera_M=z["camera_M"] if "camera_M" in z.files else None,
    )
