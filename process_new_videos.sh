#!/bin/bash
VIDEOS=("NGf03Yg6fM0" "65S9nuRzK4Q" "H8JiB2Nv5Qo" "f1o6FJL8bxM" "dGPRMNAECKM" "BBEbtuQkDb0" "XW6_uwEqt_A" "kxztAr2tQmE" "ED8hNoulZv4")

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
echo "All done downloading new dataset!"
