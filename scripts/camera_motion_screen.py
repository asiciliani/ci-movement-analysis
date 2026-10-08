"""
Fast camera ego-motion screen for every video that has outputs.
Samples every `stride`-th frame at low resolution; masks a generous region around any
known dancer position (from the legacy features CSV or the tracks npz, if present).
Writes outputs/<stem>/<stem>_camera_motion.json. Used by aggregate_dataset.py to exclude
moving-camera footage from kinematic analysis.
"""
import sys, json, glob, os
from pathlib import Path
import numpy as np, pandas as pd, cv2
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.tracking.camera_motion import CameraMotionEstimator, summarize_camera_motion

STRIDE = 2
def boxes_from_csv(df, i, trunk):
    out = []
    if i >= len(df): return out
    r = df.iloc[i]
    for d in "AB":
        x, y = r.get(f"torso_{d}_x", np.nan), r.get(f"torso_{d}_y", np.nan)
        if np.isfinite(x) and np.isfinite(y):
            s = 3.0 * trunk
            out.append(np.array([x - s, y - 2 * s, x + s, y + 2 * s]))
    return out

def screen(video, outdir):
    stem = Path(video).stem
    csvs = glob.glob(f"{outdir}/*_features.csv")
    df = pd.read_csv(csvs[0], low_memory=False) if csvs else None
    trunk = 60.0
    if df is not None and "torso_A_x" in df:
        t = 2 * np.hypot(df.torso_A_x - df.pelvis_A_x, df.torso_A_y - df.pelvis_A_y).median()
        if np.isfinite(t) and t > 5: trunk = float(t)
    cap = cv2.VideoCapture(video)
    if not cap.isOpened(): return None
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)); n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    n = min(n, 2400)  # first 80 s is enough to classify the camera
    est = CameraMotionEstimator(work_width=400)
    motion = []
    i = 0
    while i < n:
        ok, f = cap.read()
        if not ok: break
        if i % STRIDE == 0:
            m, _ = est.step(f, boxes_from_csv(df, i, trunk) if df is not None else [])
            motion.append(m)
        i += 1
    cap.release()
    s = summarize_camera_motion(np.array(motion), w)
    s["stride"] = STRIDE; s["video"] = Path(video).name
    with open(f"{outdir}/{stem}_camera_motion.json", "w") as fh: json.dump(s, fh, indent=2)
    return s

if __name__ == "__main__":
    vids = sorted(glob.glob("videos/*.mp4") + glob.glob("videos/*.mov"))
    for v in vids:
        stem = Path(v).stem; outdir = f"outputs/{stem}"
        if not os.path.isdir(outdir): continue
        if os.path.exists(f"{outdir}/{stem}_camera_motion.json"): continue
        s = screen(v, outdir)
        if s: print(f"{stem}: static={s['camera_static']} moving_frac={s['moving_fraction']:.2f} median={s['median_motion_px']}", flush=True)
