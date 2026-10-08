#!/bin/bash
echo "Starting Massive & Historical CI Dataset Expansion..."

# Create a list of search queries to get a diverse and historical dataset
QUERIES=(
    "ytsearch5:Contact Improvisation Steve Paxton"
    "ytsearch5:Contact Improvisation Nancy Stark Smith"
    "ytsearch3:Contact Improvisation Magnesium 1972"
    "ytsearch15:Contact Improvisation duet performance"
    "ytsearch10:Contact Improvisation jam"
)

mkdir -p videos
mkdir -p outputs

for QUERY in "${QUERIES[@]}"; do
    echo "Searching and downloading for query: $QUERY"
    # Download the first 60 seconds of each video found in the search
    uv run yt-dlp --js-runtimes node --remote-components ejs:github \
        --download-sections "*00:00-01:00" \
        -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" \
        --merge-output-format mp4 \
        -o "videos/%(id)s.mp4" \
        "$QUERY"
done

echo "Downloads complete. Running YOLO tracking pipeline on all new videos..."

# Run analysis on any newly downloaded mp4 video that doesn't have an output directory yet
for VIDEO_FILE in videos/*.mp4; do
    VID_ID=$(basename "$VIDEO_FILE" .mp4)
    if [ ! -d "outputs/$VID_ID" ]; then
        echo "Running analysis on $VID_ID..."
        mkdir -p "outputs/$VID_ID"
        .venv/bin/python3 run_analysis.py --video "$VIDEO_FILE" --output-dir "outputs/$VID_ID"
    else
        echo "Skipping $VID_ID (already analyzed)."
    fi
done

echo "Massive Dataset Expansion Complete!"
