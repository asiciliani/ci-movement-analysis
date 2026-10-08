#!/bin/bash
VIDEOS=("tt1TgoRwle0" "SQq1_bhD5q0" "U1M_QqM2f1c" "v-_4hlLnyMo" "IAa9o45Dqhs" "oNZe588clcw" "n2M6UOGjGSg" "r9PGJRItIX4" "cF44KD8DJg0" "ul2LMUIuwno" "PdPStkfazbE" "ZfdejcO5Sqw")
for VID in "${VIDEOS[@]}"; do
    echo "Processing $VID..."
    uv run yt-dlp --js-runtimes node --remote-components ejs:github --download-sections "*00:00-01:00" -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" --merge-output-format mp4 -o "videos/${VID}.mp4" "https://www.youtube.com/watch?v=$VID"
    if [ -f "videos/${VID}.mp4" ]; then
        echo "Running analysis on $VID..."
        mkdir -p "outputs/${VID}"
        .venv/bin/python3 run_analysis.py --video "videos/${VID}.mp4" --output-dir "outputs/${VID}"
    else
        echo "Failed to download $VID"
    fi
done
echo "All done!"
