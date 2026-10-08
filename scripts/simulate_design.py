"""
Design simulation for the Phase-2 coupling study (DATA_COLLECTION_PROTOCOL.md §5).

Each simulated dyad is recorded in two blocks with the same camera/room/sound:
  S  solo-solo:      a = own_A + k*nuisance,              b = own_B + k*nuisance
  N  no-touch duet:  a = own_A + k*nuisance + c*shared,   b = own_B + k*nuisance + c*shared(t - lag)
own_* and shared are smooth AR(1) speed-like processes (25 fps); `nuisance` stands for everything
the two dancers share without interacting (camera-compensation residual, apparent-scale change,
music). k varies between dyads, c is the true coupling.

Outputs (outputs/design/):
  1. false-positive rate of the naive per-block circular-shift test on S blocks (no coupling) as the
     nuisance grows - the mechanism behind AUDIT 27;
  2. false-positive rate and power of the pre-registered contrast (Wilcoxon on N-S differences of
     peak |r| across dyads) vs number of dyads and coupling strength.
"""
from __future__ import annotations

import sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
from scipy.signal import lfilter

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.analysis.coupling_controls import peak, shift_null

FPS = 25.0
T = int(4 * 60 * FPS)        # 4-minute blocks
OUT = Path("outputs/design")


def ar1(n, phi, rng):
    return lfilter([np.sqrt(1 - phi ** 2)], [1, -phi], rng.normal(size=n))


def block(rng, k, c, lag=0, phi=0.97):
    nz = ar1(T, phi, rng); sh = ar1(T, phi, rng)
    a = ar1(T, phi, rng) + k * nz + c * sh
    b = ar1(T, phi, rng) + k * nz + c * np.roll(sh, lag)
    return a, b


def naive_false_positive(ks=(0.0, 0.3, 0.6), n_sim=60, seed=0):
    rng = np.random.default_rng(seed); rows = []
    for k in ks:
        ps = [shift_null(*block(rng, k, 0.0), FPS, n=200, seed=i)["p"] for i in range(n_sim)]
        rows.append({"nuisance_k": k, "naive_circular_test_false_positive_rate": float(np.mean(np.array(ps) < 0.05))})
    return pd.DataFrame(rows)


def contrast_power(n_dyads=(6, 10, 15), cs=(0.0, 0.2, 0.35, 0.5), n_sim=200, seed=1):
    rng = np.random.default_rng(seed); rows = []
    for n in n_dyads:
        for c in cs:
            hits = 0
            for _ in range(n_sim):
                d = []
                for _ in range(n):
                    k = rng.uniform(0, 0.6)                       # dyad-specific nuisance
                    lag = int(rng.integers(-10, 11))              # dyad-specific lead/lag (±0.4 s)
                    cd = max(0.0, rng.normal(c, 0.15 * c)) if c > 0 else 0.0
                    rN = abs(peak(*block(rng, k, cd, lag), FPS)[1]); rS = abs(peak(*block(rng, k, 0.0), FPS)[1])
                    d.append(rN - rS)
                p = stats.wilcoxon(d, alternative="greater").pvalue
                hits += p < 0.05
            rows.append({"n_dyads": n, "coupling_c": c, "rejection_rate": hits / n_sim})
    return pd.DataFrame(rows)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    fp = naive_false_positive(); print(fp.to_string(index=False))
    pw = contrast_power(); print(pw.to_string(index=False))
    fp.to_csv(OUT / "naive_false_positive.csv", index=False); pw.to_csv(OUT / "contrast_power.csv", index=False)
    md = ["# Phase-2 design simulation\n", "## Naive circular-shift test on blocks with NO coupling\n", fp.to_markdown(index=False),
          "\n\n## N-S contrast (Wilcoxon across dyads, one-sided, alpha 0.05)\n",
          "Rows with coupling_c = 0 are the false-positive rate under dyad-varying nuisance; the others are power.\n",
          pw.pivot(index="coupling_c", columns="n_dyads", values="rejection_rate").to_markdown(),
          "\n\nFor scale: c = 0.5 corresponds to a mean N-S difference in peak |r| of about 0.14 "
          "(SD across dyads about 0.11), c = 0.2-0.35 to about 0.02-0.03. The between-dyad SD is an "
          "assumption of this model; the pilot must measure it."]
    (OUT / "design_simulation.md").write_text("\n".join(md))
