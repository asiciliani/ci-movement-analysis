#!/bin/bash
# Rebuild features from pre-audit CSVs (positions only) for every video not yet re-tracked.
cd "$(dirname "$0")/.."
for d in outputs/*/; do
  stem=$(basename "$d")
  [ -f "$d/${stem}_tracks.npz" ] && continue
  [ -f "$d/${stem}_feature_info.json" ] && continue
  src=$(ls "$d"/${stem}_features.csv "$d"/ci_features.csv "$d"/${stem}_features_legacy.csv 2>/dev/null | head -1)
  [ -z "$src" ] && continue
  .venv/bin/python run_features.py --legacy-csv "$src" --output-dir "$d" 2>&1 | grep -vi warning
done
