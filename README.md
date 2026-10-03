# Contact Improvisation Movement Analysis — Proof of Concept (PoC)

Computational exploration for a Licenciatura thesis in Computer Science (UBA / FCEN - Exactas).

> **Core Research Question:**  
> *How does interpersonal movement coordination emerge and change during Contact Improvisation, and can those dynamics be characterized computationally from video?*

---

## 1. Overview & Research Mindset

This prototype provides an end-to-end computational pipeline to answer a crucial preliminary question:  
**Can we extract useful movement/coordination signals from ordinary videos of two Contact Improvisation dancers?**

### Avoiding Presuppositions (Not just "Synchronization")
Contact Improvisation (CI) rarely conforms to simple in-phase synchronization. Instead, it is characterized by:
- **Initiation and Following:** Asymmetric temporal delays where one dancer's impulse leads to the other's adaptation.
- **Shared Momentum & Weight Exchange:** Rolling points of contact, lifts, and counterbalances where velocities may be opposing or complementary rather than identical.
- **Mutual Adaptation & Interruption:** Sudden redirection of momentum, pauses, and floor transitions.

This PoC computes candidate interpersonal movement measures and systematically tests whether they correlate with manually annotated interaction phases.

---

## 2. Architecture & Modular Structure

```text
.
├── src/
│   ├── pose/             # Pose estimation using YOLOv8-Pose (17 COCO landmarks)
│   │   ├── pose_detector.py
│   │   └── __init__.py
│   ├── tracking/         # Two-dancer persistent tracker & foreground filtering
│   │   ├── dancer_tracker.py
│   │   └── __init__.py
│   ├── features/         # Kinematics, smoothed velocities, distances, contact proxies
│   │   ├── kinematics.py
│   │   └── __init__.py
│   ├── analysis/         # Lagged cross-correlation, rolling coupling, annotations
│   │   ├── coordination.py
│   │   └── __init__.py
│   └── visualization/    # Multi-panel dashboards, trajectory plots, HTML reports, video overlays
│       ├── plots.py
│       ├── video_overlay.py
│       ├── report.py
│       └── __init__.py
├── videos/               # Local input MP4 videos
├── annotations/          # Manual annotation CSV/JSON files
├── outputs/              # Generated plots, CSVs, annotated MP4 videos, HTML reports
├── notebooks/            # Exploratory research notebooks
├── run_analysis.py       # Master pipeline CLI runner
├── requirements.txt      # Python dependencies
└── README.md
```

---

## 3. Implemented Movement Measures

### 1. Inter-Dancer Distances
- **Torso Center Distance:** Euclidean distance between torso centers $(\text{midpoint}(\text{shoulders}, \text{hips}))$.
- **Pelvis Distance:** Distance between pelvis centers $(\text{midpoint}(\text{left\_hip}, \text{right\_hip}))$.
- **Whole-Body Center Distance:** Distance between full-body keypoint centroids.
- **Normalized Distances:** Distances normalized by frame diagonal or torso scale to provide camera zoom invariance.

### 2. Relative Velocities & Speeds
- Trajectories are smoothed via a Savitzky-Golay filter to remove detection jitter.
- Torso/Pelvis velocity vectors: $\vec{v}_A(t) = (\dot{x}_A, \dot{y}_A)$ and $\vec{v}_B(t) = (\dot{x}_B, \dot{y}_B)$.
- Instantaneous speeds: $||\vec{v}_A(t)||$ and $||\vec{v}_B(t)||$.

### 3. Directional Coordination (Cosine Similarity)
- Measures whether dancers are moving in parallel, perpendicular, or opposite directions:
  $$\cos \theta(t) = \frac{\vec{v}_A(t) \cdot \vec{v}_B(t)}{\|\vec{v}_A(t)\| \, \|\vec{v}_B(t)\| + \epsilon} \in [-1, 1]$$
  - $+1$: Moving in the identical direction (shared trajectory, following).
  - $0$: Orthogonal / independent directions.
  - $-1$: Moving in opposite directions (pushing away, counterbalancing, separating).

### 4. Time-Lagged Coordination (Cross-Correlation)
- Computes normalized cross-correlation over lag window $\tau \in [-2\text{s}, +2\text{s}]$:
  $$R_{AB}(\tau) = \frac{1}{N \sigma_A \sigma_B} \sum_t \left(v_A(t) - \mu_A\right)\left(v_B(t+\tau) - \mu_B\right)$$
  - Peak lag $\tau^* > 0$: Dancer A precedes Dancer B (predictive coupling).
  - Peak lag $\tau^* < 0$: Dancer B precedes Dancer A.
  - Peak lag $\tau^* \approx 0$: Simultaneous coupling.
- **Rolling Cross-Correlation Heatmap:** Windowed cross-correlation over time showing dynamic shifts in precedence across the dance.

### 5. Movement Phase & Rhythm
- Bandpass filtering $(0.2\text{ Hz} - 2.5\text{ Hz})$ of vertical position/speed followed by Hilbert transform to compute instantaneous phase $\phi_A(t), \phi_B(t)$.
- Phase Locking Value (PLV) quantifying degree of phase coherence: $\text{PLV} = |\frac{1}{N} \sum e^{i(\phi_A - \phi_B)}|$.

### 6. Contact Proxies
- **Minimum Keypoint Distance:** $\min_{i, j} \|\mathbf{k}_{A, i} - \mathbf{k}_{B, j}\|$ across confident keypoints.
- **Hand-to-Torso / Wrist Proximities:** Captures reach and hold events.

### 7. Manual Annotation Integration
- Simple CSV/JSON interval schema (`start_time, end_time, label, notes`).
- Supports time formats like `MM:SS` or float seconds.
- Computes phase-wise summary statistics to evaluate whether computational signals differ significantly across dance states (`separate`, `approaching`, `contact`, `shared_weight`, `transition`).

---

## 4. Quickstart & Usage

### Setup Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Running Analysis on a Video
```bash
python run_analysis.py \
    --video videos/ci_duet_sample.mp4 \
    --annotations annotations/ci_duet_sample.csv \
    --output-dir outputs/
```

### Options:
- `--max-frames N`: Run only first $N$ frames for fast experimentation.
- `--no-video`: Skip rendering the annotated MP4 video (only generate plots and HTML report).

---

## 5. Outputs Generated
For each video processed, the pipeline outputs:
1. `outputs/{video_stem}_dashboard.png`: 6-panel synchronized time-series dashboard (distances, speeds, cosine similarity, contact proxy, global xcorr, rolling lag heatmap).
2. `outputs/{video_stem}_trajectories.png`: 2D spatial trajectory map of both dancers.
3. `outputs/{video_stem}_phase_comparison.png`: Bar charts comparing kinematics across manual annotation phases.
4. `outputs/{video_stem}_annotated.mp4`: Full video with tracked skeleton overlays, trajectory trails, and a real-time HUD bar.
5. `outputs/{video_stem}_report.html`: Self-contained standalone HTML inspection report.
6. `outputs/{video_stem}_features.csv`: Frame-by-frame time-series data.
7. `outputs/{video_stem}_phase_summary.csv`: Aggregated metrics per annotated phase.
