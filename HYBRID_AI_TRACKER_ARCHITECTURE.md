# Future Work: Hybrid Semantic-Heuristic Tracking for CI

*Based on the October 2026 AI Occlusion Experiment.*

## The Problem: Severe Multi-Person Occlusion
In Contact Improvisation (CI), dancers frequently enter states of severe topological entanglement (e.g., lifts, shared floorwork). 
During our experiment on a 5-second clip of a heavy lift (Gastón & Paula), traditional top-down pose estimators (YOLOv8-Pose) failed. 
* **The Failure Mode:** The heuristic tracker draws a single bounding box around the tangled mass and attempts to fit a single 17-point skeleton to it, resulting in "spider-skeletons" and catastrophic identity swapping (e.g., attaching Dancer A's legs to Dancer B's inverted head).

## The Solution: Multimodal Semantic AI
In the same experiment, a Vision-Language Model (VLM) was able to visually parse the exact same frames. Because the VLM possesses **Semantic Understanding**, it correctly identified that one dancer was upside-down over the shoulder of the other, successfully distinguishing limbs based on clothing context, hair, and structural logic rather than rigid heuristics.

## Proposed Architecture: The Hybrid VLM-YOLO Tracker
For future research (Master's/PhD), the tracking pipeline could be upgraded to a hybrid model to solve the CI occlusion problem:

1. **High-Speed Heuristic Baseline (YOLO):** 
   * YOLOv8 processes the video at 60 FPS. 
   * It calculates an "Entanglement Confidence Score" based on bounding box overlap (IoU) and keypoint confidence.
2. **Semantic Interruption Trigger:** 
   * When IoU > 0.85 and keypoint confidence drops below a threshold, YOLO flags a "Severe Occlusion Event" (e.g., a puppy pile).
3. **VLM Hand-off:** 
   * The specific tangled frames are batched and sent to a local or cloud-based Vision-Language Model (e.g., LLaVA, Gemini, or a zero-shot segmentation model like SAM 2).
   * The VLM is prompted to semantically segment Dancer A vs. Dancer B using visual context (shirt color, hair).
4. **Correction & Resume:** 
   * The VLM returns the correct semantic masks or localized joint coordinates. 
   * The pipeline updates the Hungarian matching algorithm to preserve identities through the tangle, then hands control back to YOLO once the dancers separate.
