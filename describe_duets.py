"""
Proof of concept: descriptive characterisation of CI duets (contact, rolling point of contact, levels,
lifts, descents to the floor, movement vocabulary). Runs on the clips whose tracked pair passed the
visual audit (videos/curation.csv: pair_ok yes/partial) and writes outputs/describe/:

  per_clip.csv              one row per clip: contact fraction and bouts, levels, lifts, descents
  contact_map.png           which body regions meet when the dancers touch (pooled and per clip)
  events.csv                every detected contact bout, lift and descent with start/end/duration
  vocabulary_*.png/csv      unsupervised movement "words" (k-means on 1 s pose windows) with examples
  check_*.jpg               frames of detected lifts / contact regions / vocabulary for visual validation
  report.md

Descriptive only: no claim here needs a null of "not interacting". Each detector must be checked on
the check_*.jpg sheets before its numbers are used.
"""
from __future__ import annotations

import glob
from pathlib import Path
import numpy as np
import pandas as pd
import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.ndimage import median_filter
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from src.io.tracks import load_tracks
from src.analysis import describe as D
from src.pose.pose_detector import SKELETON_EDGES

OUT = Path("outputs/describe"); OUT.mkdir(parents=True, exist_ok=True)
CONTACT_BL = 0.25
K_WORDS = 10
RNG = np.random.default_rng(0)


def clip_analysis(vid: str):
    tr = load_tracks(f"outputs/{vid}/{vid}_tracks.npz"); fps = float(tr.meta["fps"])
    kA, kB = tr.kpts[:, 0].astype(float), tr.kpts[:, 1].astype(float)
    both = tr.present.all(1)
    sA, sB = np.nanmedian(D.trunk_len(kA)), np.nanmedian(D.trunk_len(kB)); s = (sA + sB) / 2
    dmin, rA, rB, _ = D.contact_regions(kA, kB, s, CONTACT_BL)
    dmin[~both] = np.nan
    # depth gate only for body-to-body overlaps: an arm's-length hand hold between dancers at different
    # depths is real contact (salsa known-answer check, AUDIT 40)
    limb = np.array([(a in ("hand", "arm")) or (b in ("hand", "arm")) for a, b in zip(rA, rB)])
    depth_ok = D.same_depth(kA, kB, sA, sB) | limb
    contact = median_filter((np.nan_to_num(dmin, nan=9) < CONTACT_BL) & depth_ok, size=5).astype(bool) & both
    lvA, lvB = D.level(kA, sA), D.level(kB, sB)
    aer = D.aerial_support(kA, kB, sA, sB, contact)
    lift = median_filter(np.nan_to_num(np.abs(aer)) > 0, size=5).astype(bool) & both

    ev = []
    bouts = D.episodes(contact, fps, min_s=0.3)
    for a, b in bouts:
        ev.append(dict(video=vid, kind="contact", start_s=a / fps, end_s=b / fps, dur_s=(b - a) / fps))
    lifts = D.episodes(lift, fps, min_s=0.3)
    for a, b in lifts:
        who = np.nanmean(aer[a:b]); ev.append(dict(video=vid, kind="weight_share", start_s=a / fps, end_s=b / fps, dur_s=(b - a) / fps,
                                                   lifted="A" if who > 0 else "B"))
    # descents: standing (>=1.2 bl) to floor (<0.6 bl) within 4 s; speed of the drop = softness proxy
    for lab, lv, k, sc in (("A", lvA, kA, sA), ("B", lvB, kB, sB)):
        lvs = pd.Series(lv).rolling(5, center=True, min_periods=3).median().to_numpy()
        stand = np.flatnonzero(lvs >= 1.2); floor = np.flatnonzero(lvs < 0.6)
        i = 0
        while i < len(stand):
            t0 = stand[i]; nxt = floor[(floor > t0) & (floor <= t0 + 4 * fps)]
            if len(nxt):
                t1 = nxt[0]; t0 = stand[stand < t1].max()              # last standing frame before the floor
                pel = D.pelvis(k)[t0:t1 + 1, 1] / sc
                v = np.diff(pel) * fps
                ev.append(dict(video=vid, kind="descent", dancer=lab, start_s=t0 / fps, end_s=t1 / fps, dur_s=(t1 - t0) / fps,
                               drop_bl=float(lvs[t0] - lvs[t1]), peak_down_speed_bl_s=float(np.nanmax(v)) if len(v) else np.nan,
                               in_contact=bool(contact[t0:t1 + 1].mean() > 0.5)))
                i = np.searchsorted(stand, t1)
            else:
                i += 1
    regions = pd.Series([tuple(sorted((a, b))) for a, b, c in zip(rA, rB, contact) if c and a is not None])
    lvc = pd.concat([pd.Series(D.level_class(lvA)[tr.present[:, 0]]), pd.Series(D.level_class(lvB)[tr.present[:, 1]])]).dropna()
    minutes = both.sum() / fps / 60
    row = dict(video=vid, fps=fps, minutes_both_visible=minutes, contact_frac=float(contact[both].mean()),
               contact_bouts_per_min=len(bouts) / minutes, contact_bout_median_s=float(np.median([b - a for a, b in bouts]) / fps) if bouts else np.nan,
               weight_share_per_min=len(lifts) / minutes, weight_share_median_s=float(np.median([b - a for a, b in lifts]) / fps) if lifts else np.nan,
               frac_standing=float((lvc == "standing").mean()), frac_middle=float((lvc == "middle").mean()), frac_floor=float((lvc == "floor").mean()))
    feats = []
    for lab, k, sc, pres in (("A", kA, sA, tr.present[:, 0]), ("B", kB, sB, tr.present[:, 1])):
        pf = D.pose_features(k, sc); pf["contact"] = contact.astype(float); pf["dist_bl"] = dmin
        pf["rel_level"] = (D.level(k, sc) - (lvB if lab == "A" else lvA)); pf.loc[~pres, :] = np.nan
        pel = D.pelvis(k) / sc; pf["speed"] = np.linalg.norm(np.gradient(pel, axis=0), axis=1) * fps
        w, step = int(fps), int(fps / 2)
        for st in range(0, len(pf) - w, step):
            seg = pf.iloc[st:st + w]
            if seg["trunk_tilt"].notna().mean() < 0.8:
                continue
            f = seg.median().to_dict(); f.update(video=vid, dancer=lab, frame=st + w // 2, motion=float(np.nanmedian(seg["speed"])))
            feats.append(f)
    return row, ev, regions, pd.DataFrame(feats), tr


def draw(frame, k, color):
    for a, b in SKELETON_EDGES:
        if k[a, 2] > 0.3 and k[b, 2] > 0.3:
            cv2.line(frame, tuple(k[a, :2].astype(int)), tuple(k[b, :2].astype(int)), color, 3)


def sheet(items, path, title_fn, n=12, w=400):
    """items: list of (video, frame_idx, label). Writes a grid of frames with both skeletons."""
    tiles = []
    for vid, fi, label in items[:n]:
        vp = (sorted(glob.glob(f"videos/{vid}.*")) or [None])[0]
        if vp is None:
            continue
        cap = cv2.VideoCapture(vp); cap.set(1, int(fi)); ok, f = cap.read(); cap.release()
        if not ok:
            continue
        tr = TRACKS[vid]
        for j, col in ((0, (255, 160, 0)), (1, (0, 140, 255))):
            if tr.present[fi, j]:
                draw(f, tr.kpts[fi, j], col)
        f = cv2.resize(f, (w, int(w * f.shape[0] / f.shape[1])))
        cv2.putText(f, title_fn(vid, fi, label), (5, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)
        tiles.append(f)
    if not tiles:
        return
    h = max(t.shape[0] for t in tiles); tiles = [cv2.copyMakeBorder(t, 0, h - t.shape[0], 0, 0, cv2.BORDER_CONSTANT) for t in tiles]
    while len(tiles) % 4:
        tiles.append(np.zeros_like(tiles[0]))
    cv2.imwrite(str(path), np.vstack([np.hstack(tiles[i:i + 4]) for i in range(0, len(tiles), 4)]), [cv2.IMWRITE_JPEG_QUALITY, 80])


TRACKS = {}


def main():
    cur = pd.read_csv("videos/curation.csv")
    vids = cur[cur.pair_ok.isin(["yes", "partial"])].video.tolist()
    rows, events, regs, feats = [], [], {}, []
    for v in vids:
        row, ev, rg, ft, tr = clip_analysis(v); TRACKS[v] = tr
        rows.append(row); events += ev; regs[v] = rg; feats.append(ft)
        print(f"[describe] {v}: contact {row['contact_frac']:.0%}, weight-share/min {row['weight_share_per_min']:.1f}, floor {row['frac_floor']:.0%}")
    pc = pd.DataFrame(rows); ev = pd.DataFrame(events); F = pd.concat(feats, ignore_index=True)
    pc.to_csv(OUT / "per_clip.csv", index=False); ev.to_csv(OUT / "events.csv", index=False)

    # contact map: share of contact frames by (region, region), pooled and per clip
    R = D.REGIONS
    def mat(series):
        M = np.zeros((len(R), len(R)))
        for (a, b), n in series.value_counts().items():
            i, j = R.index(a), R.index(b); M[i, j] += n; M[j, i] += n if i != j else 0
        return M / max(M.sum() - np.trace(M) / 2, 1)
    fig, axs = plt.subplots(1, 1 + len(vids), figsize=(3.2 * (1 + len(vids)), 3.4))
    for ax, (name, ser) in zip(axs, [("pooled", pd.concat(regs.values()))] + list(regs.items())):
        M = mat(ser); ax.imshow(M, cmap="Blues", vmin=0); ax.set_title(name, fontsize=8)
        ax.set_xticks(range(len(R))); ax.set_yticks(range(len(R))); ax.set_xticklabels(R, rotation=90, fontsize=7); ax.set_yticklabels(R, fontsize=7)
        for i in range(len(R)):
            for j in range(len(R)):
                if M[i, j] >= 0.05:
                    ax.text(j, i, f"{M[i, j]:.0%}", ha="center", va="center", fontsize=6)
    fig.tight_layout(); fig.savefig(OUT / "contact_map.png", dpi=130); plt.close(fig)
    pooled = pd.concat(regs.values()).value_counts(normalize=True).head(10)

    # vocabulary: k-means on standardised 1 s pose windows, pooled over clips and dancers
    cols = ["trunk_tilt", "inverted", "knee_L", "knee_R", "hip_L", "hip_R", "elbow_L", "elbow_R", "arm_up_L", "arm_up_R",
            "level", "stance_width", "contact", "dist_bl", "rel_level", "motion"]
    X = F[cols].copy(); X["dist_bl"] = X["dist_bl"].clip(upper=3); X = X.fillna(X.median())
    Z = StandardScaler().fit_transform(X)
    km = KMeans(K_WORDS, n_init=10, random_state=0).fit(Z); F["word"] = km.labels_
    prof = F.groupby("word")[cols].median().round(2); prof["n"] = F.word.value_counts().sort_index()
    prof.to_csv(OUT / "vocabulary_profiles.csv")
    usage = pd.crosstab(F.video, F.word, normalize="index").round(3); usage.to_csv(OUT / "vocabulary_usage.csv")
    # signature reliability: is a clip's word distribution in its first half closer to its own second half
    # than to other clips' second halves?
    halves = []
    for v, g in F.groupby("video"):
        mid = g.frame.median()
        halves.append((v, np.bincount(g[g.frame <= mid].word, minlength=K_WORDS) / max((g.frame <= mid).sum(), 1),
                       np.bincount(g[g.frame > mid].word, minlength=K_WORDS) / max((g.frame > mid).sum(), 1)))
    def jsd(p, q):
        m = (p + q) / 2; kl = lambda a, b: np.sum(np.where(a > 0, a * np.log((a + 1e-12) / (b + 1e-12)), 0))
        return 0.5 * kl(p, m) + 0.5 * kl(q, m)
    hits = 0
    for i, (v, p1, _) in enumerate(halves):
        d = [jsd(p1, h[2]) for h in halves]; hits += int(np.argmin(d) == i)
    sig = dict(clips=len(halves), self_match=hits, chance=1 / len(halves))

    # validation sheets
    lif = ev[ev.kind == "weight_share"].sort_values("dur_s", ascending=False)
    sheet([(r.video, int(((r.start_s + r.end_s) / 2) * TRACKS[r.video].meta["fps"]), r.lifted) for r in lif.itertuples()][:12],
          OUT / "check_weight_share.jpg", lambda v, f, l: f"ON TOP {v[:6]} carried={l}")
    samples = []
    for v in vids:
        tr = TRACKS[v]; fps = tr.meta["fps"]
        kA, kB = tr.kpts[:, 0].astype(float), tr.kpts[:, 1].astype(float); s = np.nanmean([np.nanmedian(D.trunk_len(kA)), np.nanmedian(D.trunk_len(kB))])
        dmin, rA, rB, _ = D.contact_regions(kA, kB, s)
        idx = np.flatnonzero((dmin < CONTACT_BL) & tr.present.all(1) & D.same_depth(kA, kB, s, s))
        for fi in RNG.choice(idx, size=min(2, len(idx)), replace=False) if len(idx) else []:
            samples.append((v, int(fi), f"{rA[fi]}-{rB[fi]}"))
    sheet(samples, OUT / "check_contact_regions.jpg", lambda v, f, l: f"{v[:6]} A:{l.split('-')[0]} B:{l.split('-')[1]}", n=16)
    for w in range(K_WORDS):
        g = F[F.word == w]; pick = g.sample(min(8, len(g)), random_state=0)
        sheet([(r.video, int(r.frame), r.dancer) for r in pick.itertuples()], OUT / f"check_word_{w}.jpg",
              lambda v, f, l, w=w: f"word {w} {v[:6]} dancer {l}", n=8)

    md = ["# Descriptive PoC on the pair-verified CI clips\n",
          f"{len(vids)} clips, {pc.minutes_both_visible.sum():.1f} min with both dancers visible. Contact = nearest body segments "
          f"< {CONTACT_BL} body lengths (2-D: occlusion can fake contact). Levels from pelvis height above the own lowest foot.\n",
          "## Per clip\n", pc.round(2).to_markdown(index=False),
          "\n\n## Where they touch (pooled share of contact frames by body-region pair)\n", pooled.round(3).to_markdown(),
          "\n\n## Events\n", ev.groupby("kind").dur_s.describe().round(2).to_markdown(),
          "\n\nDescents to the floor (standing → floor within 4 s): duration, drop and peak downward pelvis speed\n\n",
          ev[ev.kind == "descent"].groupby("in_contact")[["dur_s", "drop_bl", "peak_down_speed_bl_s"]].median().round(2).to_markdown() if (ev.kind == "descent").any() else "none",
          "\n\n## Movement vocabulary (k-means on 1 s pose windows)\n", prof.to_markdown(),
          f"\n\nSignature check (split-half): {sig['self_match']}/{sig['clips']} clips' first half is closest to their own second half "
          f"(chance {sig['chance']:.2f}). Camera angle also differs between clips, so this mixes dancer style and viewpoint.\n",
          "\n## Validation sheets\ncheck_weight_share.jpg, check_contact_regions.jpg, check_word_*.jpg — every detector must be eyeballed before use."]
    (OUT / "report.md").write_text("\n".join(md)); print("\n".join(md[:6]))


if __name__ == "__main__":
    main()
