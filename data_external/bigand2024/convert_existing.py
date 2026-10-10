"""Convert already-downloaded trial csvs to 25 Hz npz (same as fetch.sh) and delete the csv."""
import sys, glob, os
from concurrent.futures import ProcessPoolExecutor
import numpy as np, pandas as pd

def conv(p):
    out = p[:-4] + ".npz"
    if not os.path.exists(out):
        m = pd.read_csv(p, index_col=0).to_numpy(float); X = m.reshape(23, 3, -1).transpose(2, 0, 1)
        T = X.shape[0] // 10 * 10
        with np.errstate(all="ignore"):
            Y = np.nanmean(X[:T].reshape(-1, 10, 23, 3), axis=1)
        np.savez_compressed(out, X=Y.astype(np.float32), fs=25.0)
    os.remove(p); return out

if __name__ == "__main__":
    files = sorted(glob.glob(os.path.join(os.path.dirname(__file__), "Dyad_*/subj_*/*.csv")))
    with ProcessPoolExecutor(4) as ex:
        n = sum(1 for _ in ex.map(conv, files, chunksize=8))
    print("converted", n)
