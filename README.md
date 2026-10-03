# CI Movement Analysis: The Somatic Echo

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)

This repository contains the computational pipeline for the Licenciatura thesis: **"The Somatic Echo: Computational Kinematics of Energy Transfer and Injury Prevention Algorithms in Contact Improvisation."** (Universidad de Buenos Aires - Exactas).

## 🧠 Core Concept
Contact Improvisation (CI) dancers develop specific "Movement Algorithms" (MAs) to manage gravity, momentum, and shared weight safely. This project uses 2D Pose Estimation and Time-Series Analysis to prove whether physical interaction temporarily rewrites a dancer's motor algorithms.

**Key Metrics Extracted:**
* **Jerk ($da/dt$):** Measuring collision avoidance and the "Yield" algorithm when interacting with the floor or partner.
* **Kinetic Energy Proxy ($v^2$):** Measuring momentum conservation and the fluidity of weight transfer.
* **Degrees of Freedom (PCA):** Measuring the dimensionality of spherical space usage.

## 🏗️ Architecture
* **Pose Estimation:** YOLOv8-Pose
* **Tracking:** Custom Bipartite Hungarian matching with occlusion-handling heuristics.
* **Signal Processing:** Savitzky-Golay filtering for robust high-order kinematic derivatives.
* **Future Work (VLM):** A hybrid architecture for severe topological occlusion, escalating from YOLO to a Semantic Vision-Language Model (VLM) via IoU thresholds.

## 📂 Repository Structure
* `src/` - Core Python pipeline (Tracking, Features, Analysis, Visualization)
* `videos/` - Input CI MP4 videos (ignored by git to save space).
* `outputs/` - Generated CSVs, annotated MP4s, HTML reports, and Somatic Echo dashboards.
* `THESIS_PROPOSAL.md` - Formal English pitch.
* `PLAN_DE_TESIS_ES.md` - Formal Spanish pitch for UBA Exactas.
* `DATA_COLLECTION_PROTOCOL.md` - A-B-A experiment recording protocol.
* `HYBRID_AI_TRACKER_ARCHITECTURE.md` - VLM fallback mechanism blueprint.
* `BRAINSTORMING_LOG.md` - Jam Thermodynamics and network topology ideas.

## 🚀 Quick Start
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run the full pipeline on a video
python run_analysis.py --video videos/my_video.mp4 --output-dir outputs/
```
