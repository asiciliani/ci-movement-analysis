#!/bin/bash
# Re-track the pair-verified duets with YOLO11x-pose (AUDIT 52) and the fixed two-dancer assignment (AUDIT 54).
# The YOLOv8n outputs are kept next to the new ones as outputs/<stem>_v8n/. ~1.2-1.5 s per frame on CPU.
# Track ids change, so bystander exclusions and the pair audit must be redone on the new tracks.
cd "$(dirname "$0")/.."; M=data_external/pose_models/yolo11x-pose.pt
STEMS=${STEMS:-"kMkJpfUGZz8_full vinlwkaIW4c_full kxztAr2tQmE_full zQRF2sLK1vY dGPRMNAECKM_full swmrAJkYrlY_full iOEZ3i9rgYM_full Rc9vIJt00vs_full hJQgFDsAms4_full uS1JQ-LY8Fs_full"}
for s in $STEMS; do
  v=$(ls videos/$s.* videos/full/$s.* videos/external/$s.* 2>/dev/null | head -1)
  [ -z "$v" ] && { echo "no video for $s"; continue; }
  if [ ! -d outputs/${s}_v8n ]; then mv outputs/$s outputs/${s}_v8n; fi
  [ -s outputs/$s/${s}_tracks.npz ] || .venv/bin/python -u pipeline/run_tracking.py --video "$v" --output-dir outputs/$s --model $M 2>&1 | grep -E "\[track\] done|Error|Trace"
  echo "=== $s $(date '+%d %H:%M')"
done
