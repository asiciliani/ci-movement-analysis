#!/bin/bash
# Observed mocap markers (53 per dancer, 3-D, metres) for the first take of each pair's song1: surface points
# on both bodies, used for the 3-D rolling-vs-gripping check. Optional argument: a regex for the sequences
# (default _song1_take1; "" fetches all 71). Keeps markers_obs as float32 + fps only.
cd "$(dirname "$0")"; PY=../../.venv/bin/python
grep -E "${1-_song1_take1}_(leader|follower)\.npz$" wanted.txt | xargs -P 6 -I{} sh -c '
  p="{}"; out="markers/${p}"; mkdir -p "$(dirname "$out")"; [ -s "$out" ] && exit 0
  tmp=$(mktemp --suffix=.npz); curl -sL -o "$tmp" "https://huggingface.co/datasets/Rosie-Lab/compas3d/resolve/main/$p" < /dev/null &&
  '"$PY"' -c "
import sys, numpy as np; z=np.load(sys.argv[1], allow_pickle=True)
np.savez_compressed(sys.argv[2], markers=z[\"markers_obs\"].astype(np.float32), fps=float(z[\"mocap_frame_rate\"]))" "$tmp" "$out"; rm -f "$tmp"'
echo "sequences with markers: $(ls markers/Pair*/*/*_leader.npz | wc -l)"
