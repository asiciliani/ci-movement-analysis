cd /home/andisici/Documents/Exactas/tesis
# CoMPAS3D renders (CC BY-NC 4.0): one sequence per proficiency level, first 60 s, one camera panel (the render is a 2x2 multi-view grid), tracked with the same pipeline
for s in Pair1/Pair1_song1_take1 Pair2/Pair2_song2_take1 Pair5/Pair5_song2_take1 Pair7/Pair7_song1_take1; do
  stem=salsa_$(basename $s); out=videos/external/$stem.mp4
  [ -s $out ] || { curl -sL "https://huggingface.co/datasets/Rosie-Lab/compas3d/resolve/main/$s/$(basename $s).mp4" -o /tmp/$stem.full.mp4 &&
    ffmpeg -v quiet -y -i /tmp/$stem.full.mp4 -t 60 -an -vf "crop=540:540:960:0,fps=30" -c:v libx264 -preset veryfast -crf 23 $out && rm -f /tmp/$stem.full.mp4; }
  [ -s outputs/$stem/${stem}_tracks.npz ] || .venv/bin/python -u run_tracking.py --video $out --output-dir outputs/$stem 2>&1 | grep -E "done|Error|Trace"
  echo "=== $stem finished"
done
