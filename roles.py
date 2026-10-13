"""
Idea A (13 Oct): role symmetry. In each weight-sharing episode, who is the base and who is on top (the flyer)?
CI ideology says roles alternate; salsa (fixed leader/follower) is the known-answer control.

CI (2-D, the 10 verified duets):
  episodes      weight-sharing episodes exactly as describe_duets.clip_analysis (aerial_support: +1 = A's pelvis
                above B's shoulders and over B's body, in contact; median-filtered; >= 0.3 s). Tracked on top =
                sign of the mean of aerial_support over the episode.
  identity      tracked A/B swap in some clips (curation.csv: "swaps", "swaps in lifts"), which fakes alternation.
                `sheets` draws, per episode, 5 frames (-1.5 s, start, middle, end, +1.5 s) with A blue / B orange;
                each row is judged by eye and written to outputs/roles/role_check.csv: is the episode real weight
                sharing, who is on top by APPEARANCE (a person label per duet, e.g. "dark"/"light"), and whether the
                tracked A/B identity is stable through the strip.
  statistics    per duet: episodes, share with person 1 on top, binomial test vs 50/50, alternation (number of
                role switches between consecutive episodes) vs a within-duet permutation of the episode order.
                Computed twice: with tracked labels and with eye labels (real episodes only).

Salsa (known answer, `salsa`): weight sharing is ~absent, so the role asymmetry is measured as who travels more
and who turns more per annotated ~2.5 s figure, in CoMPAS3D 3-D (roles known): root path length (trans) and
absolute trunk yaw rotation (Kabsch fit of the trunk markers frame to frame). Same per-unit statistics (share of
units where the leader dominates, binomial, alternation permutation). The same "who travels more" in 2-D on the
4 salsa renders tracked with the CI pipeline, with the leader identified by eye on a sheet.

Outputs: outputs/roles/{episodes.csv, role_check.csv, check_roles_*.jpg, per_duet.csv, salsa_*.csv, report.md}
"""
from __future__ import annotations

import glob
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import cv2
from scipy import stats

OUT = Path("outputs/roles"); OUT.mkdir(parents=True, exist_ok=True)
OFFS = ("-1.5", "start", "mid", "end", "+1.5")
RNG = np.random.default_rng(0)


def ci_videos():
    return pd.read_csv("outputs/grammar/per_clip.csv").video.tolist()


def ci_episodes():
    import describe_duets as DD
    from src.analysis import describe as D
    rows = []
    for v in ci_videos():
        row, ev, _, _, tr = DD.clip_analysis(v)
        fps = float(tr.meta["fps"])
        ev = pd.DataFrame(ev)
        if not len(ev) or not (ev.kind == "weight_share").any():
            continue
        for i, r in enumerate(ev[ev.kind == "weight_share"].itertuples()):
            rows.append(dict(video=v, ep=i, start_s=r.start_s, end_s=r.end_s, dur_s=r.dur_s,
                             top_tracked=r.lifted, fps=fps))
    df = pd.DataFrame(rows); df.insert(0, "id", range(len(df)))
    df.to_csv(OUT / "episodes.csv", index=False)
    return df


def tile(cap, tr, fi, label, w=250, h=230, crop=True):
    """Frame with both skeletons, cropped around the two dancers (union of boxes over +-1 s, +40 %)."""
    from rolling_contact import draw
    cap.set(1, int(fi)); ok, f = cap.read()
    if not ok:
        return np.zeros((h, w, 3), np.uint8)
    for j, col in ((0, (255, 160, 0)), (1, (0, 140, 255))):
        if tr.present[fi, j]:
            draw(f, tr.kpts[fi, j], col)
    if crop:
        lo, hi = max(fi - 15, 0), min(fi + 15, tr.n_frames)
        bb = tr.bbox[lo:hi][tr.present[lo:hi]]
        if len(bb):
            x0, y0 = np.nanmin(bb[:, 0]), np.nanmin(bb[:, 1]); x1, y1 = np.nanmax(bb[:, 2]), np.nanmax(bb[:, 3])
            cx, cy, s = (x0 + x1) / 2, (y0 + y1) / 2, max(x1 - x0, (y1 - y0) * w / h) * 0.7
            X0, X1 = int(max(cx - s, 0)), int(min(cx + s, f.shape[1])); sy = s * h / w
            Y0, Y1 = int(max(cy - sy, 0)), int(min(cy + sy, f.shape[0]))
            if X1 - X0 > 20 and Y1 - Y0 > 20:
                f = f[Y0:Y1, X0:X1]
    sc = min(w / f.shape[1], h / f.shape[0]); f = cv2.resize(f, (int(f.shape[1] * sc), int(f.shape[0] * sc)))
    f = cv2.copyMakeBorder(f, 0, h - f.shape[0], 0, w - f.shape[1], cv2.BORDER_CONSTANT)
    cv2.rectangle(f, (0, 0), (w, 18), (0, 0, 0), -1)
    cv2.putText(f, label, (3, 13), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (255, 255, 255), 1)
    return f


def video_path(v):
    return (sorted(glob.glob(f"videos/{v}.*")) + sorted(glob.glob(f"videos/full/{v}.*")) + sorted(glob.glob(f"videos/external/{v}.*")))[0]


def sheets():
    from src.io.tracks import load_tracks
    df = ci_episodes(); strips = []
    for v, g in df.groupby("video", sort=False):
        tr = load_tracks(f"outputs/{v}/{v}_tracks.npz"); cap = cv2.VideoCapture(video_path(v)); fps = g.fps.iloc[0]
        for r in g.itertuples():
            ts = (r.start_s - 1.5, r.start_s, (r.start_s + r.end_s) / 2, r.end_s - 1 / fps, r.end_s + 1.5)
            row = []
            for o, t in zip(OFFS, ts):
                fi = int(np.clip(round(t * fps), 0, tr.n_frames - 1))
                pres = "".join(c for c, p in zip("AB", tr.present[fi]) if p)
                row.append(tile(cap, tr, fi, f"{o} {t:.1f}s vis:{pres}"))
            s = np.hstack(row)
            cv2.putText(s, f"#{r.id} {v[:11]} {r.start_s:.1f}-{r.end_s:.1f}s top(tracked)={r.top_tracked} "
                           f"[A=blue B=orange]", (4, s.shape[0] - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
            strips.append(s)
        cap.release()
    for p in range(0, len(strips), 4):
        S = strips[p:p + 4]; W = max(x.shape[1] for x in S)
        cv2.imwrite(str(OUT / f"check_roles_{p // 4}.jpg"),
                    np.vstack([cv2.copyMakeBorder(x, 0, 6, 0, W - x.shape[1], cv2.BORDER_CONSTANT) for x in S]),
                    [cv2.IMWRITE_JPEG_QUALITY, 82])
    print(df.to_string())


# ------------------------------------------------------------------------------------------- statistics
def switches(seq):
    seq = list(seq)
    return sum(a != b for a, b in zip(seq[:-1], seq[1:]))


def alternation_test(seq, n_perm=20000, rng=RNG):
    """Number of role switches between consecutive units vs random orderings of the same units.
    Returns (switches, expected under permutation, p_more (alternates more than chance), p_less)."""
    seq = np.asarray(list(seq))
    if len(seq) < 3 or len(set(seq)) < 2:
        return switches(seq), np.nan, np.nan, np.nan
    obs = switches(seq)
    null = np.array([switches(rng.permutation(seq)) for _ in range(n_perm)])
    return obs, float(null.mean()), float((null >= obs).mean()), float((null <= obs).mean())


def pooled_alternation(groups, n_perm=20000, rng=RNG):
    """Sum of switches over several sequences, each permuted within itself."""
    groups = [np.asarray(list(g)) for g in groups if len(g) >= 2]
    obs = sum(switches(g) for g in groups)
    null = np.array([sum(switches(rng.permutation(g)) for g in groups) for _ in range(n_perm)])
    return obs, float(null.mean()), float((null >= obs).mean()), float((null <= obs).mean())


def summarize(units: pd.DataFrame, group: str, role_col: str, first: str):
    """units: one row per unit (episode / figure), ordered in time within group. role_col: who dominates."""
    rows = []
    for g, d in units.groupby(group, sort=False):
        seq = d[role_col].tolist(); n = len(seq); k = sum(x == first for x in seq)
        sw, exp, p_more, p_less = alternation_test(seq)
        rows.append(dict(group=g, n=n, share_first=k / n if n else np.nan,
                         binom_p=stats.binomtest(k, n, 0.5).pvalue if n else np.nan,
                         switches=sw, switches_expected=exp, p_alternate_more=p_more, p_alternate_less=p_less))
    return pd.DataFrame(rows)


# ------------------------------------------------------------------------------------------- salsa 3-D
COMPAS = Path("data_external/compas3d")
TRUNK = np.array([i for i in range(53) if i not in set(range(40, 53)) | {4, 5, 6, 13, 18, 19, 20, 27}
                  | {9, 10, 11, 12, 30, 31, 32, 33, 34, 23, 24, 25, 26, 35, 36, 37, 38, 39}])


def yaw_increments(M, step=3):
    """Horizontal rotation (rad) of the trunk marker cloud between frames t-step and t (2-D Procrustes on x,y),
    repeated per frame. M: (T,53,3) metres, z up."""
    P = M[:, TRUNK, :2]; P = P - np.nanmean(P, 1, keepdims=True)
    a, b = P[:-step], P[step:]
    cross = np.nansum(a[..., 0] * b[..., 1] - a[..., 1] * b[..., 0], 1); dot = np.nansum((a * b).sum(-1), 1)
    d = np.arctan2(cross, dot) / step
    return np.r_[d, np.full(step, np.nan)]


def together_figures(seq_dir):
    txt = sorted(glob.glob(str(seq_dir / "*.txt")))
    rows = []
    for line in open(txt[0], encoding="utf-8", errors="ignore") if txt else []:
        f = line.rstrip("\n").split("\t")
        if len(f) >= 9 and f[0] == "Together":
            rows.append(dict(start_s=float(f[3]), end_s=float(f[5]), label=f[8]))
    return pd.DataFrame(rows)


def turn_target(label):
    """Known answer from the annotation: who is said to turn in this figure."""
    l = label.lower(); f = "for the follower" in l or "follower turn" in l; L = "for the leader" in l
    return "both" if f and L else "follower" if f else "leader" if L else "none" if "turn" not in l else "other"


def salsa3d():
    rows = []
    for ld in sorted(COMPAS.glob("trans/Pair*/*/*_leader.npz")):
        seq = ld.parent.name; fd = ld.parent / ld.name.replace("leader", "follower")
        if not fd.exists():
            continue
        tl, tf = np.load(ld)["trans"], np.load(fd)["trans"]; fps = float(np.load(ld)["fps"])
        mk = COMPAS / "markers" / ld.parent.parent.name / seq
        yl = yf = None
        if (mk / f"{seq}_leader.npz").exists() and (mk / f"{seq}_follower.npz").exists():
            yl = yaw_increments(np.load(mk / f"{seq}_leader.npz")["markers"]); yf = yaw_increments(np.load(mk / f"{seq}_follower.npz")["markers"])
        sp = lambda t: np.r_[np.linalg.norm(np.diff(t[:, :2], axis=0), axis=1), np.nan]
        sl, sf = sp(tl), sp(tf)
        for i, r in enumerate(together_figures(ld.parent).itertuples()):
            a, b = int(r.start_s * fps), min(int(r.end_s * fps), len(tl))
            if b - a < fps:
                continue
            row = dict(pair=ld.parent.parent.name, seq=seq, fig=i, start_s=r.start_s, end_s=r.end_s, label=r.label,
                       turn_target=turn_target(r.label), path_leader=np.nansum(sl[a:b]), path_follower=np.nansum(sf[a:b]))
            if yl is not None:
                row.update(yaw_leader=float(np.degrees(np.nansum(np.abs(yl[a:b])))), yaw_follower=float(np.degrees(np.nansum(np.abs(yf[a:b])))))
            rows.append(row)
    df = pd.DataFrame(rows)
    df["travels_more"] = np.where(df.path_leader > df.path_follower, "leader", "follower")
    if "yaw_leader" in df:
        df["turns_more"] = np.where(df.yaw_leader.isna(), None, np.where(df.yaw_leader > df.yaw_follower, "leader", "follower"))
    df.to_csv(OUT / "salsa3d_figures.csv", index=False)
    return df


def report_salsa3d(df):
    md = ["## Salsa, CoMPAS3D 3-D (roles known): who travels more / who turns more per annotated figure\n",
          f"{df.seq.nunique()} sequences, {df.pair.nunique()} pairs, {len(df)} 'Together' figures (>= 1 s); "
          f"trunk yaw from markers in {df.yaw_leader.notna().groupby(df.seq).any().sum()} sequences.\n"]
    # validation of the yaw measure with the annotation's own turn labels
    t = df.dropna(subset=["yaw_leader"])
    val = t.groupby("turn_target").apply(lambda g: pd.Series(dict(n=len(g), follower_turns_more=(g.turns_more == "follower").mean(),
                                                                  yaw_leader_med=g.yaw_leader.median(), yaw_follower_med=g.yaw_follower.median()))).round(2)
    md += ["Known-answer check of the turn measure (annotation says who turns):\n", val.to_markdown(), ""]
    for col, first in (("travels_more", "leader"), ("turns_more", "follower")):
        d = df.dropna(subset=[col])
        per_seq = summarize(d, "seq", col, first)
        per_pair = d.groupby("pair")[col].apply(lambda s: (s == first).mean())
        k = int((d[col] == first).sum()); n = len(d)
        obs, exp, p_more, p_less = pooled_alternation([g[col].tolist() for _, g in d.groupby("seq")])
        md += [f"### {col} (share = {first})\n",
               f"Pooled figures: {k}/{n} = {k / n:.0%} (binomial p = {stats.binomtest(k, n, 0.5).pvalue:.2g}); per pair "
               f"{per_pair.round(2).to_dict()}; sequences with binomial p < 0.05: {(per_seq.binom_p < 0.05).sum()}/{len(per_seq)}.",
               f"Alternation (switches between consecutive figures, permuted within sequence): observed {obs}, expected {exp:.1f}, "
               f"p(more) = {p_more:.3f}, p(less) = {p_less:.3f}.\n"]
        per_seq.to_csv(OUT / f"salsa3d_{col}_per_seq.csv", index=False)
    return md


# ------------------------------------------------------------------------------------------- salsa 2-D
def fit_dlt(X, u):
    """Least-squares 3x4 projective camera from 3-D points X (N,3) to image points u (N,2)."""
    A = []
    for (x, y, z), (a, b) in zip(X, u):
        A.append([x, y, z, 1, 0, 0, 0, 0, -a * x, -a * y, -a * z, -a])
        A.append([0, 0, 0, 0, x, y, z, 1, -b * x, -b * y, -b * z, -b])
    _, _, Vt = np.linalg.svd(np.asarray(A)); return Vt[-1].reshape(3, 4)


def project(P, X):
    h = np.c_[X, np.ones(len(X))] @ P.T; return h[:, :2] / h[:, 2:]


def identity_oracle(tr, tl, tf):
    """Per frame, is track 0 the leader? Fits one camera to the 3-D root positions (trans) and the 2-D hip
    midpoints, alternating with the per-frame assignment (both pairings tried). Returns (lead0 (T,) bool/NaN,
    residual px of the chosen assignment, residual of the other)."""
    from src.analysis import describe as D
    T = min(tr.n_frames, len(tl)); p0, p1 = D.pelvis(tr.kpts[:T, 0].astype(float)), D.pelvis(tr.kpts[:T, 1].astype(float))
    ok = np.isfinite(p0).all(1) & np.isfinite(p1).all(1); idx = np.flatnonzero(ok)[::3]
    lead0 = np.ones(T, bool)
    for _ in range(8):
        X = np.r_[tl[idx], tf[idx]]
        U = np.r_[np.where(lead0[idx, None], p0[idx], p1[idx]), np.where(lead0[idx, None], p1[idx], p0[idx])]
        P = fit_dlt(X, U)
        a = np.linalg.norm(project(P, tl[:T]) - p0, axis=1) + np.linalg.norm(project(P, tf[:T]) - p1, axis=1)
        b = np.linalg.norm(project(P, tl[:T]) - p1, axis=1) + np.linalg.norm(project(P, tf[:T]) - p0, axis=1)
        new = a <= b
        if (new[idx] == lead0[idx]).all():
            break
        lead0 = new
    out = np.where(ok, lead0.astype(float), np.nan)
    return out, np.where(lead0, a, b) / 2, np.where(lead0, b, a) / 2


def salsa2d():
    from src.io.tracks import load_tracks
    from src.analysis import describe as D
    rows, idrows = [], []
    for p in sorted(Path("outputs").glob("salsa_*/salsa_*_tracks.npz")):
        seq = p.parent.name.replace("salsa_", ""); pair = seq.split("_")[0]; d = COMPAS / "trans" / pair / seq
        tr = load_tracks(p); fps = float(tr.meta["fps"])
        tl, tf = np.load(d / f"{seq}_leader.npz")["trans"], np.load(d / f"{seq}_follower.npz")["trans"]
        lead0, res, res_other = identity_oracle(tr, tl, tf)
        lab = pd.Series(lead0).ffill().bfill().to_numpy()
        sw = int(np.nansum(np.abs(np.diff(pd.Series(lead0).dropna().rolling(5, center=True).median().dropna().to_numpy()))))
        idrows.append(dict(seq=seq, frames_both=int(np.isfinite(lead0).sum()), track0_is_leader=float(np.nanmean(lead0)),
                           swaps=sw, res_px_median=float(np.nanmedian(res)), res_other_px_median=float(np.nanmedian(res_other))))
        T = min(tr.n_frames, len(tl))
        sc = [np.nanmedian(D.trunk_len(tr.kpts[:, j].astype(float))) for j in (0, 1)]
        def step2d(j, k=5):
            # pelvis smoothed (0.3 s rolling median) and differenced over k frames: raw frame-to-frame path is keypoint jitter
            pel = pd.DataFrame(D.pelvis(tr.kpts[:T, j].astype(float))).rolling(9, center=True, min_periods=5).median().to_numpy()
            st = np.full(T, np.nan); st[k:] = np.linalg.norm(pel[k:] - pel[:-k], axis=1) / k
            return st / sc[j]
        sp2 = [step2d(0), step2d(1)]
        sp3 = [np.r_[np.linalg.norm(np.diff(t[:T, :2], axis=0), axis=1), np.nan] for t in (tl, tf)]
        for i, r in enumerate(together_figures(d).itertuples()):
            a, b = int(r.start_s * fps), min(int(r.end_s * fps), T)
            if b - a < fps:
                continue
            p0, p1 = np.nansum(sp2[0][a:b]), np.nansum(sp2[1][a:b])
            # oracle-corrected: per frame, credit each tracked step to whoever the oracle says it is
            L = lab[a:b] > 0.5
            pl = np.nansum(np.where(L, sp2[0][a:b], sp2[1][a:b])); pf = np.nansum(np.where(L, sp2[1][a:b], sp2[0][a:b]))
            rows.append(dict(seq=seq, fig=i, start_s=r.start_s, label=r.label, track0_is_leader=float(np.nanmean(lead0[a:b])),
                             truth=("leader" if np.nansum(sp3[0][a:b]) > np.nansum(sp3[1][a:b]) else "follower"),
                             tracked=("track0" if p0 > p1 else "track1"),
                             corrected=("leader" if pl > pf else "follower")))
    return pd.DataFrame(idrows), pd.DataFrame(rows)


def report_salsa2d():
    ids, df = salsa2d(); ids.to_csv(OUT / "salsa2d_identity.csv", index=False); df.to_csv(OUT / "salsa2d_figures.csv", index=False)
    md = ["## Salsa renders in 2-D (same pipeline as CI): who travels more per annotated figure\n",
          "Identity oracle: one projective camera fitted to the 3-D root positions and the tracked 2-D hips, per-frame assignment "
          "(which track is the leader) chosen by the smaller reprojection error.\n", ids.round(2).to_markdown(index=False), ""]
    for seq, g in df.groupby("seq"):
        maj = "track0" if (g.track0_is_leader.mean() > 0.5) else "track1"
        g = g.assign(tracked_as_role=np.where(g.tracked == maj, "leader", "follower"))
        sw_t = alternation_test(g.tracked.tolist()); sw_c = alternation_test(g.corrected.tolist()); sw_3 = alternation_test(g.truth.tolist())
        md.append(f"- {seq}: {len(g)} figures. 3-D truth: leader travels more in {(g.truth == 'leader').mean():.0%}. 2-D tracked labels "
                  f"(majority mapping): {(g.tracked_as_role == 'leader').mean():.0%}, agreement with 3-D {(g.tracked_as_role == g.truth).mean():.0%}; "
                  f"oracle-corrected: {(g.corrected == 'leader').mean():.0%}, agreement {(g.corrected == g.truth).mean():.0%}. "
                  f"Switches: tracked {sw_t[0]} (exp {sw_t[1]:.1f}, p_more {sw_t[2]:.2f}), corrected {sw_c[0]} (exp {sw_c[1]:.1f}), 3-D {sw_3[0]} (exp {sw_3[1]:.1f}).")
    return md


# ------------------------------------------------------------------------------------------- CI statistics
def concentration_test(ns_ks, n_sim=100000, rng=RNG):
    """Are flyer roles more concentrated on one person per duet than 50/50 coin flips? Statistic: sum over duets
    of max(k, n - k) (episodes with the duet's most frequent flyer); null: independent fair coins per episode."""
    obs = sum(max(k, n - k) for n, k in ns_ks)
    sim = sum(np.maximum(x, n - x) for n, x in ((n, rng.binomial(n, 0.5, n_sim)) for n, _ in ns_ks))
    return obs, float(sim.mean()), float((sim >= obs).mean())


def ci_stats():
    ep = pd.read_csv(OUT / "episodes.csv"); chk = pd.read_csv(OUT / "role_check.csv").drop(columns="video")
    df = ep.merge(chk, on="id")
    md = ["## CI weight-sharing episodes (10 duets)\n",
          f"Detector episodes: {len(df)}. By eye: real {int((df.real == 'yes').sum())}, false {int((df.real == 'no').sum())}, "
          f"unclear {int((df.real == 'unclear').sum())}; flyer identifiable by appearance in "
          f"{int(((df.real == 'yes') & df.top_eye.notna()).sum())}. All false positives are one dancer standing or kneeling next to a "
          f"partner who is low (lying, seated, on all fours): 'pelvis above the partner's shoulders' without being on them.\n"]
    known = df[(df.real == "yes") & df.top_eye.notna() & df.tracked_top_is.notna()]
    md.append(f"Detector's role (which tracked body is on top) vs eye, where both known: the tracked 'top' body is the eye flyer in "
              f"{int((known.tracked_top_is == known.top_eye).sum())}/{len(known)} (errors: the flyer folded over or inverted on a standing "
              f"base, whose pelvis is then higher).")
    # identity swaps: letter -> person mapping changes between consecutive known episodes of a duet
    sw = 0; npairs = 0
    for v, g in known[known.tracked_top_is == known.top_eye].groupby("video", sort=False):
        m = [(r.top_tracked, r.top_eye) for r in g.itertuples()]
        for (l1, p1), (l2, p2) in zip(m[:-1], m[1:]):
            npairs += 1; sw += int((l1 == l2) != (p1 == p2))
    md.append(f"Tracked identity swaps between consecutive checked episodes of the same duet: {sw}/{npairs}.\n")
    # statistics: tracked labels (all detector episodes) and eye labels (real episodes with a known flyer)
    t = summarize(df, "video", "top_tracked", "A"); t.insert(1, "labels", "tracked (all detector episodes)")
    e_df = df[(df.real == "yes") & df.top_eye.notna()]
    firsts = e_df.groupby("video").top_eye.agg(lambda s: s.value_counts().index[0])
    e_df = e_df.assign(flyer_is_main=np.where(e_df.top_eye == e_df.video.map(firsts), "main", "other"))
    e = summarize(e_df, "video", "flyer_is_main", "main"); e.insert(1, "labels", "eye (real episodes, flyer known)")
    e["main_flyer"] = e.group.map(firsts)
    tab = pd.concat([t, e], ignore_index=True); tab.to_csv(OUT / "per_duet.csv", index=False)
    md += ["Per duet (share_first = share of episodes with tracked A on top / with the duet's most frequent flyer on top; "
           "switches between consecutive episodes vs within-duet permutation):\n", tab.round(3).to_markdown(index=False), ""]
    for name, d, col in (("tracked", df, "top_tracked"), ("eye", e_df, "flyer_is_main")):
        groups = [g[col].tolist() for _, g in d.groupby("video", sort=False)]
        obs, exp, p_more, p_less = pooled_alternation(groups)
        nk = [(len(g), sum(x == g[0] for x in g)) for g in groups]
        c_obs, c_exp, c_p = concentration_test(nk)
        md.append(f"- {name} labels: pooled switches {obs} vs {exp:.1f} expected (p alternate more = {p_more:.3f}, less = {p_less:.3f}); "
                  f"concentration on one flyer per duet {c_obs} vs {c_exp:.1f} under 50/50 coins (p = {c_p:.3f}).")
    # same set of episodes, tracked vs eye: does tracking change the alternation count?
    same = e_df.copy()
    st = sum(switches(g.top_tracked) for _, g in same.groupby("video")); se = sum(switches(g.top_eye) for _, g in same.groupby("video"))
    ns = [len(g) for _, g in e_df.groupby("video")]; r = np.random.default_rng(2)
    null = sum(np.maximum(x, n - x) for n, x in ((n, r.binomial(n, 0.5, 100000)) for n in ns)); crit = np.quantile(null, 0.95)
    c_obs = concentration_test([(len(g), int((g.flyer_is_main == "main").sum())) for _, g in e_df.groupby("video")])[0]
    pw = []
    for p in (0.7, 0.8, 0.9, 1.0):
        sim = sum(np.maximum(x, n - x) for n, x in ((n, r.binomial(n, p, 20000)) for n in ns))
        pw.append(f"p = {p}: power {np.mean(sim > crit):.2f}, P(stat <= observed {c_obs}) = {np.mean(sim <= c_obs):.3f}")
    md.append("- What these counts can tell (episode counts per duet " + str(ns) + "): if each duet had one dancer on top with probability p, "
              + "; ".join(pw) + ". Perfect alternation in every duet would give p = 0.001 on the switch test; a switch probability of 0.8 "
              "would be detected about half the time.")
    md.append(f"- On the same {len(same)} eye-labelled episodes: tracked A/B labels give {st} role switches, the eye labels {se}.\n")
    return md


def main():
    md = ["# Role symmetry: who is on top (CI) / who travels or turns (salsa)\n",
          "Method and caveats in the docstring of roles.py. Check sheets: outputs/roles/check_roles_*.jpg; verdicts role_check.csv.\n"]
    md += ci_stats()
    md += report_salsa3d(pd.read_csv(OUT / "salsa3d_figures.csv")) if (OUT / "salsa3d_figures.csv").exists() else report_salsa3d(salsa3d())
    md += report_salsa2d()
    (OUT / "report.md").write_text("\n".join(md)); print("\n".join(md))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "sheets"
    if cmd == "salsa3d":
        print("\n".join(report_salsa3d(salsa3d())))
    elif cmd == "salsa2d":
        print("\n".join(report_salsa2d()))
    else:
        {"sheets": sheets, "report": main}[cmd]()
