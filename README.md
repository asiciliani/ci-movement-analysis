# CI Movement Analysis: Kinematic Signatures

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)

This repository contains the computational pipeline for the Licenciatura thesis: **"Cinemática Computacional: Extracción Empírica de Firmas de Movimiento en Contact Improvisation."** (Universidad de Buenos Aires - Exactas).

## 🧠 Core Concept
Contact Improvisation (CI) dancers develop specific "Movement Algorithms" (MAs) to manage gravity, momentum, and shared weight safely. This project uses 2D Pose Estimation and Time-Series Analysis to **empirically detect the mathematical signatures (traits)** that define a CI duet, abandoning rigid laboratory protocols in favor of analyzing wild, ecological data (Jams and practices).

**The 3 Kinematic Signatures:**
1. **The Yield (Collision Avoidance):** Measured via the minimization of **Jerk** ($da/dt$).
2. **The Momentum Ride (Energy Transfer):** Measured via the conservation of the system's **Kinetic Energy** ($v^2$).
3. **Physical Listening (Synchronization):** Measured via the **Cross-Correlation** and phase-locking of the dancers' velocity vectors.

## 🏗️ Architecture
* **Pose Estimation:** YOLOv8-Pose
* **Tracking:** Custom Bipartite Hungarian matching with occlusion-handling heuristics.
* **Signal Processing:** Savitzky-Golay filtering for robust high-order kinematic derivatives.
* **Future Work (VLM):** A hybrid architecture for severe topological occlusion, escalating from YOLO to a Semantic Vision-Language Model (VLM) via IoU thresholds.

## 📂 Repository Structure
* `src/` - Core Python pipeline (Tracking, Features, Analysis, Visualization)
* `videos/` - Input CI MP4 videos (ignored by git to save space).
* `outputs/` - Generated CSVs, annotated MP4s, HTML reports, and KDE/Boxplot dashboards.
* `PLAN_DE_TESIS_ES.md` - Formal Spanish thesis pitch for UBA Exactas (Mixed Methodology).
* `BIBLIOGRAPHY.md` - Essential state-of-the-art literature review.
* `THESIS_PROPOSAL.md` - Original English pitch.
* `HYBRID_AI_TRACKER_ARCHITECTURE.md` - VLM fallback mechanism blueprint.

## 🚀 Quick Start
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run the full pipeline to extract kinematic signatures
python run_analysis.py --video videos/my_video.mp4 --output-dir outputs/
```
