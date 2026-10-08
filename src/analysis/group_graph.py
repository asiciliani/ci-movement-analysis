"""
Proximity-graph analysis of multi-person footage (jams).

This is plain graph analysis, not a neural network: nodes are tracked people (bbox centres from
the stage-1 detections table), an edge joins two people whose centre distance is below
`edge_dist_bl` body lengths (person height / 3.3 as the scale). Per frame we report the number
of nodes, edges, connected components, the largest component and mean degree; per track pair we
report how long they stayed connected. Identity switches inside the underlying tracker are not
corrected here: the per-frame topology does not depend on identities, the pair persistence does.
"""
from __future__ import annotations

from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd


def _components(n: int, edges: np.ndarray) -> np.ndarray:
    parent = np.arange(n)

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]; i = parent[i]
        return i
    for a, b in edges:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
    return np.array([find(i) for i in range(n)])


def frame_graph_metrics(det: pd.DataFrame, edge_dist_bl: float = 1.0, min_conf: float = 0.3) -> Tuple[pd.DataFrame, pd.DataFrame]:
    det = det[(det.conf >= min_conf) & (det.track_id >= 0)].copy()
    det["cx"] = (det.x1 + det.x2) / 2; det["cy"] = (det.y1 + det.y2) / 2; det["h"] = det.y2 - det.y1
    scale = float(np.median(det.h)) / 3.3 if len(det) else np.nan   # trunk ~ 0.3 of standing height
    rows, pair_rows = [], {}
    for f, g in det.groupby("frame"):
        ids = g.track_id.to_numpy(); P = g[["cx", "cy"]].to_numpy()
        n = len(ids)
        if n == 0:
            rows.append({"frame": f, "n_nodes": 0, "n_edges": 0, "n_components": 0, "largest_component": 0, "mean_degree": 0.0}); continue
        D = np.linalg.norm(P[:, None] - P[None], axis=-1)
        iu = np.triu_indices(n, 1)
        close = D[iu] < edge_dist_bl * scale
        edges = np.column_stack([iu[0][close], iu[1][close]])
        comp = _components(n, edges)
        sizes = np.bincount(comp)
        rows.append({"frame": f, "n_nodes": n, "n_edges": int(close.sum()), "n_components": int(len(np.unique(comp))),
                     "largest_component": int(sizes.max()), "mean_degree": float(2 * close.sum() / n)})
        for a, b in edges:
            key = tuple(sorted((int(ids[a]), int(ids[b]))))
            pair_rows[key] = pair_rows.get(key, 0) + 1
    pairs = pd.DataFrame([{"id_a": k[0], "id_b": k[1], "frames_connected": v} for k, v in pair_rows.items()]).sort_values("frames_connected", ascending=False) if pair_rows else pd.DataFrame(columns=["id_a", "id_b", "frames_connected"])
    return pd.DataFrame(rows), pairs


def summarize(metrics: pd.DataFrame, pairs: pd.DataFrame, fps: float) -> Dict[str, Any]:
    return {"n_frames": int(len(metrics)), "mean_nodes": float(metrics.n_nodes.mean()), "mean_edges": float(metrics.n_edges.mean()),
            "mean_components": float(metrics.n_components.mean()), "p95_largest_component": float(metrics.largest_component.quantile(0.95)),
            "n_pairs_ever_connected": int(len(pairs)), "pairs_connected_over_5s": int((pairs.frames_connected > 5 * fps).sum()) if len(pairs) else 0,
            "edge_density": float((metrics.n_edges / np.maximum(1, metrics.n_nodes * (metrics.n_nodes - 1) / 2)).mean())}
