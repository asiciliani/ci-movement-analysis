"""
Demo video: a CI duet with both tracked skeletons on the left and, on the right, what the descriptive pipeline
reads at each moment (duet state, where they touch, who is on top, each dancer's height level), plus the state
timeline of the whole excerpt. Meant for showing the project in one minute, not for analysis.

Same measures as the reported results: states from state_grammar.frame_states (with the SEP_BL release rule),
contact regions from describe.contact_regions, weight sharing from describe.aerial_support, levels from
describe.level. Labels in Spanish.

Usage:  python analyses/demo_video.py [video_id] [start_s] [duration_s]
        (default: kMkJpfUGZz8_full 65 45, the most varied 45 s of the corpus by a state-mix score)
Output: outputs/demo/<video_id>_<start>s.mp4 (gitignored: third-party footage, shown privately only)
"""
from __future__ import annotations

import glob
import subprocess
import sys
from pathlib import Path
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

import state_grammar as SG
from src.io.tracks import load_tracks
from src.analysis import describe as D
from src.pose.pose_detector import SKELETON_EDGES

OUT = Path("outputs/demo"); OUT.mkdir(parents=True, exist_ok=True)
H, PANEL_W = 540, 470
COL = {"A": (66, 160, 255), "B": (255, 150, 40)}                                   # RGB
STATE = {"apart": ("separados", (150, 150, 150)), "near": ("cerca, sin tocarse", (120, 190, 230)),
         "contact": ("en contacto", (90, 200, 120)), "share": ("peso compartido", (235, 90, 90)),
         "floor": ("en el piso", (190, 130, 230)), None: ("sin datos", (60, 60, 60))}
REGION_ES = {"head": "cabeza", "torso": "torso", "arm": "brazo", "hand": "mano", "leg": "pierna", "foot": "pie"}
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(size, bold=False):
    return ImageFont.truetype(FONT_B if bold else FONT, size)


def measures(vid):
    st, fps, dmin, both = SG.frame_states(vid, return_dist=True)
    tr = load_tracks(f"outputs/{vid}/{vid}_tracks.npz")
    kA, kB = tr.kpts[:, 0].astype(float), tr.kpts[:, 1].astype(float)
    sA, sB = np.nanmedian(D.trunk_len(kA)), np.nanmedian(D.trunk_len(kB))
    _, rA, rB, _ = D.contact_regions(kA, kB, (sA + sB) / 2)
    touching = np.isin(st.astype(str), ["contact", "share", "floor"]) & (np.nan_to_num(dmin, nan=9) < SG.HYST_OUT)
    top = D.aerial_support(kA, kB, sA, sB, st == "share")
    return dict(st=st, fps=fps, tr=tr, rA=rA, rB=rB, touching=touching, top=top,
                lvA=D.level(kA, sA), lvB=D.level(kB, sB))


def draw_skeletons(frame, tr, i):
    for j, lab in ((0, "A"), (1, "B")):
        if not tr.present[i, j]:
            continue
        k = tr.kpts[i, j]; c = COL[lab][::-1]                                       # BGR for cv2
        for a, b in SKELETON_EDGES:
            if k[a, 2] > 0.3 and k[b, 2] > 0.3:
                cv2.line(frame, tuple(k[a, :2].astype(int)), tuple(k[b, :2].astype(int)), c, 3, cv2.LINE_AA)
        if k[0, 2] > 0.3:
            cv2.putText(frame, lab, (int(k[0, 0]) - 8, int(k[0, 1]) - 18), cv2.FONT_HERSHEY_SIMPLEX, 0.9, c, 2, cv2.LINE_AA)
    return frame


def level_bar(d, x, y, label, lv, color):
    d.text((x, y), label, font=font(16, True), fill=color)
    x0, w, h = x + 30, 150, 14
    d.rectangle([x0, y + 3, x0 + w, y + 3 + h], outline=(90, 90, 90))
    if np.isfinite(lv):
        frac = float(np.clip(lv / 1.8, 0, 1))
        d.rectangle([x0, y + 3, x0 + int(w * frac), y + 3 + h], fill=color)
        txt = "de pie" if lv >= 1.2 else "en el piso" if lv < 0.6 else "a media altura"
    else:
        txt = "no detectado"
    d.text((x0 + w + 10, y), txt, font=font(15), fill=(220, 220, 220))


def panel(m, i, a, b, t_rel, dur):
    img = Image.new("RGB", (PANEL_W, H), (24, 24, 28)); d = ImageDraw.Draw(img)
    d.text((22, 18), "Contact Improvisation:", font=font(20, True), fill=(240, 240, 240))
    d.text((22, 44), "lo que mide la computadora", font=font(20), fill=(200, 200, 200))
    s = m["st"][i]; name, col = STATE.get(s, STATE[None])
    d.text((22, 92), "Estado del dúo", font=font(15), fill=(160, 160, 160))
    d.rounded_rectangle([22, 114, PANEL_W - 22, 162], radius=10, fill=col)
    d.text((36, 124), name, font=font(24, True), fill=(20, 20, 20))
    y = 182
    if m["touching"][i] and m["rA"][i]:
        d.text((22, y), "Se tocan con", font=font(15), fill=(160, 160, 160))
        d.text((22, y + 20), f"A: {REGION_ES[m['rA'][i]]}   ·   B: {REGION_ES[m['rB'][i]]}", font=font(19), fill=(240, 240, 240))
    if s == "share" and np.isfinite(m["top"][i]) and m["top"][i] != 0:
        who = "A" if m["top"][i] > 0 else "B"
        d.text((22, y + 50), f"{who} está arriba, cargado por {'B' if who == 'A' else 'A'}", font=font(19, True), fill=COL[who])
    d.text((22, 272), "Altura de cada bailarín", font=font(15), fill=(160, 160, 160))
    level_bar(d, 22, 296, "A", m["lvA"][i], COL["A"]); level_bar(d, 22, 324, "B", m["lvB"][i], COL["B"])
    # timeline of the excerpt
    d.text((22, 372), f"Los {dur:.0f} s del fragmento", font=font(15), fill=(160, 160, 160))
    x0, x1, ty = 22, PANEL_W - 22, 396
    n = b - a
    for k in range(n):
        xa = x0 + int((x1 - x0) * k / n); xb = x0 + int((x1 - x0) * (k + 1) / n)
        d.rectangle([xa, ty, max(xa, xb - 1), ty + 26], fill=STATE.get(m["st"][a + k], STATE[None])[1])
    xc = x0 + int((x1 - x0) * (i - a) / n)
    d.line([xc, ty - 5, xc, ty + 31], fill=(255, 255, 255), width=3)
    lx, ly = 22, 436
    for key in ("apart", "near", "contact", "share", "floor"):
        nm, c = STATE[key]
        w = d.textlength(nm, font=font(13)) + 30
        if lx + w > PANEL_W - 10:
            lx, ly = 22, ly + 22
        d.rectangle([lx, ly + 3, lx + 12, ly + 15], fill=c); d.text((lx + 17, ly), nm, font=font(13), fill=(200, 200, 200)); lx += w
    d.text((22, H - 40), "Video público · pose 2-D (YOLOv8) · detectores validados a ojo", font=font(12), fill=(130, 130, 130))
    d.text((22, H - 22), f"t = {t_rel:4.1f} s", font=font(12), fill=(130, 130, 130))
    return np.asarray(img)[:, :, ::-1]                                                # BGR


def main(vid="kMkJpfUGZz8_full", start_s=65.0, dur_s=45.0):
    m = measures(vid); fps = m["fps"]
    a = int(start_s * fps); b = min(int((start_s + dur_s) * fps), len(m["st"]))
    vp = [x for d in ("videos", "videos/full", "videos/external") for x in sorted(glob.glob(f"{d}/{vid}.*"))][0]
    cap = cv2.VideoCapture(vp); cap.set(cv2.CAP_PROP_POS_FRAMES, a)
    ok, f = cap.read(); W = int(round(f.shape[1] * H / f.shape[0])); W += W % 2
    out = OUT / f"{vid}_{int(start_s)}s.mp4"
    enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24",
                            "-s", f"{W + PANEL_W}x{H}", "-r", f"{fps}", "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                            "-crf", "23", str(out)], stdin=subprocess.PIPE)
    for i in range(a, b):
        if i > a:
            ok, f = cap.read()
            if not ok:
                break
        left = cv2.resize(draw_skeletons(f, m["tr"], i), (W, H))
        enc.stdin.write(np.hstack([left, panel(m, i, a, b, (i - a) / fps, dur_s)]).tobytes())
    cap.release(); enc.stdin.close(); enc.wait()
    print(f"[demo] {out} ({(b - a) / fps:.0f} s)")


if __name__ == "__main__":
    args = sys.argv[1:]
    main(*(args[:1] + [float(x) for x in args[1:3]]))
