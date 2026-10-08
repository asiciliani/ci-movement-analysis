#!/bin/bash
# Third acquisition pass (after the pair audit): broader duet queries, stricter screen
# (full-body people, no shot cuts, <= 3 people on screen). Same storage rules as acquire_videos.sh.
cd "$(dirname "$0")/.."
mkdir -p videos/candidates
COMMON=(--js-runtimes node --remote-components ejs:github --match-filter "duration > 90 & duration < 3600"
        --download-sections "*00:30-02:00" -f "bv*[height<=720][ext=mp4]+ba[ext=m4a]/b[height<=720][ext=mp4]/b"
        --merge-output-format mp4 --no-overwrites --quiet --no-warnings -o "videos/candidates/%(id)s.mp4")
QUERIES=(
  "contact improvisation duet"
  "contact improv duet practice"
  "contact improvisation duet rehearsal studio"
  "contact improvisation class duet exercise"
  "contact improvisation underscore duet"
  "improvisación de contacto dúo estudio"
  "contato improvisação dueto"
  "kontaktimprovisation duett"
  "contact improvisation two dancers empty studio"
  "contact improvisation duet one take"
  "contact improvisation teachers dance together"
  "contact improvisation small dance duet"
)
N=${N:-8}
for q in "${QUERIES[@]}"; do
  echo "=== $q"
  uv run yt-dlp "${COMMON[@]}" "ytsearch${N}:${q}" 2>&1 | tail -2
done
for f in videos/candidates/*.mp4; do s=$(basename "${f%.*}"); [ -f "videos/$s.mp4" ] && rm -f "$f"; done
.venv/bin/python -u scripts/screen_candidates.py
