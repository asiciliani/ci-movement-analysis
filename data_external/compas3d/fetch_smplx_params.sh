#!/bin/bash
# SMPL-X (locked head) body parameters per sequence and role: poses (T,165), betas (300), trans (T,3), gender, fps.
# Turned into meshes with the SMPL-X model files (data_external/smplx_models/, licence: smpl-x.is.tue.mpg.de).
# Optional argument: regex for the sequences (default: all).
cd "$(dirname "$0")"; PY=../../.venv/bin/python
grep -E "${1-}.*_(leader|follower)\.npz$" wanted.txt | xargs -P 4 -I{} sh -c '
  p="{}"; out="smplx/${p}"; mkdir -p "$(dirname "$out")"; [ -s "$out" ] && exit 0
  tmp=$(mktemp --suffix=.npz); curl -sL -o "$tmp" "https://huggingface.co/datasets/Rosie-Lab/compas3d/resolve/main/$p" < /dev/null &&
  '"$PY"' -c "
import sys, numpy as np; z=np.load(sys.argv[1], allow_pickle=True)
np.savez_compressed(sys.argv[2], poses=z[\"poses\"].astype(np.float32), betas=z[\"betas\"].astype(np.float32),
                    trans=z[\"trans\"].astype(np.float32), gender=str(z[\"gender\"]), model=str(z[\"surface_model_type\"]),
                    fps=float(z[\"mocap_frame_rate\"]))" "$tmp" "$out"; rm -f "$tmp"'
echo "sequences with SMPL-X params: $(ls smplx/Pair*/*/*_leader.npz | wc -l)"
