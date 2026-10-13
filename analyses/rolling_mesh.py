"""
Rolling vs gripping on full body meshes (SMPL-X), on salsa with a known answer. Follows rolling_3d.py (AUDIT 44),
where 53 sparse markers could tell WHERE bodies touch but not whether the contact point travels.

CoMPAS3D ships SMPL-X (locked head) parameters per dancer; with the model files (data_external/smplx_models/,
licence from smpl-x.is.tue.mpg.de, not redistributed) each frame becomes a 10,475-vertex skin surface. Check:
the observed mocap markers lie ~2 cm from the reconstructed skin (marker base + clothing).

  frames         10 fps; every VERT_STEP-th vertex (~2,600 per body, ~2 cm spacing)
  contact        vertices of one body within CONTACT_M of the other body's surface
  body chart     each dancer's own rest-pose (T-pose) mesh: a contact vertex keeps its chart position however
                 the limb moves, so a held hand does not "travel" when the partner turns under it
  sites          per frame, contact vertices of body A grouped into connected patches on A's chart (DBSCAN,
                 eps SITE_EPS_M); each patch is paired with the partner vertices it touches
  tracks         sites linked frame to frame when the chart centroids on BOTH bodies moved < LINK_M in that step
                 (a slide moves a few cm per 0.1 s; a hand change, one hand released and the other taking over,
                 jumps ~1 m on the chart and must start a new track); a track survives gaps up to GAP_S
  travel         per track >= MIN_TRACK_S: net displacement of the chart centroid between its first and last
                 0.5 s, on each body (m)
  label          GRIP: both bodies < GRIP_M; SLIDE/ROLL: either body >= ROLL_M; otherwise MIXED

Known-answer checks:
  1. hand-hand tracks stay put (GRIP, or MIXED when the hand pivots inside the hold), also during turns under
     the arm, where the 2-D version reported rolls
  2. closed holds: a hand-on-back track that stays put
  3. sensitivity (tests/test_rolling_mesh_synthetic.py): a synthetic hand sliding down a real, moving dancer's
     back is reported as SLIDE/ROLL with its true length, and a synthetic hold as GRIP
  The figures annotated "hands change behind the leader..." turned out not to be a positive class: the hold is
  released and re-taken with the other hand, nothing slides (0 of 100 figures contain a SLIDE/ROLL track).
  Salsa has almost no sliding contact, so real rolling still has to be validated on CI itself.

Outputs: outputs/rolling_mesh/{tracks.csv, segments.csv, report.md}
"""
from __future__ import annotations

import pickle
from pathlib import Path
import numpy as np
import pandas as pd
import torch
import smplx
from scipy import stats
from scipy.spatial import cKDTree
from sklearn.cluster import DBSCAN

import rolling_3d as R3

ROOT = Path("data_external/compas3d")
MODELS = Path("data_external/smplx_models/models_lockedhead")
OUT = Path("outputs/rolling_mesh"); OUT.mkdir(parents=True, exist_ok=True)
FPS_OUT, VERT_STEP = 10.0, 4
CONTACT_M, SITE_EPS_M, LINK_M, GAP_S, MIN_TRACK_S, END_S = 0.03, 0.06, 0.08, 0.3, 1.0, 0.5
GRIP_M, ROLL_M = 0.05, 0.15

# SMPL-X joint index -> coarse region (per-triangle segmentation in smplx_parts_segm.pkl uses joint indices)
_REG = {**{j: "trunk" for j in (0, 3, 6, 9, 13, 14)}, **{j: "leg" for j in (1, 2, 4, 5, 7, 8, 10, 11)},
        **{j: "head" for j in (12, 15, 22, 23, 24)}, 16: "upper_arm", 17: "upper_arm", 18: "forearm", 19: "forearm",
        **{j: "hand" for j in [20, 21] + list(range(25, 55))}}


def vertex_regions(faces: np.ndarray) -> np.ndarray:
    segm = pickle.load(open(MODELS.parent / "smplx_parts_segm.pkl", "rb"), encoding="latin1")["segm"]
    reg = np.empty(faces.max() + 1, dtype=object)
    for f, j in zip(faces, segm):
        reg[f] = _REG.get(int(j), "trunk")
    return reg


def meshes(z, step: int):
    """Posed vertices (T', V', 3) at FPS_OUT, rest-pose vertices (V', 3), faces of the full mesh."""
    m = smplx.create(str(MODELS), model_type="smplx", gender=str(z["gender"]), num_betas=300, use_pca=False,
                     flat_hand_mean=True, batch_size=1)
    idx = np.arange(0, len(z["poses"]), max(1, int(round(float(z["fps"]) / FPS_OUT))))
    keep = np.arange(0, m.v_template.shape[0], step)
    betas = torch.tensor(z["betas"])[None]
    with torch.no_grad():
        rest = m(betas=betas).vertices[0].numpy()[keep]
        V = []
        for a in range(0, len(idx), 256):
            P = torch.tensor(z["poses"][idx[a:a + 256]]); n = len(P)
            out = m(betas=betas.expand(n, -1), global_orient=P[:, :3], body_pose=P[:, 3:66], jaw_pose=P[:, 66:69],
                    leye_pose=P[:, 69:72], reye_pose=P[:, 72:75], left_hand_pose=P[:, 75:120],
                    right_hand_pose=P[:, 120:165], transl=torch.tensor(z["trans"][idx[a:a + 256]]),
                    expression=torch.zeros(n, 10))
            V.append(out.vertices.numpy()[:, keep])
    return np.concatenate(V), rest, m.faces.astype(int), keep, idx / float(z["fps"])


def frame_sites(VA, VB, restA, restB):
    """Contact sites of one frame: list of (chart centroid on A, chart centroid on B, region on A, region on B idx)."""
    dA, jB = cKDTree(VB).query(VA, distance_upper_bound=CONTACT_M)
    hit = np.isfinite(dA)
    if not hit.any():
        return []
    ia = np.flatnonzero(hit); ib = jB[hit]
    lab = DBSCAN(eps=SITE_EPS_M, min_samples=1).fit_predict(restA[ia])
    return [(restA[ia[lab == c]].mean(0), restB[ib[lab == c]].mean(0), ia[lab == c], ib[lab == c]) for c in np.unique(lab)]


def track_sites(per_frame, t, regA, regB):
    """Greedy frame-to-frame linking of sites; returns finished tracks."""
    live, done = [], []
    for k, sites in enumerate(per_frame):
        used = set()
        for tr in live:
            if t[k] - tr["t"][-1] > GAP_S:
                continue
            best, bd = None, np.inf
            for s_i, (cA, cB, _, _) in enumerate(sites):
                if s_i in used:
                    continue
                d = max(np.linalg.norm(cA - tr["cA"][-1]), np.linalg.norm(cB - tr["cB"][-1]))
                if d < LINK_M and d < bd:
                    best, bd = s_i, d
            if best is not None:
                cA, cB, ia, ib = sites[best]; used.add(best)
                tr["t"].append(t[k]); tr["cA"].append(cA); tr["cB"].append(cB)
                tr["rA"].extend(regA[ia]); tr["rB"].extend(regB[ib])
        for s_i, (cA, cB, ia, ib) in enumerate(sites):
            if s_i not in used:
                live.append(dict(t=[t[k]], cA=[cA], cB=[cB], rA=list(regA[ia]), rB=list(regB[ib])))
        still = [tr for tr in live if t[k] - tr["t"][-1] <= GAP_S]
        done += [tr for tr in live if t[k] - tr["t"][-1] > GAP_S]
        live = still
    return done + live


def summarise(tr):
    t = np.array(tr["t"]); dur = t[-1] - t[0]
    if dur < MIN_TRACK_S:
        return None
    first, last = t <= t[0] + END_S, t >= t[-1] - END_S
    cA, cB = np.array(tr["cA"]), np.array(tr["cB"])
    netA = float(np.linalg.norm(cA[last].mean(0) - cA[first].mean(0)))
    netB = float(np.linalg.norm(cB[last].mean(0) - cB[first].mean(0)))
    label = "GRIP" if max(netA, netB) < GRIP_M else "SLIDE/ROLL" if max(netA, netB) >= ROLL_M else "MIXED"
    return dict(start_s=t[0], end_s=t[-1], dur_s=dur, travel_leader_m=netA, travel_follower_m=netB,
                region_leader=pd.Series(tr["rA"]).mode().iat[0], region_follower=pd.Series(tr["rB"]).mode().iat[0], label=label)


def sequence(seq_dir: Path):
    name = seq_dir.name
    zL = np.load(seq_dir / f"{name}_leader.npz"); zF = np.load(seq_dir / f"{name}_follower.npz")
    VL, restL, faces, keep, t = meshes(zL, VERT_STEP); VF, restF, _, _, _ = meshes(zF, VERT_STEP)
    n = min(len(VL), len(VF)); reg = vertex_regions(faces)[keep]
    per_frame = [frame_sites(VL[k], VF[k], restL, restF) for k in range(n)]
    rows = [r for r in (summarise(tr) for tr in track_sites(per_frame, t[:n], reg, reg)) if r]
    return pd.DataFrame(rows).assign(seq=name), np.array([len(s) > 0 for s in per_frame]), t[:n]


def main():
    seqs = sorted(p.parent for p in ROOT.glob("smplx/Pair*/*/*_leader.npz")
                  if (p.parent / p.name.replace("leader", "follower")).exists())
    T, S = [], []
    for s in seqs:
        tracks, contact, t = sequence(s)
        T.append(tracks)
        ann = R3.annotations(ROOT / "trans" / s.relative_to(ROOT / "smplx"))
        for r in ann.itertuples():
            inside = tracks[(tracks.start_s < r.end_s) & (tracks.end_s > r.start_s)] if len(tracks) else tracks
            S.append(dict(seq=s.name, start_s=r.start_s, end_s=r.end_s, label=r.label, cls=R3.figure_class(r.label),
                          contact_frac=float(contact[(t >= r.start_s) & (t < r.end_s)].mean()) if ((t >= r.start_s) & (t < r.end_s)).any() else np.nan,
                          n_tracks=len(inside), any_slide=bool((inside.label == "SLIDE/ROLL").any()) if len(inside) else False,
                          hand_hand_grip=float(((inside.region_leader == "hand") & (inside.region_follower == "hand") & (inside.label == "GRIP")).mean()) if len(inside) else np.nan))
        print(f"[rolling_mesh] {s.name}: {len(tracks)} tracks, " + (tracks.label.value_counts().to_dict().__str__() if len(tracks) else ""))
    T = pd.concat(T, ignore_index=True); Sg = pd.DataFrame(S)
    T.to_csv(OUT / "tracks.csv", index=False); Sg.to_csv(OUT / "segments.csv", index=False)
    hh = T[(T.region_leader == "hand") & (T.region_follower == "hand")]
    body = T[~((T.region_leader == "hand") & (T.region_follower == "hand"))]
    order = ["open hold", "turn, hands held", "closed hold", "hand travels over body", "other"]
    tab = Sg.groupby("cls").agg(figures=("label", "size"), contact=("contact_frac", "median"),
                                with_slide=("any_slide", "mean")).reindex(order).round(3)
    def fisher(a, b):
        x, y = Sg[Sg.cls == a].any_slide, Sg[Sg.cls == b].any_slide
        return stats.fisher_exact([[x.sum(), (~x).sum()], [y.sum(), (~y).sum()]], alternative="greater")[1]
    checks = pd.DataFrame([
        ("hand-hand tracks are GRIP", f"{(hh.label == 'GRIP').mean():.0%} of {len(hh)}"),
        ("hand-hand tracks during turn figures are GRIP", ""),
        ("hand travels > turn, hands held (figures with a SLIDE/ROLL track)", f"p = {fisher('hand travels over body', 'turn, hands held'):.4f}"),
        ("hand travels > open hold", f"p = {fisher('hand travels over body', 'open hold'):.4f}"),
    ], columns=["check", "result"])
    turn_t = Sg[Sg.cls == "turn, hands held"]
    in_turn = hh[[any((r.seq == s.seq) and (r.start_s < s.end_s) and (r.end_s > s.start_s) for s in turn_t.itertuples()) for r in hh.itertuples()]]
    checks.loc[1, "result"] = f"{(in_turn.label == 'GRIP').mean():.0%} of {len(in_turn)}" if len(in_turn) else "none"
    md = [f"# Rolling vs gripping on SMPL-X meshes: CoMPAS3D salsa ({len(seqs)} sequences, {len(T)} contact tracks >= {MIN_TRACK_S:g} s)\n",
          f"Contact = vertices within {CONTACT_M * 100:.0f} cm of the partner's skin, {FPS_OUT:g} fps; sites tracked on each dancer's "
          f"rest-pose body; GRIP < {GRIP_M * 100:.0f} cm net travel on both bodies, SLIDE/ROLL >= {ROLL_M * 100:.0f} cm on either.\n",
          "## Known-answer checks\n", checks.to_markdown(index=False),
          "\n\n## Tracks by label\n", T.label.value_counts().to_frame("tracks").to_markdown(),
          "\n\nHand-hand tracks:\n\n" + hh.label.value_counts().to_frame("tracks").to_markdown(),
          "\n\nBody tracks (any non hand-hand), main regions:\n\n" + body.groupby(["region_leader", "region_follower", "label"]).size().sort_values(ascending=False).head(12).to_frame("tracks").to_markdown(),
          "\n\n## By annotated figure class\n", tab.to_markdown()]
    (OUT / "report.md").write_text("\n".join(md)); print("\n".join(md))


if __name__ == "__main__":
    main()
