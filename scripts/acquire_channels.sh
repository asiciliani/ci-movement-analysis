#!/bin/bash
# Second acquisition pass: specific practitioner channels + practitioner-name searches.
# Same screening as acquire_videos.sh. Clips are stored by YouTube id only; for thesis use of
# footage of identifiable practitioners, ask for their consent (see DATASET.md).
cd "$(dirname "$0")/.."
mkdir -p videos/candidates
COMMON=(--js-runtimes node --remote-components ejs:github --match-filter "duration > 90 & duration < 2400"
        --download-sections "*00:30-02:00" -f "bv*[height<=720][ext=mp4]+ba[ext=m4a]/b[height<=720][ext=mp4]/b"
        --merge-output-format mp4 --no-overwrites --quiet --no-warnings -o "videos/candidates/%(id)s.mp4")
# Practitioner channels are listed one URL per line in scripts/channels.local.txt (not tracked:
# practitioners are identifiable, see DATASET.md).
CHANNELS=()
[ -f scripts/channels.local.txt ] && mapfile -t CHANNELS < scripts/channels.local.txt
for c in "${CHANNELS[@]}"; do
  echo "=== channel $c"
  uv run yt-dlp "${COMMON[@]}" --playlist-end 20 "$c" 2>&1 | tail -2
done
QUERIES=(
  "Nancy Stark Smith contact improvisation duet"
  "Steve Paxton contact improvisation"
  "Nita Little contact improvisation"
  "Ray Chung contact improvisation duet"
  "Martin Keogh contact improvisation"
  "Jörg Hassmann contact improvisation"
  "contact improvisation Buenos Aires jam"
  "contacto improvisación dúo"
  "contact improvisation Freiburg festival duet"
  "contact improvisation Earthdance jam"
)
N=${N:-4}
for q in "${QUERIES[@]}"; do
  echo "=== $q"
  uv run yt-dlp "${COMMON[@]}" "ytsearch${N}:${q}" 2>&1 | tail -2
done
for f in videos/candidates/*.mp4; do s=$(basename "${f%.*}"); [ -f "videos/$s.mp4" ] && rm -f "$f"; done
.venv/bin/python -u scripts/screen_candidates.py
