#!/bin/bash
# Curated acquisition of public CI duet footage. Downloads 90 s (from 0:30) at <=720p into
# videos/candidates/, then screens each clip (static camera + two full-size people) before it is queued.
# Criteria and verdicts are logged in videos/candidates.csv. Nothing is redistributed.
cd "$(dirname "$0")/.."
mkdir -p videos/candidates
N=${N:-6}
QUERIES=(
  "contact improvisation duet performance"
  "contact improvisation duet studio"
  "contact improvisation score two dancers"
  "contact improvisation demonstration weight sharing"
  "contact improvisation duo improvisación de contacto"
  "contact improvisation round robin jam duet"
  "contact improvisation nancy stark smith duet"
  "contact improvisation lifts flying low duet"
)
for q in "${QUERIES[@]}"; do
  echo "=== $q"
  uv run yt-dlp --js-runtimes node --remote-components ejs:github \
    --match-filter "duration > 90 & duration < 2400" \
    --download-sections "*00:30-02:00" \
    -f "bv*[height<=720][ext=mp4]+ba[ext=m4a]/b[height<=720][ext=mp4]/b" --merge-output-format mp4 \
    --no-overwrites --quiet --no-warnings \
    -o "videos/candidates/%(id)s.mp4" "ytsearch${N}:${q}" 2>&1 | tail -2
done
# drop candidates we already have
for f in videos/candidates/*.mp4; do s=$(basename "${f%.*}"); [ -f "videos/$s.mp4" ] && rm -f "$f"; done
.venv/bin/python -u scripts/screen_candidates.py
