#!/bin/bash
# Download Bigand et al. (2024) mocap (CC BY 4.0, doi:10.48557/UR2GBG), dyads START..N.
# Each trial csv (one subject, 60 s x 250 Hz x 23 markers, ~19 MB) is converted to a 25 Hz .npz
# (block means, float32, ~0.4 MB) and the csv deleted, unless KEEP_CSV=1.
cd "$(dirname "$0")"; START=${START:-1}; N=${N:-35}
awk 'NF==2 && $2 ~ /\.(csv|txt)$/ {print $1, $2}' files.tsv | while read id name; do
  [ -f "$name" ] || curl -sL --retry 3 -o "$name" "https://dataverse.iit.it/api/access/datafile/$id" < /dev/null; done
PY=../../.venv/bin/python
pat=$(seq -f "Dyad_%02g/" $START $N | paste -sd'|')
grep -E "$pat" files.tsv | xargs -P 6 -n 3 sh -c '
  out="$1/${2%.csv}.npz"; [ -s "$out" ] && exit 0; mkdir -p "$1"
  curl -sL --retry 3 -o "$1/$2" "https://dataverse.iit.it/api/access/datafile/$0" &&
  '"$PY"' -W ignore -c "
import sys, numpy as np, pandas as pd
m = pd.read_csv(sys.argv[1], index_col=0).to_numpy(float); X = m.reshape(23, 3, -1).transpose(2, 0, 1)
T = X.shape[0] // 10 * 10
with np.errstate(all=\"ignore\"): Y = np.nanmean(X[:T].reshape(-1, 10, 23, 3), axis=1)
np.savez_compressed(sys.argv[2], X=Y.astype(np.float32), fs=25.0)" "$1/$2" "$out" && [ -z "$KEEP_CSV" ] && rm -f "$1/$2"'
echo "trials available: $(ls Dyad_*/subj_*/*.npz 2>/dev/null | wc -l) npz, $(ls Dyad_*/subj_*/*.csv 2>/dev/null | wc -l) csv"
