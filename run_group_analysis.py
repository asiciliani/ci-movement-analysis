"""
Jam / multi-person analysis: proximity graph over the stage-1 detections table.

    python run_tracking.py --video videos/jam.mp4            # stage 1 (all detections are saved)
    python run_group_analysis.py --detections outputs/jam/jam_detections.csv --fps 30

Writes <stem>_graph_metrics.csv, <stem>_graph_pairs.csv, <stem>_graph_summary.json and a figure.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from src.analysis.group_graph import frame_graph_metrics, summarize


def main(detections: str, fps: float, edge_dist_bl: float = 1.0):
    p = Path(detections); stem = p.name.replace("_detections.csv", "")
    det = pd.read_csv(p)
    metrics, pairs = frame_graph_metrics(det, edge_dist_bl=edge_dist_bl)
    s = summarize(metrics, pairs, fps)
    metrics.to_csv(p.parent / f"{stem}_graph_metrics.csv", index=False); pairs.to_csv(p.parent / f"{stem}_graph_pairs.csv", index=False)
    with open(p.parent / f"{stem}_graph_summary.json", "w") as f:
        json.dump(s, f, indent=2)
    fig, ax = plt.subplots(3, 1, figsize=(10, 6), sharex=True)
    t = metrics.frame / fps
    ax[0].plot(t, metrics.n_nodes, label="people detected"); ax[0].plot(t, metrics.n_edges, label="proximity edges"); ax[0].legend(); ax[0].set_ylabel("count")
    ax[1].plot(t, metrics.n_components, color="#5E3C99"); ax[1].set_ylabel("components")
    ax[2].plot(t, metrics.largest_component, color="#E66100"); ax[2].set_ylabel("largest group"); ax[2].set_xlabel("time (s)")
    fig.suptitle(f"Proximity graph: {stem} (edge if centre distance < {edge_dist_bl} body length)")
    fig.tight_layout(); fig.savefig(p.parent / f"{stem}_graph.png", dpi=150)
    print(json.dumps(s, indent=2))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--detections", required=True); ap.add_argument("--fps", type=float, default=30.0)
    ap.add_argument("--edge-dist-bl", type=float, default=1.0); a = ap.parse_args()
    main(a.detections, a.fps, a.edge_dist_bl)
