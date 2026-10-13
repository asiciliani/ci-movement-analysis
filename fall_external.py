"""
External reference for falls.py: staged accidental falls and lying-down activities from the UR Fall Detection
Dataset (Kwolek & Kepski 2014; CC BY-NC-SA 4.0, non-commercial academic use; data_external/urfall/fetch.sh).

Frontal RGB camera (cam0, 640x480, 30 fps, static). Each sequence is downloaded, the same pose model as the CI
corpus (yolov8n-pose, imgsz 640) is run on every 2nd frame (-> 15 fps, the CI corpus rate), the most confident
person is kept, and the PNGs and zip are deleted; only the keypoints are kept, in outputs/falls/urfall/<seq>.npz
together with the dataset's per-frame posture label (-1 not lying, 0 transition, 1 lying on the ground).

Usage: .venv/bin/python -I fall_external.py pose      (download + pose, one sequence at a time)
The descriptors are computed by falls.py (`describe`), with the same code as the CI descents.
Caveat: these are young volunteers falling on purpose onto a mattress, i.e. staged falls, not real accidents.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import numpy as np
import pandas as pd

RAW = ROOT / "data_external/urfall/raw"
OUT = ROOT / "outputs/falls/urfall"; OUT.mkdir(parents=True, exist_ok=True)
BASE = "https://fenix.ur.edu.pl/~mkepski/ds/data"
# falls with >= 1.3 s of 'not lying' frames before the annotated fall (others start mid-fall), and the ADLs
# that contain a transition to lying (label 0/1: lying down on the floor / a bed / sofa)
FALLS = ["fall-01", "fall-02", "fall-03", "fall-05", "fall-07", "fall-09", "fall-10", "fall-11", "fall-13",
         "fall-17", "fall-25", "fall-27", "fall-29"]
ADLS = ["adl-10", "adl-11", "adl-21", "adl-22", "adl-23", "adl-30", "adl-36", "adl-37"]


def labels():
    L = pd.concat([pd.read_csv(RAW / f, header=None) for f in ("urfall-cam0-falls.csv", "urfall-cam0-adls.csv")])
    return {s: dict(zip(g[1], g[2])) for s, g in L.groupby(0)}


def pose_seq(seq, model, lab):
    out = OUT / f"{seq}.npz"
    if out.exists():
        return
    z = RAW / f"{seq}-cam0-rgb.zip"
    if not z.exists():
        subprocess.run(["curl", "-sfL", "-o", str(z), f"{BASE}/{z.name}"], check=True)
    tmp = RAW / f"tmp_{seq}"; tmp.mkdir(exist_ok=True)
    with zipfile.ZipFile(z) as zf:
        names = sorted(n for n in zf.namelist() if n.lower().endswith(".png"))
        for n in names[::2]:
            zf.extract(n, tmp)
    files = sorted(tmp.rglob("*.png"))
    K = np.full((len(files), 17, 3), np.nan, np.float32); fr = []
    for i, f in enumerate(files):
        r = model.predict(str(f), imgsz=640, conf=0.25, verbose=False)[0]
        if r.keypoints is not None and len(r.boxes):
            b = int(np.argmax(r.boxes.conf.cpu().numpy()))
            K[i, :, :2] = r.keypoints.xy[b].cpu().numpy(); K[i, :, 2] = r.keypoints.conf[b].cpu().numpy()
        fr.append(int(f.stem.split("-")[-1]))                      # frame number from file name (1-based)
    y = np.array([lab.get(seq, {}).get(n, -9) for n in fr])
    np.savez_compressed(out, kpts=K, frame=np.array(fr), label=y, fps=15.0)
    shutil.rmtree(tmp); z.unlink()
    print(seq, len(files), "frames, labels", {v: int((y == v).sum()) for v in np.unique(y)}, flush=True)


if __name__ == "__main__":
    if sys.argv[1:] == ["pose"]:
        os.environ.setdefault("OMP_NUM_THREADS", "2")
        import torch
        torch.set_num_threads(2)
        from ultralytics import YOLO
        model = YOLO(str(ROOT / "yolov8n-pose.pt")); lab = labels()
        for s in FALLS + ADLS:
            pose_seq(s, model, lab)
