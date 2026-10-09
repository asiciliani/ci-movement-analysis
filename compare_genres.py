"""
Same descriptors, two partner dances: CI (pair-verified public clips) vs salsa (CoMPAS3D renders, tracked with
the same video pipeline). Salsa is a known-answer check for the detectors: contact should be mostly
hand-to-hand holds (GRIP), dancers stay standing, almost no weight sharing. If the detectors report that for
salsa, the CI numbers mean something; if they don't, the detectors are wrong.

Outputs: outputs/compare_genres/{per_clip.csv, report.md, contact_regions.png}
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

import describe_duets as DD
import rolling_contact as RC

OUT = Path("outputs/compare_genres"); OUT.mkdir(parents=True, exist_ok=True)


def main():
    cur = pd.read_csv("videos/curation.csv")
    ci = [v for v in cur[cur.pair_ok.isin(["yes", "partial"]) & (cur.content == "ci_dance")].video.unique()
          if Path(f"outputs/{v}/{v}_tracks.npz").exists()]
    salsa = sorted(p.parent.name for p in Path("outputs").glob("salsa_*/salsa_*_tracks.npz"))
    rows, regs = [], {"CI": [], "salsa": []}
    for genre, vids in (("CI", ci), ("salsa", salsa)):
        for v in vids:
            row, ev, rg, _, _ = DD.clip_analysis(v)
            bouts, _ = RC.bouts_for_clip(v)
            b = pd.DataFrame(bouts)
            row.update(genre=genre, n_bouts=len(b),
                       roll_share=float((b.label == "ROLL").mean()) if len(b) else np.nan,
                       grip_share=float((b.label == "GRIP").mean()) if len(b) else np.nan,
                       hand_share=float(b.hand_share.median()) if len(b) else np.nan,
                       hand_hand_share=float(np.mean([r == ("hand", "hand") for r in rg])) if len(rg) else np.nan,
                       torso_share=float(np.mean(["torso" in r for r in rg])) if len(rg) else np.nan)
            rows.append(row); regs[genre].append(rg)
            print(f"[compare] {genre} {v}: contact {row['contact_frac']:.0%} weight-share/min {row['weight_share_per_min']:.1f} "
                  f"hand-hand {row['hand_hand_share']:.0%} torso {row['torso_share']:.0%} floor {row['frac_floor']:.0%}")
    df = pd.DataFrame(rows); df.to_csv(OUT / "per_clip.csv", index=False)
    cols = ["contact_frac", "weight_share_per_min", "frac_floor", "frac_standing", "hand_hand_share", "torso_share", "roll_share", "grip_share"]
    tab = df.groupby("genre")[cols].median().T.round(3)
    tests = {c: stats.mannwhitneyu(df[df.genre == "CI"][c].dropna(), df[df.genre == "salsa"][c].dropna()).pvalue
             if df[df.genre == "salsa"][c].notna().sum() >= 2 else np.nan for c in cols}
    tab["mann_whitney_p"] = pd.Series(tests).round(4)
    pooled = {g: pd.concat(r).value_counts(normalize=True) if r else pd.Series(dtype=float) for g, r in regs.items()}
    reg = pd.DataFrame(pooled).fillna(0).sort_values("CI", ascending=False).head(10).round(3)
    fig, ax = plt.subplots(figsize=(8, 4)); reg.plot.bar(ax=ax); ax.set_ylabel("share of contact frames")
    ax.set_title("Where the two bodies touch: CI vs salsa"); fig.tight_layout(); fig.savefig(OUT / "contact_regions.png", dpi=130)
    md = [f"# CI vs salsa with the same video pipeline ({len(ci)} CI clips, {len(salsa)} salsa clips)\n",
          "Medians per genre (each clip one observation). Salsa = CoMPAS3D renders (CC BY-NC 4.0), first 60 s.\n",
          tab.to_markdown(), "\n\n## Contact regions (pooled share of contact frames)\n", reg.to_markdown(),
          "\n\nKnown-answer expectations for salsa: hand-hand dominant, standing ~100 %, weight sharing ~0, GRIP > ROLL."]
    (OUT / "report.md").write_text("\n".join(md)); print("\n".join(md))


if __name__ == "__main__":
    main()
