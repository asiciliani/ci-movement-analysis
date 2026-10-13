"""
"Yield / knowing how to fall": how CI dancers go down to the floor, from 2-D keypoints.

Step 1 (validation)  `sheet`  : check sheets for a random sample of detected descents (5 frames across each,
                                both skeletons, descender named in the label); verdicts typed by hand into
                                outputs/falls/descent_check*.csv.
Step 2 (descriptors) `describe`: for descents that pass the (revised) detector, the yield descriptors: duration,
                                pelvis-height velocity profile, smoothness (SPARC, log dimensionless jerk) with
                                a noise floor, and what happens in the 2 s after reaching the floor.
Step 3 (external)    see fall_external.py (accidental falls, same descriptors).

Units: bl = dancer's median trunk length. Height = describe.level (pelvis above own lowest foot), which uses the
dancer's own feet as the reference so camera panning and perspective cancel to first order. Image y grows down.
Descriptive only; 2-D monocular video gives no forces, no true vertical, no depth.
"""
from __future__ import annotations
import warnings
warnings.filterwarnings('ignore', category=RuntimeWarning)

import glob
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import cv2
from scipy.signal import butter, filtfilt

from src.io.tracks import load_tracks
from src.analysis import describe as D
from rolling_contact import draw
import state_grammar as SG

OUT = Path("outputs/falls"); OUT.mkdir(parents=True, exist_ok=True)
COL = {0: (255, 160, 0), 1: (0, 140, 255)}          # BGR: A light blue, B orange
NAME = {0: "A(blue)", 1: "B(orange)"}


def video_path(vid):
    return (sorted(glob.glob(f"videos/{vid}.*")) + sorted(glob.glob(f"videos/full/{vid}.*")))[0]


def tile(cap, tr, fi, j, label, box=None, h=300):
    cap.set(1, fi); ok, f = cap.read()
    if not ok:
        return np.zeros((h, int(h * 1.2), 3), np.uint8)
    for jj in (0, 1):
        if tr.present[fi, jj]:
            draw(f, tr.kpts[fi, jj], COL[jj])
    if tr.present[fi, j]:                            # mark the descender's pelvis
        p = D.pelvis(tr.kpts[fi:fi + 1, j].astype(float))[0]
        if np.isfinite(p).all():
            cv2.circle(f, tuple(p.astype(int)), 14, (0, 0, 255), 4)
    if box is not None:
        x0, y0, x1, y1 = box; f = f[y0:y1, x0:x1]
    w = int(h * f.shape[1] / f.shape[0]); f = cv2.resize(f, (w, h))
    cv2.rectangle(f, (0, 0), (w, 20), (0, 0, 0), -1)
    cv2.putText(f, label, (3, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (255, 255, 255), 1)
    return f


def make_sheets(df, tag, per_sheet=4):
    """df rows: video, dancer (A/B), start_s, end_s. Five frames: start-0.5, start, mid, end, end+1 s."""
    strips = []
    for i, r in enumerate(df.itertuples()):
        tr = load_tracks(f"outputs/{r.video}/{r.video}_tracks.npz"); fps = float(tr.meta["fps"])
        j = 0 if r.dancer == "A" else 1
        k = tr.kpts[:, j].astype(float); lv = D.level(k, np.nanmedian(D.trunk_len(k)))
        cap = cv2.VideoCapture(video_path(r.video)); row = []
        W, H = int(cap.get(3)), int(cap.get(4))
        T = [("-0.5", r.start_s - 0.5), ("start", r.start_s), ("mid", (r.start_s + r.end_s) / 2), ("end", r.end_s), ("+1.0", r.end_s + 1.0)]
        F = [int(np.clip(round(t * fps), 0, tr.n_frames - 1)) for _, t in T]
        pts = tr.kpts[F][..., :2].reshape(-1, 2); pts = pts[np.isfinite(pts).all(1)]
        box = None
        if len(pts):
            (x0, y0), (x1, y1) = pts.min(0), pts.max(0); cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            half_h = max(y1 - y0, (x1 - x0) / 1.4, H / 4) * 0.65; half_w = half_h * 1.2
            box = (int(max(0, cx - half_w)), int(max(0, cy - half_h)), int(min(W, cx + half_w)), int(min(H, cy + half_h)))
        for (name, _), fi in zip(T, F):
            row.append(tile(cap, tr, fi, j, f"{name} lv={lv[fi]:.2f}" if np.isfinite(lv[fi]) else f"{name} lv=-", box))
        hmin = min(x.shape[0] for x in row); row = [cv2.resize(x, (int(x.shape[1] * hmin / x.shape[0]), hmin)) for x in row]
        cap.release()
        s = np.hstack(row)
        cv2.putText(s, f"#{r.id} {r.video[:11]} {NAME[j]} t={r.start_s:.1f}-{r.end_s:.1f}s", (4, s.shape[0] - 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 2)
        strips.append(s)
    for p in range(0, len(strips), per_sheet):
        Wm = max(x.shape[1] for x in strips[p:p + per_sheet])
        strips[p:p + per_sheet] = [cv2.copyMakeBorder(x, 0, 4, 0, Wm - x.shape[1], cv2.BORDER_CONSTANT) for x in strips[p:p + per_sheet]]
        cv2.imwrite(str(OUT / f"check_{tag}_{p // per_sheet}.jpg"), np.vstack(strips[p:p + per_sheet]), [cv2.IMWRITE_JPEG_QUALITY, 80])


def sheet_round1(n=25, seed=0):
    ev = pd.read_csv("outputs/describe/events.csv"); d = ev[ev.kind == "descent"].reset_index(drop=True)
    d = d.sample(n, random_state=seed).sort_values(["video", "start_s"]).reset_index(drop=True)
    d.insert(0, "id", range(len(d))); d["verdict"] = ""; d["note"] = ""
    d[["id", "video", "dancer", "start_s", "end_s", "dur_s", "drop_bl", "peak_down_speed_bl_s", "in_contact", "verdict", "note"]] \
        .to_csv(OUT / "descent_check_sample.csv", index=False)
    make_sheets(d, "r1")


# ----------------------------------------------------------------------------------------------- revised detector
# Round 1 (outputs/falls/descent_check.csv): 14/25 of describe_duets.py's descents were false. Failure modes and
# the rule added against each:
#   kneeling / all fours / oblique lying read as "standing" (ankle keypoints far below the pelvis) -> UPRIGHT needs
#       the trunk vertical (shoulders >= 0.7 bl above hips) and at least one leg with a vertical shank
#       (ankle >= 0.45 bl below knee) and thigh (knee >= 0.35 bl below hip), held for >= 0.5 s;
#   inversions (feet above the pelvis, level < 0) read as "floor" -> FLOOR needs -0.4 < level < 0.6 for >= 0.3 s;
#   identity swaps and lost tracks / camera cuts -> the descender must be tracked in >= 90 % of the frames from
#       0.5 s before to the floor and the pelvis must not jump > 0.6 bl between consecutive frames;
#   a "drop" of the level with no downward pelvis motion (lying body re-read) -> the camera-stabilised pelvis
#       must move down by >= 0.5 bl.
UPRIGHT_MIN_S, FLOOR_MIN_S, MAX_DESCENT_S = 0.5, 0.3, 4.0


def _y(k, i):
    return np.where(k[:, i, 2] >= D.CONF, k[:, i, 1], np.nan)


def upright(k, sc):
    lv = D.level(k, sc)
    sh = np.nanmean(np.c_[_y(k, 5), _y(k, 6)], 1); hip = np.nanmean(np.c_[_y(k, 11), _y(k, 12)], 1)
    trunk_up = (hip - sh) / sc >= 0.7
    leg = np.zeros(len(k), bool)
    for h, kn, an in ((11, 13, 15), (12, 14, 16)):
        leg |= ((_y(k, an) - _y(k, kn)) / sc >= 0.45) & ((_y(k, kn) - _y(k, h)) / sc >= 0.35)
    return (np.nan_to_num(lv, nan=0) >= 1.2) & trunk_up & leg


def stabilise(p, M, t0, t1):
    """Pelvis points p[t0..t1] (px) mapped into frame t0's coordinates with the per-frame camera similarity
    transforms M[t] (frame t-1 -> t). NaN transforms are treated as identity."""
    out = np.full((t1 - t0 + 1, 2), np.nan); A = np.eye(3)       # A: frame t0 coords -> frame t coords
    for i, t in enumerate(range(t0, t1 + 1)):
        if i > 0 and M is not None and np.isfinite(M[t]).all():
            A = np.vstack([M[t], [0, 0, 1]]) @ A
        if np.isfinite(p[t]).all():
            out[i] = (np.linalg.inv(A) @ np.r_[p[t], 1])[:2]
    return out


def _sustained(mask, n):
    """True runs shorter than n frames removed."""
    out = np.zeros_like(mask)
    for a, b in D.episodes(mask, 1.0, min_s=n, merge_gap_s=0):
        out[a:b] = True
    return out


def detect_k(k, present, M, fps):
    """Revised descent rule on one body's keypoints k (T,17,3). Returns a list of candidate dicts (frames)."""
    sc = np.nanmedian(D.trunk_len(k)); ev = []
    lv = pd.Series(D.level(k, sc)).rolling(5, center=True, min_periods=3).median().to_numpy()
    up = _sustained(upright(k, sc), int(UPRIGHT_MIN_S * fps))
    fl = _sustained((lv < 0.6) & (lv > -0.4), int(FLOOR_MIN_S * fps))
    pel = D.pelvis(k); stand = np.flatnonzero(up); floor = np.flatnonzero(fl); i = 0
    while i < len(stand):
        t0 = stand[i]; nxt = floor[(floor > t0) & (floor <= t0 + MAX_DESCENT_S * fps)]
        if not len(nxt):
            i += 1; continue
        t1 = nxt[0]; t0 = stand[stand < t1].max(); i = np.searchsorted(stand, t1)
        a = max(0, t0 - int(0.5 * fps))
        pres = present[a:t1 + 1].mean()
        jump = np.nanmax(np.r_[np.linalg.norm(np.diff(pel[a:t1 + 1], axis=0), axis=1) / sc, 0])
        ps = stabilise(pel, M, t0, t1)
        drop = (np.nanmax(ps[-3:, 1]) - np.nanmin(ps[:3, 1])) / sc if np.isfinite(ps[:, 1]).sum() > 2 else np.nan
        ok = (pres >= 0.9) and (jump <= 0.6) and (np.nan_to_num(drop) >= 0.5)
        why = ";".join(w for w, c in (("gap", pres < 0.9), ("jump", jump > 0.6), ("no_drop", not np.nan_to_num(drop) >= 0.5)) if c)
        ev.append(dict(f0=int(t0), f1=int(t1), start_s=t0 / fps, end_s=t1 / fps, dur_s=(t1 - t0) / fps,
                       present=pres, max_jump_bl=jump, stab_drop_bl=drop, valid=ok, reject=why))
    return ev


def detect(vid, tr=None):
    tr = tr or load_tracks(f"outputs/{vid}/{vid}_tracks.npz"); fps = float(tr.meta["fps"]); ev = []
    for j, lab in ((0, "A"), (1, "B")):
        for e in detect_k(tr.kpts[:, j].astype(float), tr.present[:, j], tr.camera_M, fps):
            ev.append(dict(video=vid, dancer=lab, **e))
    return pd.DataFrame(ev), tr


def detect_all(vids):
    E = pd.concat([detect(v)[0] for v in vids], ignore_index=True)
    return E[[c for c in E.columns if c not in ('f0', 'f1')] + ['f0', 'f1']] if len(E) else E



def sheet_round2(seed=1, n_rej=10):
    """Out-of-sample check after the rules were fixed: every valid descent of the revised detector plus a random
    sample of candidates it rejected (recall check). The sheet does not show which is which."""
    vids = pd.read_csv("outputs/grammar/per_clip.csv").video.tolist()
    E = detect_all(vids); E.to_csv(OUT / "descents_v2_all.csv", index=False)
    S = pd.concat([E[E.valid], E[~E.valid].sample(min(n_rej, (~E.valid).sum()), random_state=seed)])
    S = S.sample(frac=1, random_state=seed).reset_index(drop=True); S.insert(0, "id", range(len(S)))
    S["verdict"] = ""; S["note"] = ""
    S.to_csv(OUT / "descent_check_v2_sample.csv", index=False)
    make_sheets(S, "r2")


# ----------------------------------------------------------------------------------------------- descriptors
LP_HZ = 3.0          # low-pass for the pelvis-height signal (15 fps: Nyquist 7.5 Hz)
G_BL = 9.81 / 0.50   # gravity in bl/s^2 if a trunk (shoulder-mid to hip-mid) is ~0.50 m: only a rough yardstick


def lowpass(x, fps, hz=None):
    b, a = butter(2, (hz or LP_HZ) / (fps / 2)); return filtfilt(b, a, x)


def fill(x, max_gap):
    s = pd.Series(x); return s.interpolate(limit=max_gap, limit_area="inside").to_numpy()


def sparc(speed, fps, fc=None, amp_th=0.05, pad=4):
    """Spectral arc length (Balasubramanian et al. 2015) of a speed profile; closer to 0 = smoother."""
    fc = fc or min(10.0, fps / 2)
    n = int(2 ** (np.ceil(np.log2(len(speed))) + pad)); f = np.arange(n) * fps / n
    M = np.abs(np.fft.fft(speed, n)); M = M / M.max()
    sel = f <= fc; f, M = f[sel], M[sel]
    above = np.flatnonzero(M >= amp_th); f, M = f[:above[-1] + 1], M[:above[-1] + 1]
    return -float(np.sum(np.sqrt((np.diff(f) / (f[-1] - f[0])) ** 2 + np.diff(M) ** 2)))


def ldlj(v, fps):
    """Log dimensionless jerk of a 1-D velocity profile (speed-based form); closer to 0 = smoother."""
    T = len(v) / fps; j = np.gradient(np.gradient(v)) * fps * fps
    return -float(np.log(T ** 3 / np.max(np.abs(v)) ** 2 * np.sum(j ** 2) / fps))


def pelvis_height(k, sc, M, a, b):
    """Camera-stabilised pelvis height (bl, up positive, 0 at frame a) over frames a..b; NaN gaps <= 3 filled."""
    ps = stabilise(D.pelvis(k), M, a, b)
    ref = ps[np.flatnonzero(np.isfinite(ps[:, 1]))[0], 1] if np.isfinite(ps[:, 1]).any() else np.nan
    return fill(-(ps[:, 1] - ref) / sc, 3), ps / sc


def yield_descriptors(k, M, fps, f0, f1, noise_sd=None, rng=None, keep=None):
    """Descriptors of one descent: upright frame f0 -> floor frame f1. Window f0-1 s .. f1+2 s."""
    sc0 = np.nanmedian(D.trunk_len(k)); T = len(k); tl = D.trunk_len(k)[upright(k, sc0)]
    sc = np.nanmedian(tl) if np.isfinite(tl).sum() >= 10 else sc0      # body length measured while upright
    a, b = max(0, f0 - int(fps)), min(T - 1, f1 + int(2 * fps))
    h, ps = pelvis_height(k, sc, M, a, b)
    first = np.flatnonzero(np.isfinite(h))[0] if np.isfinite(h).any() else len(h)
    if first > f0 - a or not np.isfinite(h[first: f1 - a + 1]).all():
        return None
    h, ps, a = h[first:], ps[first:], a + first          # drop a leading undetected stretch
    h = h - h[f0 - a]; ok = np.isfinite(h); hf = h.copy()
    last = np.flatnonzero(ok)[-1]; hf[: last + 1] = lowpass(fill(h[: last + 1], 99), fps)
    v = np.gradient(hf) * fps; acc = np.gradient(v) * fps
    seg = slice(f0 - a, min(len(h), f1 - a + int(1.0 * fps)))       # lowest point within 1 s after the floor frame
    hmin_i = (f0 - a) + int(np.nanargmin(hf[seg])); drop = -hf[hmin_i]
    if not drop > 0.3:                                  # no measurable downward pelvis motion in the image
        return None
    i10 = (f0 - a) + int(np.argmax(hf[f0 - a:] <= -0.1 * drop)); i90 = (f0 - a) + int(np.argmax(hf[f0 - a:] <= -0.9 * drop))
    ipk = i10 + int(np.argmin(v[i10:i90 + 1])); peak = -v[ipk]
    # braking: mean downward speed over the last 20 % of the drop, relative to the peak
    last20 = (hf[f0 - a:hmin_i + 1] <= -0.8 * drop); vl = -v[f0 - a:hmin_i + 1][last20]
    w0, w1 = max(0, i10 - int(0.5 * fps)), min(last + 1, i90 + int(0.5 * fps) + 1)
    if w1 - w0 < 6 or not np.isfinite(v[w0:w1]).all():
        return None
    sp = np.abs(v[w0:w1])
    out = dict(drop_bl=drop, dur_10_90_s=(i90 - i10) / fps, peak_down_v_bl_s=peak, peak_v_per_drop=peak / drop, t_peak_frac=(ipk - i10) / max(i90 - i10, 1),
               end_speed_ratio=float(np.mean(vl) / peak) if len(vl) else np.nan,
               peak_down_acc_g=float(-np.min(acc[f0 - a:ipk + 1]) / G_BL) if ipk > f0 - a else np.nan,
               peak_brake_acc_g=float(np.max(acc[ipk:min(len(acc), hmin_i + int(0.5 * fps))]) / G_BL),
               sparc=sparc(sp, fps), ldlj=ldlj(v[w0:w1], fps))
    if keep is not None:                            # profile aligned on the peak downward velocity, for plotting
        keep.append(dict(t=(np.arange(len(hf)) - ipk) / fps, h=hf, v=v))
    if noise_sd is not None:                        # noise floor: same metrics after adding keypoint-level jitter
        S, L = [], []
        for _ in range(30):
            hn = h[: last + 1] + rng.normal(0, noise_sd, last + 1)
            vn = np.gradient(lowpass(fill(hn, 99), fps)) * fps
            S.append(sparc(np.abs(vn[w0:w1]), fps)); L.append(ldlj(vn[w0:w1], fps))
        out.update(sparc_jitter_sd=float(np.std(S)), ldlj_jitter_sd=float(np.std(L)))
    # after reaching the floor (2 s from the floor frame f1): does the body keep moving?
    aft = slice(f1 - a, min(len(h), f1 - a + int(2 * fps)))
    pf = pd.DataFrame(ps[aft]).interpolate(limit_area="inside").to_numpy()
    spd = np.linalg.norm(np.gradient(np.c_[lowpass(fill(pf[:, 0], 99), fps), lowpass(fill(pf[:, 1], 99), fps)], axis=0), axis=1) * fps \
        if np.isfinite(pf).all(1).sum() > 9 and np.isfinite(pf).all() else np.full(len(pf), np.nan)
    lv = D.level(k, sc)[f1:f1 + int(2 * fps)]
    sh = (k[:, 5, :2] + k[:, 6, :2]) / 2; hp = (k[:, 11, :2] + k[:, 12, :2]) / 2; ax = sh - hp
    ang = np.degrees(np.arctan2(ax[:, 0], -ax[:, 1]))[f1:f1 + int(2 * fps)]   # trunk axis vs image vertical
    ang = ang[np.isfinite(ang)]; ang = np.degrees(np.unwrap(np.radians(ang))) if len(ang) else ang
    out.update(after_speed_med_bl_s=float(np.nanmedian(spd)), after_moving_frac=float(np.nanmean(spd > 0.5)) if np.isfinite(spd).any() else np.nan,
               after_max_level=float(np.nanmax(lv)) if np.isfinite(lv).any() else np.nan,
               after_trunk_rot_deg=float(np.max(ang) - np.min(ang)) if len(ang) > 3 else np.nan,
               after_tracked=float(np.isfinite(D.pelvis(k)[f1:f1 + int(2 * fps), 0]).mean()))
    return out


def still_noise(k, fps, sc):
    """Keypoint jitter of the pelvis height (bl): SD of (raw - 3 Hz low-pass) over upright frames."""
    y = D.pelvis(k)[:, 1] / sc; up = upright(k, sc)
    res = []
    for s0, s1 in D.episodes(up & np.isfinite(y), fps, min_s=1.0, merge_gap_s=0):
        yy = y[s0:s1]; res.append(yy - lowpass(yy, fps))
    return float(np.std(np.concatenate(res))) if res else np.nan


HAND_CONTACT = {("Rc9vIJt00vs_full", "A", 90.3): True, ("dGPRMNAECKM_full", "A", 33.5): True,
                ("hJQgFDsAms4_full", "A", 224.0): True, ("iOEZ3i9rgYM_full", "B", 174.1): True,
                ("kxztAr2tQmE_full", "B", 34.9): True, ("uS1JQ-LY8Fs_full", "A", 327.1): False,
                ("vinlwkaIW4c_full", "B", 143.5): True, ("vinlwkaIW4c_full", "B", 73.3): False,
                ("zQRF2sLK1vY", "A", 29.9): False, ("zQRF2sLK1vY", "A", 54.2): True, ("zQRF2sLK1vY", "B", 47.3): True}


def describe_all():
    rng = np.random.default_rng(0); PROF = {}
    vids = pd.read_csv("outputs/grammar/per_clip.csv").video.tolist()
    chk = pd.read_csv(OUT / "descent_check_v2.csv")
    E = detect_all(vids); E = E[E.valid].reset_index(drop=True); rows = []
    for vid, g in E.groupby("video"):
        tr = load_tracks(f"outputs/{vid}/{vid}_tracks.npz"); fps = float(tr.meta["fps"])
        st, _, dmin, _ = SG.frame_states(vid, return_dist=True)
        for r in g.itertuples():
            j = 0 if r.dancer == "A" else 1; k = tr.kpts[:, j].astype(float); sc = np.nanmedian(D.trunk_len(k))
            nsd = still_noise(k, fps, sc)
            P = PROF.setdefault("CI", []); d = yield_descriptors(k, tr.camera_M, fps, r.f0, r.f1, nsd, rng, P)
            if d is None:
                continue
            m = chk[(chk.video == vid) & (chk.dancer == r.dancer) & (np.abs(chk.start_s - r.start_s) < 0.1)]
            rows.append(dict(source="CI", video=vid, dancer=r.dancer, start_s=r.start_s, end_s=r.end_s,
                             hand_label=m.verdict.iloc[0] if len(m) else "", hand_note=m.note.iloc[0] if len(m) else "",
                             hand_contact=HAND_CONTACT.get((vid, r.dancer, round(r.start_s, 1))),
                             contact_frac=float(np.nanmean(np.nan_to_num(dmin[r.f0:r.f1 + 1], nan=9) < 0.25)),
                             noise_sd_bl=nsd, **d))
    R = pd.DataFrame(rows)
    # external: UR Fall (staged falls, lying down)
    ext = []
    for f in sorted((OUT / "urfall").glob("*.npz")):
        z = np.load(f); K = z["kpts"].astype(float); fps = float(z["fps"]); pres = np.isfinite(K[:, 11, 0])
        sc = np.nanmedian(D.trunk_len(K)); nsd = still_noise(K, fps, sc)
        cands = detect_k(K, pres, None, fps)            # the CI rule, for the record (feet often vanish when lying)
        y = z["label"]; up = upright(K, sc)
        src = "URFall-" + ("fall" if f.stem.startswith("fall") else "adl")
        # event from the dataset's own posture labels: last upright frame before the first 'transition' (0)
        # frame -> first 'lying' (1) frame
        if (y == 0).any() and (y == 1).any() and up[: np.argmax(y == 0) + 1].any():
            g0 = int(np.argmax(y == 0)); f0 = int(np.flatnonzero(up[: g0 + 1])[-1]); f1 = int(np.argmax(y == 1))
            d = yield_descriptors(K, None, fps, f0, f1, nsd, rng, PROF.setdefault(src, []))
        else:
            f0 = f1 = -1; d = None
        ext.append(dict(source=src, video=f.stem, dancer="", start_s=f0 / fps, end_s=f1 / fps, valid=d is not None,
                        reject="" if d is not None else ("no_upright_before" if f0 < 0 else "pelvis_lost_or_no_drop"),
                        ci_rule_candidates=len(cands), ci_rule_valid=sum(c["valid"] for c in cands), noise_sd_bl=nsd, **(d or {})))
    X = pd.DataFrame(ext)
    ALL = pd.concat([R, X[X.valid].drop(columns=["valid", "reject"])] if len(X) else [R], ignore_index=True)
    ALL.to_csv(OUT / "yield_descriptors.csv", index=False)
    if len(X):
        X.to_csv(OUT / "urfall_candidates.csv", index=False)
    return R, X, ALL, PROF


COLORS = {"CI": "#2a78d6", "URFall-fall": "#eb6834", "URFall-adl": "#1baf7a"}
NAMES = {"CI": "CI descents (valid, n={n})", "URFall-fall": "UR Fall: staged falls (n={n})", "URFall-adl": "UR Fall: lying down, ADL (n={n})"}
METRICS = [("dur_10_90_s", "10-90 % descent time (s)"), ("peak_down_v_bl_s", "peak downward speed (bl/s)"),
           ("peak_brake_acc_g", "peak braking acc. (~g)"), ("peak_v_per_drop", "peak speed / drop (1/s)"), ("end_speed_ratio", "speed in last 20 % / peak"),
           ("sparc", "SPARC (0 = smoothest)"), ("after_speed_med_bl_s", "pelvis speed, 2 s after (bl/s)")]


def plots(ALL, PROF):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": "#52514e",
                         "axes.labelcolor": "#0b0b0b", "xtick.color": "#52514e", "ytick.color": "#52514e"})
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.6))
    for src, P in PROF.items():
        for i, p in enumerate(P):
            lab = NAMES[src].format(n=len(P)) if i == 0 else None
            ax[0].plot(p["t"], p["h"] - p["h"][np.argmin(np.abs(p["t"]))], color=COLORS[src], lw=1.5, alpha=0.75, label=lab)
            ax[1].plot(p["t"], p["v"], color=COLORS[src], lw=1.5, alpha=0.75)
    for a, yl in zip(ax, ("pelvis height (bl), 0 at peak speed", "vertical pelvis velocity (bl/s)")):
        a.set_xlim(-1.5, 2.5); a.set_xlabel("time from peak downward speed (s)"); a.set_ylabel(yl)
        a.axvline(0, color="#c3c2b7", lw=0.8); a.axhline(0, color="#c3c2b7", lw=0.8)
    ax[0].legend(frameon=False, fontsize=8, loc="upper right")
    fig.suptitle("Going down: camera-stabilised pelvis height, 3 Hz low-pass, 15 fps", fontsize=10)
    fig.tight_layout(); fig.savefig(OUT / "profiles.png", dpi=130); plt.close(fig)

    fig, axs = plt.subplots(1, len(METRICS), figsize=(15, 3.2))
    srcs = [s for s in COLORS if s in set(ALL.source)]
    for a, (m, t) in zip(axs, METRICS):
        for x, s in enumerate(srcs):
            v = ALL.loc[ALL.source == s, m].dropna().to_numpy()
            a.scatter(x + np.random.default_rng(x).uniform(-0.15, 0.15, len(v)), v, s=22, color=COLORS[s], edgecolor="white", lw=0.8, zorder=3)
            if len(v):
                a.hlines(np.median(v), x - 0.3, x + 0.3, color="#0b0b0b", lw=2, zorder=4)
        a.set_xticks(range(len(srcs))); a.set_xticklabels(["CI", "fall", "lie down"][:len(srcs)] if srcs == list(COLORS)[:len(srcs)] else srcs)
        a.set_title(t, fontsize=8.5); a.grid(axis="y", color="#e8e7e3", lw=0.6)
    fig.tight_layout(); fig.savefig(OUT / "descriptors.png", dpi=130); plt.close(fig)


def report(R, X, ALL):
    from scipy.stats import mannwhitneyu
    md = ["# Yield: how CI dancers go down to the floor (falls.py)\n"]
    c1 = pd.read_csv(OUT / "descent_check.csv"); c2 = pd.read_csv(OUT / "descent_check_v2.csv")
    md += ["## Validation\n", "Round 1, describe_duets.py descents (25 random of 127):\n", c1.verdict.value_counts().to_frame("n").to_markdown(),
           "\n\nRound 2 (revised detector; all its valid descents + 10 random rejected candidates, sheet blind to the decision):\n",
           pd.crosstab(c2.valid, c2.verdict).to_markdown(), "\n"]
    cols = ["drop_bl", "dur_10_90_s", "peak_down_v_bl_s", "peak_v_per_drop", "t_peak_frac", "peak_down_acc_g", "peak_brake_acc_g", "end_speed_ratio",
            "sparc", "sparc_jitter_sd", "ldlj", "ldlj_jitter_sd", "after_speed_med_bl_s", "after_moving_frac", "after_max_level", "after_trunk_rot_deg", "after_tracked"]
    md += ["## Per CI descent\n", R[["video", "dancer", "start_s", "hand_label", "hand_contact"] + cols].round(2).to_markdown(index=False),
           "\n\n## Medians by source\n", ALL.groupby("source")[cols].median().round(2).T.to_markdown(),
           "\n\n## CI: floor vs low, contact vs solo (medians; n tiny)\n",
           R.groupby("hand_label")[cols].median().round(2).T.to_markdown(), "\n\n", R.groupby("hand_contact")[cols].median().round(2).T.to_markdown()]
    if len(X):
        rows = []
        for m, _ in METRICS + [("ldlj", ""), ("peak_down_acc_g", ""), ("drop_bl", ""), ("t_peak_frac", ""), ("after_moving_frac", ""), ("after_max_level", "")]:
            ci = ALL.loc[ALL.source == "CI", m].dropna()
            for s in ("URFall-fall", "URFall-adl"):
                o = ALL.loc[ALL.source == s, m].dropna()
                if len(o) > 2 and len(ci) > 2:
                    rows.append(dict(metric=m, vs=s, ci_median=ci.median(), other_median=o.median(), n_ci=len(ci), n_other=len(o),
                                     p_mannwhitney=mannwhitneyu(ci, o).pvalue))
        md += ["\n\n## CI vs UR Fall (Mann-Whitney, uncorrected)\n", pd.DataFrame(rows).round(3).to_markdown(index=False),
               "\n\nUR Fall sequences:\n", X[["source", "video", "valid", "reject", "ci_rule_candidates", "ci_rule_valid"]].to_markdown(index=False)]
    md += ["\n\n## Limits\n",
           "- 2-D monocular video: no forces, no ground contact, no depth. 'Braking' is image-plane pelvis deceleration in body lengths; the ~g figures assume a 0.5 m trunk and are a yardstick only.",
           "- 15 fps and a 3 Hz low-pass: impacts shorter than ~0.2 s are smeared, so SPARC / jerk cannot see a hard landing; jerk-based smoothness is weakly identified at this frame rate.",
           "- The valid CI set is precision-first: about half of the rejected candidates were real descents lost to tracking gaps and identity swaps (floor tangles, carries), so fast or entangled descents are under-represented.",
           "- 'Floor' (pelvis < 0.6 bl above own feet) does not separate a deep squat from sitting or lying: 7 of the 11 valid descents end in a squat or kneel.",
           "- UR Fall falls are staged by volunteers onto a mattress, filmed frontally with a static camera; drops are larger (standing to lying) and perspective differs. Body-length units do not remove that.",
           "- n = 11 CI descents, 8 falls, 3 lying-down sequences: every comparison is descriptive."]
    (OUT / "report.md").write_text("\n".join(md))
    return "\n".join(md)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "sheet"
    if cmd == "sheet":
        sheet_round1()
    elif cmd == "sheet2":
        sheet_round2()
    elif cmd == "sensitivity":                      # same comparison with a 5 Hz low-pass
        LP_HZ = 5.0; R, X, ALL, PROF = describe_all()
        print(ALL.groupby("source")[["peak_down_v_bl_s", "peak_v_per_drop", "peak_brake_acc_g", "end_speed_ratio", "sparc", "ldlj", "sparc_jitter_sd", "ldlj_jitter_sd"]].median().round(2).T)
        LP_HZ = 3.0; describe_all()
    elif cmd == "describe":
        R, X, ALL, PROF = describe_all(); plots(ALL, PROF); print(report(R, X, ALL))

