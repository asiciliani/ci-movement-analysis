#!/bin/bash
# UR Fall Detection Dataset (Kwolek & Kepski 2014, Comput. Methods Programs Biomed. 117:489-501)
# https://fenix.ur.edu.pl/~mkepski/ds/uf.html  -- licence CC BY-NC-SA 4.0, non-commercial academic use.
# Fetches the per-frame posture labels (cam0). The RGB zips (40-70 MB each) of the 13 falls + 8 ADLs used are
# downloaded one at a time, posed and deleted by `.venv/bin/python -I fall_external.py pose` (repo root);
# only the keypoints are kept (outputs/falls/urfall/*.npz).
set -e
cd "$(dirname "$0")"
B=https://fenix.ur.edu.pl/~mkepski/ds/data
mkdir -p raw
for f in urfall-cam0-falls.csv urfall-cam0-adls.csv; do [ -f raw/$f ] || curl -sfL -o raw/$f $B/$f; done
