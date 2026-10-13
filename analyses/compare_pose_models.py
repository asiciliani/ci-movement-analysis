"""
Compare 2-D pose models on the hard frames of the CI corpus (AUDIT row 51).

The current pipeline (YOLOv8n-pose + BoT-SORT) loses one dancer when the bodies are entangled
(embrace, carry, floor tangle, dark clothing on a dark stage; AUDIT rows 42-43). This script
builds a small frame test set, runs one candidate model at a time on it and renders overlay
contact sheets for a by-eye verdict.

    .venv/bin/python analyses/compare_pose_models.py select              # pick frames, write frames/ + gt sheets
    .venv/bin/python analyses/compare_pose_models.py run <model>         # one model per process (RAM)
    .venv/bin/python analyses/compare_pose_models.py render <model>      # overlay sheets for the by-eye check
    .venv/bin/python analyses/compare_pose_models.py compare hard <model> <model> ...   # one row per frame, for the verdicts
    .venv/bin/python analyses/compare_pose_models.py score               # table from preds + verdicts.csv

Ground truth and by-eye verdicts are typed by hand into outputs/pose_models/testset.csv
(columns gt_ok / gt_note) and outputs/pose_models/verdicts.csv (frame id x model -> 2/1/0).
"""
from __future__ import annotations

import glob
import json
import sys
import time
from pathlib import Path

import cv2
import numpy as np
import pandas as pd

OUT = Path("outputs/pose_models")
FR = OUT / "frames"
WEIGHTS = Path("data_external/pose_models")
SEED = 0
N_HARD_EXTRA = 5      # per duet, besides the false-release frames
N_ORD = 4             # per duet
NT = int(__import__('os').environ.get('POSE_NT', 2))   # threads per model: the machine is shared, 4 threads oversubscribe and run slower
EDGES = [(5, 6), (5, 7), (7, 9), (6, 8), (8, 10), (5, 11), (6, 12), (11, 12), (11, 13), (13, 15), (12, 14), (14, 16), (0, 5), (0, 6)]
COLS = [(255, 160, 0), (0, 140, 255), (0, 220, 0), (220, 0, 220), (0, 220, 220), (128, 128, 255)]


def video_path(v):
    return (sorted(glob.glob(f"videos/{v}.*")) + sorted(glob.glob(f"videos/full/{v}.*")))[0]


def read_frame(v, fi):
    cap = cv2.VideoCapture(video_path(v)); cap.set(cv2.CAP_PROP_POS_FRAMES, fi); ok, f = cap.read(); cap.release()
    return f if ok else None


# ----------------------------------------------------------------------------------------- select
def select():
    import state_grammar as SG
    from src.io.tracks import load_tracks
    FR.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)
    vids = pd.read_csv("outputs/grammar/per_clip.csv").video.tolist()
    c1 = pd.read_csv("outputs/grammar/contact_check.csv"); c2 = pd.read_csv("outputs/grammar/contact_check_v2.csv")
    fr_rows = pd.concat([c1[c1.verdict.isin(["false_release", "false_contact"])].assign(src="check1"),
                         c2[(c2.verdict == "false_release") | c2.note.str.contains("lost")].assign(src="check2")])
    rows = []
    for v in vids:
        tr = load_tracks(f"outputs/{v}/{v}_tracks.npz")
        st, fps, dmin, both = SG.frame_states(v, return_dist=True)
        T = len(st)
        kc = np.nan_to_num(np.nanmean(tr.kpts[..., 2], axis=2), nan=0.0)        # (T,2) mean kpt conf
        kc[~tr.present] = 0.0
        weak = kc.min(1)                                                         # 0 if one dancer missing
        ctx = pd.Series(np.where(pd.isna(st), None, st)).ffill(limit=int(3 * fps)).bfill(limit=int(1 * fps)).to_numpy()
        entangled = np.isin(ctx.astype(str), ["contact", "share", "floor"])
        used = []

        def far(fi, gap=2.0):
            return all(abs(fi - u) > gap * fps for u in used)

        # (a) the false releases of the hand check: worst frame inside the gap
        for _, r in fr_rows[fr_rows.video == v].iterrows():
            rec = r.recontact_s if "recontact_s" in r and np.isfinite(r.get("recontact_s", np.nan)) else 1.0
            a = int(round(r.release_s * fps)); b = int(round((r.release_s + max(rec, 0.3)) * fps)) + 1
            a, b = max(a - 2, 0), min(b + 2, T)
            fi = a + int(np.argmin(weak[a:b]))
            if not far(fi, 0.5):
                continue
            used.append(fi)
            rows.append(dict(video=v, frame=fi, kind="hard", src=f"{r.src}#{int(r.id)}", state=ctx[fi], tracks_n=int(tr.present[fi].sum()),
                             weak_conf=round(float(weak[fi]), 2), note_check=r.note))
        # (b) more entangled frames where the tracks lose a dancer or are weak
        cand = np.flatnonzero(entangled & (weak < 0.35))
        rng.shuffle(cand); k = 0
        for fi in cand:
            if k >= N_HARD_EXTRA:
                break
            if far(fi, 3.0):
                used.append(fi); k += 1
                rows.append(dict(video=v, frame=int(fi), kind="hard", src="entangled_weak", state=ctx[fi],
                                 tracks_n=int(tr.present[fi].sum()), weak_conf=round(float(weak[fi]), 2), note_check=""))
        # (c) ordinary frames: both tracked, standing, apart or near
        cand = np.flatnonzero(both & np.isin(st.astype(str), ["apart", "near"]) & (weak > 0.6))
        rng.shuffle(cand); k = 0
        for fi in cand:
            if k >= N_ORD:
                break
            if far(fi, 3.0):
                used.append(fi); k += 1
                rows.append(dict(video=v, frame=int(fi), kind="ordinary", src="ordinary", state=st[fi],
                                 tracks_n=2, weak_conf=round(float(weak[fi]), 2), note_check=""))
    df = pd.DataFrame(rows).sort_values(["kind", "video", "frame"]).reset_index(drop=True)
    df.insert(0, "id", range(len(df))); df["gt_ok"] = ""; df["gt_note"] = ""
    for r in df.itertuples():
        f = read_frame(r.video, r.frame)
        cv2.imwrite(str(FR / f"{r.id:03d}.jpg"), f, [cv2.IMWRITE_JPEG_QUALITY, 92])
    df.to_csv(OUT / "testset.csv", index=False)
    print(df.groupby(["kind"]).size(), df.groupby("src").size().head(40))
    sheets("tracks")


# ----------------------------------------------------------------------------------------- models
def load_model(name):
    """Return f(img_bgr) -> (kpts (N,17,3) float, boxes (N,4) or None)."""
    import torch
    torch.set_num_threads(NT)
    if not name.startswith(("yolo", "vitpose")):                     # rtmlib builds its ORT sessions with default options
        import onnxruntime as ort
        _S = ort.InferenceSession

        def _session(*a, **k):
            so = ort.SessionOptions(); so.intra_op_num_threads = NT
            return _S(*a, sess_options=so, **k)
        ort.InferenceSession = _session
    if name.startswith("yolo"):
        from ultralytics import YOLO
        base, _, size = name.partition("@")                               # e.g. yolo11m-pose@1280 = larger inference size
        w = "yolov8n-pose.pt" if base == "yolov8n-pose" else str(WEIGHTS / f"{base}.pt")
        m = YOLO(w); imgsz = int(size or 640)

        def f(img):
            r = m.predict(img, conf=0.25, imgsz=imgsz, verbose=False)[0]
            if r.keypoints is None or len(r.boxes) == 0:
                return np.zeros((0, 17, 3)), np.zeros((0, 4))
            k = r.keypoints.data.cpu().numpy()
            return k, r.boxes.xyxy.cpu().numpy()
        return f
    if name.startswith("rtmo"):
        from rtmlib import RTMO
        url = {"rtmo-l": "https://download.openmmlab.com/mmpose/v1/projects/rtmo/onnx_sdk/rtmo-l_16xb16-600e_body7-640x640-b37118ce_20231211.zip",
               "rtmo-m": "https://download.openmmlab.com/mmpose/v1/projects/rtmo/onnx_sdk/rtmo-m_16xb16-600e_body7-640x640-39e78cc4_20231211.zip"}[name]
        m = RTMO(url, model_input_size=(640, 640), backend="onnxruntime", device="cpu", score_thr=0.3)

        def f(img):
            k, s = m(img)
            if len(k) == 0:
                return np.zeros((0, 17, 3)), None
            return np.concatenate([k, s[..., None]], -1), None
        return f
    if name.startswith("rtmpose") or name.startswith("rtmw"):
        from rtmlib import YOLOX, RTMPose
        base = "https://download.openmmlab.com/mmpose/v1/projects/rtmposev1/onnx_sdk/"
        det = YOLOX(base + "yolox_x_8xb8-300e_humanart-a39d44ed.zip", model_input_size=(640, 640), backend="onnxruntime", device="cpu",
                    score_thr=0.3)
        if name == "rtmpose-x":
            pose = RTMPose(base + "rtmpose-x_simcc-body7_pt-body7_700e-384x288-71d7b7e9_20230629.zip", model_input_size=(288, 384),
                           backend="onnxruntime", device="cpu")
        elif name == "rtmpose-m":
            pose = RTMPose(base + "rtmpose-m_simcc-body7_pt-body7_420e-256x192-e48f03d0_20230504.zip", model_input_size=(192, 256),
                           backend="onnxruntime", device="cpu")
        else:   # rtmw-x: whole body (133 kpts, DWPose-style distillation; first 17 = COCO body)
            pose = RTMPose("https://download.openmmlab.com/mmpose/v1/projects/rtmw/onnx_sdk/rtmw-dw-x-l_simcc-cocktail14_270e-384x288_20231122.zip",
                           model_input_size=(288, 384), backend="onnxruntime", device="cpu")

        def f(img):
            b = det(img)
            if len(b) == 0:
                return np.zeros((0, 17, 3)), np.zeros((0, 4))
            k, s = pose(img, bboxes=b)
            return np.concatenate([k[:, :17], s[:, :17, None]], -1), np.asarray(b)
        return f
    if name.startswith("vitpose"):
        import torch
        from transformers import AutoProcessor, RTDetrForObjectDetection, VitPoseForPoseEstimation
        dp = AutoProcessor.from_pretrained("PekingU/rtdetr_r50vd_coco_o365")
        dm = RTDetrForObjectDetection.from_pretrained("PekingU/rtdetr_r50vd_coco_o365").eval()
        repo = {"vitpose-plus-base": "usyd-community/vitpose-plus-base", "vitpose-plus-large": "usyd-community/vitpose-plus-large",
                "vitpose-base": "usyd-community/vitpose-base-simple"}[name]
        pp = AutoProcessor.from_pretrained(repo)
        pm = VitPoseForPoseEstimation.from_pretrained(repo).eval()

        @torch.no_grad()
        def f(img):
            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB); H, W = rgb.shape[:2]
            inp = dp(images=rgb, return_tensors="pt")
            res = dp.post_process_object_detection(dm(**inp), target_sizes=torch.tensor([(H, W)]), threshold=0.3)[0]
            b = res["boxes"][res["labels"] == 0].numpy()
            if len(b) == 0:
                return np.zeros((0, 17, 3)), np.zeros((0, 4))
            bx = b.copy(); bx[:, 2:] -= bx[:, :2]                                     # xywh for the pose processor
            inp = pp(rgb, boxes=[bx], return_tensors="pt")
            kw = {"dataset_index": torch.zeros(len(b), dtype=torch.long)} if "plus" in name else {}
            out = pm(**inp, **kw)
            pr = pp.post_process_pose_estimation(out, boxes=[bx])[0]
            k = np.stack([np.concatenate([p["keypoints"].numpy(), p["scores"].numpy()[:, None]], 1) for p in pr])
            return k, b
        return f
    raise ValueError(name)


def run(name):
    df = pd.read_csv(OUT / "testset.csv")
    f = load_model(name)
    f(cv2.imread(str(FR / "000.jpg")))                                                 # warm-up
    preds, times, cpu = {}, [], []
    for r in df.itertuples():
        img = cv2.imread(str(FR / f"{r.id:03d}.jpg"))
        t0, c0 = time.perf_counter(), time.process_time(); k, b = f(img)
        times.append(time.perf_counter() - t0); cpu.append(time.process_time() - c0)   # cpu: summed over threads, robust to machine load
        preds[str(r.id)] = dict(k=np.asarray(k, float).round(2).tolist(), b=None if b is None else np.asarray(b, float).round(1).tolist())
    (OUT / "preds").mkdir(exist_ok=True)
    json.dump(dict(model=name, sec=times, cpu=cpu, preds=preds), open(OUT / "preds" / f"{name}.json", "w"))
    print(name, f"wall {np.median(times):.3f} s/frame, cpu {np.median(cpu):.3f} core-s/frame", flush=True)


def timing(name, n=12):
    """Timing only, on every 9th test frame; run when the machine is quiet. Appends to timing.csv."""
    df = pd.read_csv(OUT / "testset.csv").iloc[::9].head(n)
    f = load_model(name); imgs = [cv2.imread(str(FR / f"{i:03d}.jpg")) for i in df.id]
    f(imgs[0]); t = []
    for im in imgs:
        t0 = time.perf_counter(); f(im); t.append(time.perf_counter() - t0)
    load = open("/proc/loadavg").read().split()[0]
    with open(OUT / "timing.csv", "a") as fh:
        fh.write(f"{name},{NT},{np.median(t):.3f},{np.mean(t):.3f},{load}\n")
    print(name, f"median {np.median(t):.3f} s/frame, load {load}", flush=True)


# ----------------------------------------------------------------------------------------- render
def draw(img, k, col, thr=0.3, lw=2):
    for a, b in EDGES:
        if k[a, 2] > thr and k[b, 2] > thr:
            cv2.line(img, tuple(int(x) for x in k[a, :2]), tuple(int(x) for x in k[b, :2]), col, lw, cv2.LINE_AA)
    for p in k:
        if p[2] > thr:
            cv2.circle(img, (int(p[0]), int(p[1])), lw + 1, col, -1)


def crop_boxes():
    """Region around the two dancers per test frame (current tracks +-1 s, expanded), so that sheets zoom on them."""
    f = OUT / "crops.json"
    if f.exists():
        return json.load(open(f))
    from src.io.tracks import load_tracks
    df = pd.read_csv(OUT / "testset.csv"); out = {}
    for v, d in df.groupby("video"):
        tr = load_tracks(f"outputs/{v}/{v}_tracks.npz"); W, H = tr.meta["width"], tr.meta["height"]
        for r in d.itertuples():
            a, b = max(r.frame - 15, 0), min(r.frame + 16, tr.n_frames)
            k = tr.kpts[a:b].reshape(-1, 3); k = k[np.isfinite(k[:, 0]) & (k[:, 2] > 0.3)]
            if len(k) < 10:
                out[str(r.id)] = [0, 0, W, H]; continue
            x1, y1, x2, y2 = k[:, 0].min(), k[:, 1].min(), k[:, 0].max(), k[:, 1].max()
            s = max(x2 - x1, y2 - y1, 0.25 * H) * 0.9; cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
            out[str(r.id)] = [int(max(cx - s * 1.1, 0)), int(max(cy - s, 0)), int(min(cx + s * 1.1, W)), int(min(cy + s, H))]
    json.dump(out, open(f, "w"))
    return out


def tile(i, people, label, w=330, crop=None):
    img = cv2.imread(str(FR / f"{i:03d}.jpg"))
    lw = max(2, img.shape[1] // 400)
    if crop is not None:
        lw = max(1, int(round(lw * (crop[2] - crop[0]) / img.shape[1])) + 1)
    for j, k in enumerate(people):
        draw(img, np.asarray(k), COLS[j % len(COLS)], lw=lw)
    if crop is not None:
        img = img[crop[1]:crop[3], crop[0]:crop[2]]
    img = cv2.resize(img, (w, int(w * img.shape[0] / img.shape[1])))
    cv2.rectangle(img, (0, 0), (w, 18), (0, 0, 0), -1)
    cv2.putText(img, label, (3, 13), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (255, 255, 255), 1)
    return img


def sheets(name, per=20, cols=5):
    df = pd.read_csv(OUT / "testset.csv")
    if name == "tracks":
        from src.io.tracks import load_tracks
        cache = {}

        def get(r):
            if r.video not in cache:
                cache[r.video] = load_tracks(f"outputs/{r.video}/{r.video}_tracks.npz")
            tr = cache[r.video]
            return [tr.kpts[r.frame, j] for j in range(2) if tr.present[r.frame, j]]
    else:
        P = json.load(open(OUT / "preds" / f"{name}.json"))["preds"]
        get = lambda r: P[str(r.id)]["k"]
    (OUT / "sheets").mkdir(exist_ok=True)
    tiles = []; C = crop_boxes() if name != "tracks" else {}
    for r in df.itertuples():
        ppl = [np.asarray(k) for k in get(r)]
        ppl = [k for k in ppl if (k[:, 2] > 0.3).sum() >= 3]                         # draw only skeletons with >= 3 kpts
        tiles.append(tile(r.id, ppl, f"#{r.id} {r.kind[0]} {r.video[:6]} n={len(ppl)}", crop=C.get(str(r.id))))
    for p in range(0, len(tiles), per):
        T = tiles[p:p + per]
        H = max(t.shape[0] for t in T); T = [cv2.copyMakeBorder(t, 0, H - t.shape[0] + 3, 0, 3, cv2.BORDER_CONSTANT) for t in T]
        while len(T) % cols:
            T.append(np.zeros_like(T[0]))
        grid = np.vstack([np.hstack(T[c:c + cols]) for c in range(0, len(T), cols)])
        cv2.imwrite(str(OUT / "sheets" / f"{name}_{p // per}.jpg"), grid, [cv2.IMWRITE_JPEG_QUALITY, 85])


def compare(models, kind="hard", per=5, w=235):
    """One row per test frame, one column per model (same zoom): the sheets used for the by-eye verdicts."""
    df = pd.read_csv(OUT / "testset.csv"); df = df[(df.kind == kind) & (df.gt_ok == 1)]
    P = {m: json.load(open(OUT / "preds" / f"{m}.json"))["preds"] for m in models}; C = crop_boxes()
    (OUT / "compare").mkdir(exist_ok=True); rows = []
    for r in df.itertuples():
        T = []
        for m in models:
            ppl = [np.asarray(k) for k in P[m][str(r.id)]["k"]]; ppl = [k for k in ppl if (k[:, 2] > 0.3).sum() >= 3]
            T.append(tile(r.id, ppl, f"#{r.id} {m[:22]} n={len(ppl)}", w=w, crop=C.get(str(r.id))))
        H = max(t.shape[0] for t in T)
        rows.append(np.hstack([cv2.copyMakeBorder(t, 0, H - t.shape[0] + 3, 0, 3, cv2.BORDER_CONSTANT) for t in T]))
    for p in range(0, len(rows), per):
        cv2.imwrite(str(OUT / "compare" / f"{kind}_{p // per:02d}.jpg"), np.vstack(rows[p:p + per]), [cv2.IMWRITE_JPEG_QUALITY, 85])


# ----------------------------------------------------------------------------------------- score
def dancers_auto(k, crop, thr=0.3, min_kp=6):
    """Automatic count of distinct posed people inside the dancers' region: skeletons with >= min_kp keypoints
    above thr, centred inside the crop (drops bystanders), duplicates on the same body merged. Returns kept list."""
    keep = []
    for p in sorted((np.asarray(p, float) for p in k), key=lambda p: -np.mean(p[:, 2])):
        ok = p[:, 2] > thr
        if ok.sum() < min_kp:
            continue
        c = p[ok, :2].mean(0)
        if not (crop[0] <= c[0] <= crop[2] and crop[1] <= c[1] <= crop[3]):
            continue
        size = np.sqrt(np.prod(np.ptp(p[ok, :2], axis=0)) + 1e-6)
        dup = False
        for q in keep:
            j = ok & (q[:, 2] > thr)
            if j.sum() >= 4 and np.mean(np.linalg.norm(p[j, :2] - q[j, :2], axis=1)) < 0.15 * size:
                dup = True; break
        if not dup:
            keep.append(p)
    return keep


def n_plausible(k, thr=0.3, min_kp=6):
    """Skeletons with >= min_kp keypoints above thr (a 'posed' person), anywhere in the frame."""
    return sum(int((np.asarray(p)[:, 2] > thr).sum() >= min_kp) for p in k)


def score():
    """Table per model: by-eye verdicts (verdicts.csv), automatic count, keypoint confidence, duplicates, time."""
    df = pd.read_csv(OUT / "testset.csv"); df = df[df.gt_ok == 1]
    V = pd.read_csv(OUT / "verdicts.csv").set_index("id"); C = crop_boxes()
    tm = pd.read_csv(OUT / "timing.csv", names=["model", "nt", "med", "mean", "load"]).groupby("model").med.min() \
        if (OUT / "timing.csv").exists() else {}
    n_corpus = sum(len(np.load(f"outputs/{v}/{v}_tracks.npz")["present"]) for v in pd.read_csv("outputs/grammar/per_clip.csv").video)
    rows = []
    for pf in sorted((OUT / "preds").glob("*.json")):
        J = json.load(open(pf)); m = J["model"]; P = J["preds"]; r = dict(model=m)
        for kind in ("hard", "ordinary"):
            d = df[df.kind == kind]
            K = [dancers_auto(P[str(i)]["k"], C[str(i)]) for i in d.id]
            raw = [sum(1 for p in P[str(i)]["k"] if (np.asarray(p)[:, 2] > 0.3).sum() >= 6
                       and C[str(i)][0] <= np.asarray(p)[np.asarray(p)[:, 2] > 0.3, 0].mean() <= C[str(i)][2]) for i in d.id]
            r[f"{kind}_eye2"] = f"{int((V.loc[d.id, m] == 2).sum())}/{len(d)}" if m in V.columns else ""
            r[f"{kind}_auto2"] = f"{sum(len(k) >= 2 for k in K)}/{len(d)}"
            # mean keypoint confidence of the two best skeletons in the dancers' region; a missing dancer counts as 0
            r[f"{kind}_conf2"] = round(float(np.mean([np.mean(sorted([p[:, 2].mean() for p in k], reverse=True)[:2] + [0.0] * max(0, 2 - len(k)))
                                                      for k in K])), 2)
            r[f"{kind}_dup"] = int(sum(a - len(k) for a, k in zip(raw, K)))        # duplicate skeletons on the same body
        r["s_frame"] = float(tm.get(m, np.nan)) if len(tm) else np.nan
        r["h_21min"] = round(r["s_frame"] * 20.7 * 60 * 15 / 3600, 1)               # both-visible time of AUDIT row 42
        r["h_full_videos"] = round(r["s_frame"] * n_corpus / 3600, 1)               # every frame of the 10 duet videos
        rows.append(r)
    t = pd.DataFrame(rows)
    t.to_csv(OUT / "summary.csv", index=False)
    print(n_corpus, "frames in the 10 videos"); print(t.to_string(index=False))


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "select":
        select()
    elif cmd == "run":
        run(sys.argv[2])
    elif cmd == "time":
        timing(sys.argv[2])
    elif cmd == "render":
        sheets(sys.argv[2])
    elif cmd == "compare":
        compare(sys.argv[3:], sys.argv[2])
    elif cmd == "score":
        score()
