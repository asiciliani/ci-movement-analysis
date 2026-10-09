#!/bin/bash
# Full-length versions of the pair-verified duet clips (the corpus so far used only 90 s of each), re-encoded
# at 15 fps: enough for the geometric descriptors and half the tracking cost. Clips are stored by YouTube id only.
cd "$(dirname "$0")/.."; mkdir -p videos/full
IDS=${IDS:-"kxztAr2tQmE swmrAJkYrlY hJQgFDsAms4 iOEZ3i9rgYM dGPRMNAECKM zQRF2sLK1vY Rc9vIJt00vs vinlwkaIW4c kMkJpfUGZz8 uS1JQ-LY8Fs ZfdejcO5Sqw ul2LMUIuwno"}
for id in $IDS; do
  out=videos/full/${id}_full.mp4
  if [ ! -s "$out" ]; then
    uv run yt-dlp --js-runtimes node --remote-components ejs:github -f "bv*[height<=720][ext=mp4]/b[height<=720]" \
      --quiet --no-warnings -o "/tmp/${id}_raw.%(ext)s" "https://www.youtube.com/watch?v=$id" &&
    ffmpeg -v quiet -y -i /tmp/${id}_raw.* -r 15 -an -c:v libx264 -preset veryfast -crf 23 "$out"; rm -f /tmp/${id}_raw.*
  fi
  stem=${id}_full
  [ -s outputs/$stem/${stem}_tracks.npz ] || .venv/bin/python -u run_tracking.py --video "$out" --output-dir outputs/$stem 2>&1 | grep -E "\[track\] done|Error|Trace"
  echo "=== $stem $(date +%H:%M)"
done
