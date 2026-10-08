#!/bin/bash
# Re-track videos with the audited pipeline (stage 1 + stage 2), highest-value first.
# CPU-only: ~2 fps at 720p. Safe to stop and restart: finished videos are skipped.
cd "$(dirname "$0")/.."
export OMP_NUM_THREADS=${OMP_NUM_THREADS:-3}
QUEUE=${1:-scripts/queue.txt}
while read -r stem; do
  [ -z "$stem" ] && continue
  v=$(ls videos/"$stem".mp4 videos/"$stem".mov 2>/dev/null | head -1)
  [ -z "$v" ] && { echo "skip $stem (no video)"; continue; }
  if [ -f "outputs/$stem/${stem}_tracks.npz" ]; then echo "skip $stem (tracked)"; continue; fi
  echo "=== $stem $(date)"
  .venv/bin/python -u run_tracking.py --video "$v" --output-dir "outputs/$stem" 2>&1 | grep -vi warning
  .venv/bin/python -u run_features.py --tracks "outputs/$stem/${stem}_tracks.npz" 2>&1 | grep -vi warning
done < "$QUEUE"
echo "=== queue finished $(date)"
