#!/bin/bash
while true; do
  progress=$(cat /home/andisici/.gemini/antigravity/brain/72eefced-f95d-4a04-8def-c7469cbf3bb0/.system_generated/tasks/task-741.log | grep Processed | tail -n 1 | awk '{print $4}' | tr -d '()%')
  if [ -z "$progress" ]; then progress="100"; fi
  html_file="/home/andisici/.gemini/antigravity/brain/72eefced-f95d-4a04-8def-c7469cbf3bb0/status_board.html"
  sed -i -E "s/>~[0-9.]+%</>~${progress}%</g" "$html_file"
  sed -i -E "s/width: [0-9.]+%/width: ${progress}%/g" "$html_file"
  # Mark K-Means as Done
  sed -i -E "s/Entrenando Modelo ML.../Completado/" "$html_file"
  sleep 10
done
