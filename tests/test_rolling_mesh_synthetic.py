"""Sensitivity check for rolling_mesh: a synthetic 'hand' (a small patch of points 1 cm off the skin) slides
down a real moving dancer's back at a known speed, or stays on one spot. The tracker must report the travel
for the slide and none for the hold, whatever the dancer's own movement. Skipped without the SMPL-X files."""
from pathlib import Path
import numpy as np
import pytest

SEQ = Path("data_external/compas3d/smplx/Pair1/Pair1_song1_take1")
pytestmark = pytest.mark.skipif(not (SEQ.exists() and Path("data_external/smplx_models/models_lockedhead").exists()),
                                reason="needs CoMPAS3D SMPL-X params and the licensed model files")


def _run(slide: bool):
    import rolling_mesh as RM
    z = np.load(SEQ / "Pair1_song1_take1_leader.npz")
    V, rest, faces, keep, t = RM.meshes({k: (z[k][:900] if k in ("poses", "trans") else z[k]) for k in z.files}, RM.VERT_STEP)
    reg = RM.vertex_regions(faces)[keep]
    trunk = np.flatnonzero((reg == "trunk") & (rest[:, 2] < np.median(rest[reg == "trunk", 2])))        # back half (rest pose faces +z)
    order = trunk[np.argsort(-rest[trunk, 1])]                                                       # top to bottom
    top, bottom = rest[order[5]], rest[order[-5]]
    n = len(V); per_frame = []
    patch_rest = np.random.default_rng(0).normal(0, 0.01, (25, 3))                                   # the 'hand' on its own chart
    for k in range(n):
        target = top + (bottom - top) * (k / (n - 1) if slide else 0.3)
        near = trunk[np.argsort(np.linalg.norm(rest[trunk] - target, axis=1))[:6]]                   # skin vertices under the hand
        hand = V[k][near].mean(0) + patch_rest * 0.5                                                 # ~1 cm cloud on the posed skin
        per_frame.append(RM.frame_sites(V[k], hand, rest, patch_rest))
    tracks = [RM.summarise(tr) for tr in RM.track_sites(per_frame, t[:n], reg, np.array(["hand"] * len(patch_rest), dtype=object))]
    tracks = [x for x in tracks if x]
    return tracks, float(np.linalg.norm(bottom - top))


def test_hold_is_grip():
    tracks, _ = _run(slide=False)
    assert tracks and max(x["travel_leader_m"] for x in tracks) < 0.05
    assert all(x["label"] == "GRIP" for x in tracks)


def test_slide_is_detected_with_its_length():
    tracks, length = _run(slide=True)
    longest = max(tracks, key=lambda x: x["dur_s"])
    assert longest["label"] == "SLIDE/ROLL"
    assert longest["dur_s"] > 0.8 * 9 and abs(longest["travel_leader_m"] - length) < 0.25 * length
    assert longest["travel_follower_m"] < 0.05
