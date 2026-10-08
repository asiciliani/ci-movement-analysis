"""
Screen downloaded candidate clips before spending CPU on full tracking.
For each video in videos/candidates/: (1) camera ego-motion (RANSAC global fit, every 2nd frame of the
first 60 s), (2) a sparse YOLO pose pass (1 frame every 2 s) to count frames with >= 2 full-size, full-body people
(hips and an ankle visible). Accepted clips still need a human content check (videos/curation.csv).
Accepted clips are moved to videos/ and appended to scripts/queue.txt. Verdicts go to videos/candidates.csv.
"""
import sys, glob, os, shutil, csv
from pathlib import Path
import numpy as np, cv2
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.tracking.camera_motion import CameraMotionEstimator, summarize_camera_motion

MIN_TWO_PEOPLE_FRAC = 0.6
MAX_MOVING_FRACTION = 0.7  # static or slowly panning: compensated later; aggregate_dataset.py checks the compensation
MIN_PERSON_HEIGHT_FRAC = 0.15
MIN_WIDTH = 640        # below this, trunk length is ~30 px and jitter dominates everything
MIN_FPS = 23.0         # Savitzky-Golay window of 11 samples assumes >= ~24 fps
MAX_CUTS = 0           # edited montages switch between different duets / angles (found by the pair audit)
MAX_MEDIAN_PEOPLE = 3  # crowded jams: the two tracked people are rarely a stable duet
CUT_DIFF = 0.6         # shot cut: mean |difference| of consecutive contrast-normalised 64x36 frames above this
                       # (cuts measured 0.86-1.05 in an edited montage; dance motion 0.01-0.4)
MIN_KPT_CONF = 0.3     # a person counts only if hips AND at least one ankle are visible (full body):
                       # videoconference tiles of talking heads passed the old size-only rule


def count_cuts(diffs: np.ndarray, fps: float) -> int:
    """Isolated spikes of frame difference (> CUT_DIFF and > 5x the local median) after the first second (fade-ins)."""
    k = int(fps); n = 0
    for t in range(k, len(diffs)):
        neighbours = np.r_[diffs[max(0, t - 6): t - 1], diffs[t + 2: t + 7]]   # excludes t-1..t+1
        if diffs[t] > CUT_DIFF and diffs[t] > 5 * np.median(neighbours):
            n += 1
    return n


def screen(video, model):
    cap = cv2.VideoCapture(video)
    if not cap.isOpened(): return None
    w, h, fps = int(cap.get(3)), int(cap.get(4)), cap.get(5) or 30
    n = int(cap.get(7)); est = CameraMotionEstimator(work_width=400); ms = []; two = []; npeople = []; step = int(2 * fps)
    prev_g = None; diffs = []
    i = 0
    while i < min(n, int(60 * fps)):
        ok, f = cap.read()
        if not ok: break
        if i % 2 == 0: ms.append(est.step(f, [])[0])
        g = cv2.GaussianBlur(cv2.cvtColor(cv2.resize(f, (64, 36)), cv2.COLOR_BGR2GRAY).astype(float), (3, 3), 0)
        g = (g - g.mean()) / (g.std() + 1e-6)
        diffs.append(float(np.mean(np.abs(g - prev_g))) if prev_g is not None else 0.0); prev_g = g
        if i % step == 0:
            r = model(f, imgsz=480, verbose=False)[0]
            if r.boxes is not None and len(r.boxes):
                hh = (r.boxes.xyxy[:, 3] - r.boxes.xyxy[:, 1]).cpu().numpy() / h
                kc = r.keypoints.conf.cpu().numpy() if r.keypoints is not None and r.keypoints.conf is not None else np.zeros((len(hh), 17))
                full_body = (kc[:, 11:13].min(1) >= MIN_KPT_CONF) & (kc[:, 15:17].max(1) >= MIN_KPT_CONF)
                two.append(int(((hh >= MIN_PERSON_HEIGHT_FRAC) & full_body).sum() >= 2))
                npeople.append(int((hh >= MIN_PERSON_HEIGHT_FRAC).sum()))
            else:
                two.append(0); npeople.append(0)
        i += 1
    cap.release()
    cuts = count_cuts(np.array(diffs), fps)
    cm = summarize_camera_motion(np.array(ms), w)
    frac2 = float(np.mean(two)) if two else 0.0
    med_people = float(np.median(npeople)) if npeople else 0.0
    return {"video": Path(video).name, "width": w, "height": h, "fps": round(fps, 2), "n_frames": n, "camera_static": cm["camera_static"],
            "moving_fraction": round(cm["moving_fraction"], 3), "two_people_fraction": round(frac2, 3), "shot_cuts": cuts, "median_people": med_people,
            "accepted": bool((cm["camera_static"] or cm["moving_fraction"] <= MAX_MOVING_FRACTION) and frac2 >= MIN_TWO_PEOPLE_FRAC and w >= MIN_WIDTH and fps >= MIN_FPS
                             and cuts <= MAX_CUTS and med_people <= MAX_MEDIAN_PEOPLE)}


if __name__ == "__main__":
    from ultralytics import YOLO
    model = YOLO("yolov8n-pose.pt")
    rows = []
    out_csv = "videos/candidates.csv"
    seen = set()
    if os.path.exists(out_csv):
        with open(out_csv) as f:
            for r in csv.DictReader(f): seen.add(r["video"]); rows.append(r)
    for v in sorted(glob.glob("videos/candidates/*.mp4")):
        if Path(v).name in seen: continue
        r = screen(v, model)
        if r is None: continue
        rows.append(r); print(r, flush=True)
        if r["accepted"]:
            dest = f"videos/{Path(v).name}"
            if not os.path.exists(dest): shutil.move(v, dest)
            with open("scripts/queue.txt", "a") as q: q.write(Path(v).stem + "\n")
    with open(out_csv, "w", newline="") as f:
        fields = list(dict.fromkeys(k for r in rows for k in r)) or ["video"]   # rows from older screens lack newer columns
        wtr = csv.DictWriter(f, fieldnames=fields, restval=""); wtr.writeheader(); wtr.writerows(rows)
    print(f"screened {len(rows)} candidates; accepted {sum(1 for r in rows if str(r['accepted']) == 'True')}")
