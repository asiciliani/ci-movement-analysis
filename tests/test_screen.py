import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from screen_candidates import count_cuts


def test_count_cuts_isolated_spikes_only():
    rng = np.random.default_rng(0); d = np.abs(rng.normal(0.05, 0.02, 1500))   # 60 s of ordinary motion at 25 fps
    d[[300, 800, 1200]] = 0.9                                                    # three hard cuts
    d[10] = 0.9                                                                  # fade-in inside the first second: ignored
    d[1000:1040] = 0.7                                                           # sustained fast motion / whip pan: not a cut
    assert count_cuts(d, 25.0) == 3
