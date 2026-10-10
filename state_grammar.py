"""
State grammar of a CI duet (idea 3 of the 8 Oct brainstorm): every moment is one of

  apart     nearest body segments > 1 body length
  near      0.25-1 bl, not touching
  contact   touching (depth-gated as in describe_duets.py), both off the floor-level threshold
  floor     touching or not, at least one dancer at floor level (pelvis < 0.6 bl above the own feet)
  share     weight sharing: one pelvis above the partner's shoulders and over their body, in contact

Gaps of <= 1 s where a dancer is not detected are bridged with the last state (detection flicker
otherwise chops every episode). Per duet: time share and median dwell time of each state, the transition
matrix between states (episodes >= 0.3 s), and the entropy of the next state given the current one
(how many different ways out each duet uses: 0 = always the same, log2(4) = 2 bits = uniform).

Outputs: outputs/grammar/{per_clip.csv, transitions.csv, report.md, transitions.png}
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.ndimage import median_filter

from src.io.tracks import load_tracks
from src.analysis import describe as D

OUT = Path("outputs/grammar"); OUT.mkdir(parents=True, exist_ok=True)
STATES = ["apart", "near", "contact", "share", "floor"]
HYST_OUT = 0.40
SEP_BL = 0.5      # a release counts only if the bodies get this far apart before touching again (hand check, AUDIT 43)


def frame_states(vid: str, return_dist: bool = False):
    tr = load_tracks(f"outputs/{vid}/{vid}_tracks.npz"); fps = float(tr.meta["fps"])
    kA, kB = tr.kpts[:, 0].astype(float), tr.kpts[:, 1].astype(float); both = tr.present.all(1)
    sA, sB = np.nanmedian(D.trunk_len(kA)), np.nanmedian(D.trunk_len(kB)); s = (sA + sB) / 2
    dmin, rA, rB, _ = D.contact_regions(kA, kB, s)
    limb = np.array([(a in ("hand", "arm")) or (b in ("hand", "arm")) for a, b in zip(rA, rB)])
    gate = D.same_depth(kA, kB, sA, sB) | limb
    d = np.nan_to_num(dmin, nan=9)
    # hysteresis (enter < 0.25 bl, leave > HYST_OUT bl): a distance hovering around one threshold makes the
    # state flicker between contact and near
    contact = np.zeros(len(d), bool); on = False
    for i in range(len(d)):
        on = (d[i] < 0.25 and gate[i]) if not on else (d[i] <= HYST_OUT)
        contact[i] = on
    contact = median_filter(contact, size=5).astype(bool)
    # merge contact episodes whose gap never reaches SEP_BL: in the hand check (outputs/grammar/contact_check.csv)
    # 14/15 false releases (flicker, a dancer lost in an embrace or carry) stayed <= 0.48 bl, all 9 real ones >= 0.54
    if SEP_BL:
        idx = np.flatnonzero(contact)
        for a, b in zip(idx[:-1], idx[1:]):
            if b - a > 1 and np.nanmax(np.r_[dmin[a + 1:b], 0]) <= SEP_BL:
                contact[a + 1:b] = True
    share = median_filter(np.nan_to_num(np.abs(D.aerial_support(kA, kB, sA, sB, contact))) > 0, size=5).astype(bool)
    floor = (np.nan_to_num(D.level(kA, sA), nan=9) < 0.6) | (np.nan_to_num(D.level(kB, sB), nan=9) < 0.6)
    st = np.where(share, "share", np.where(floor, "floor", np.where(contact, "contact",
                  np.where(np.nan_to_num(dmin, nan=99) < 1.0, "near", "apart")))).astype(object)
    st[~both | ~np.isfinite(dmin)] = None
    ser = pd.Series(st).ffill(limit=int(fps))          # bridge detection gaps <= 1 s
    if return_dist:
        return ser.to_numpy(), fps, dmin, both
    return ser.to_numpy(), fps


def runs(states, fps, min_s=0.3):
    out = []; prev = None; start = 0
    for i, x in enumerate(list(states) + [None]):
        if x != prev:
            if prev is not None and (i - start) >= min_s * fps:
                out.append((prev, (i - start) / fps))
            prev, start = x, i
    # merge consecutive equal states left after dropping short runs
    merged = []
    for s, d in out:
        if merged and merged[-1][0] == s:
            merged[-1] = (s, merged[-1][1] + d)
        else:
            merged.append((s, d))
    return merged


def main(hyst_out: float = 0.40):
    global HYST_OUT
    HYST_OUT = hyst_out
    cur = pd.read_csv("videos/curation.csv")
    vids = cur[cur.pair_ok.isin(["yes", "partial"]) & (cur.content == "ci_dance")].video.tolist()
    vids = [v for v in vids if f"{v}_full" not in vids and Path(f"outputs/{v}/{v}_tracks.npz").exists()]
    rows, T_all = [], pd.DataFrame(0, index=STATES, columns=STATES)
    for v in vids:
        st, fps = frame_states(v); r = runs(st, fps)
        known = pd.Series(st).dropna()
        row = dict(video=v, minutes=len(known) / fps / 60, episodes=len(r))
        for s in STATES:
            row[f"share_{s}"] = float((known == s).mean())
            d = [x[1] for x in r if x[0] == s]; row[f"dwell_{s}_s"] = float(np.median(d)) if d else np.nan
        T = pd.DataFrame(0, index=STATES, columns=STATES)
        for (a, _), (b, _) in zip(r[:-1], r[1:]):
            T.loc[a, b] += 1
        T_all += T
        P = T.div(T.sum(1).replace(0, np.nan), axis=0)
        w = T.sum(1) / max(T.values.sum(), 1)
        H = -(P * np.log2(P.where(P > 0))).sum(1)
        row["next_state_entropy_bits"] = float((w * H).sum()); row["transitions_per_min"] = len(r) / max(row["minutes"], 1e-9)
        rows.append(row)
        print(f"[grammar] {v}: {row['minutes']:.1f} min, entropy {row['next_state_entropy_bits']:.2f} bits, "
              + ", ".join(f"{s} {row['share_' + s]:.0%}" for s in STATES))
    pc = pd.DataFrame(rows); pc.to_csv(OUT / "per_clip.csv", index=False)
    P_all = T_all.div(T_all.sum(1), axis=0).round(3); P_all.to_csv(OUT / "transitions.csv")
    fig, ax = plt.subplots(figsize=(4.8, 4)); im = ax.imshow(P_all.values, cmap="Blues", vmin=0, vmax=1)
    ax.set_xticks(range(5)); ax.set_yticks(range(5)); ax.set_xticklabels(STATES, rotation=45); ax.set_yticklabels(STATES)
    for i in range(5):
        for j in range(5):
            ax.text(j, i, f"{P_all.values[i, j]:.2f}", ha="center", va="center", fontsize=8)
    ax.set_xlabel("next state"); ax.set_ylabel("current state"); ax.set_title(f"CI duet state transitions ({len(vids)} duets)")
    fig.colorbar(im, fraction=0.046); fig.tight_layout(); fig.savefig(OUT / "transitions.png", dpi=130)
    md = [f"# State grammar of {len(vids)} CI duets ({pc.minutes.sum():.1f} min)\n",
          "States per frame (see docstring); detection gaps <= 1 s bridged; episodes >= 0.3 s.\n",
          "## Per duet\n", pc.round(2).to_markdown(index=False),
          f"\n\n## Pooled transition probabilities (row = current state, {int(T_all.values.sum())} transitions)\n", P_all.to_markdown(),
          "\n\nCaveats: 'contact' and 'share' are 2-D detectors validated by eye (AUDIT 38-40); releases need SEP_BL separation (hand check, AUDIT 43); A/B identity does not matter "
          "here (states are symmetric)."]
    (OUT / "report.md").write_text("\n".join(md)); print("\n".join(md[2:5]))


if __name__ == "__main__":
    import sys
    main(float(sys.argv[1]) if len(sys.argv) > 1 else 0.40)
