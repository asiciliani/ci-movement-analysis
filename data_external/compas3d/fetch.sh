#!/bin/bash
# CoMPAS3D (Burkanova et al. 2025; CC BY-NC 4.0; huggingface.co/datasets/Rosie-Lab/compas3d).
# Keeps, per sequence and role, only the SMPL-X root translation (pelvis, 30 fps) + the move annotations.
cd "$(dirname "$0")"; PY=../../.venv/bin/python
curl -s "https://huggingface.co/api/datasets/Rosie-Lab/compas3d/tree/main?recursive=true" -o tree.json
$PY -c "
import json; t=json.load(open('tree.json'))
for x in t:
    p=x['path']
    if p.endswith(('_leader.npz','_follower.npz','.txt')) and '/.' not in p: print(p)" > wanted.txt
cat wanted.txt | xargs -P 6 -I{} sh -c '
  p="{}"; out="trans/${p%.npz}.npz"; mkdir -p "$(dirname "$out")"
  case "$p" in *.txt) [ -s "trans/$p" ] || curl -sL -o "trans/$p" "https://huggingface.co/datasets/Rosie-Lab/compas3d/resolve/main/$p"; exit 0;; esac
  [ -s "$out" ] && exit 0
  tmp=$(mktemp --suffix=.npz); curl -sL -o "$tmp" "https://huggingface.co/datasets/Rosie-Lab/compas3d/resolve/main/$p" &&
  '"$PY"' -c "
import sys, numpy as np; z=np.load(sys.argv[1], allow_pickle=True)
np.savez_compressed(sys.argv[2], trans=z[\"trans\"].astype(np.float32), fps=float(z[\"mocap_frame_rate\"]))" "$tmp" "$out"; rm -f "$tmp"'
echo "sequences: $(ls trans/Pair*/*/*_leader.npz | wc -l) leader, $(ls trans/Pair*/*/*_follower.npz | wc -l) follower"
