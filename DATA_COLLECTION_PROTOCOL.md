# Data Collection Protocol: The Somatic Echo

This document outlines the standardized filming protocol for the A-B-A "Somatic Echo" experiment. Consistency in data collection is critical for accurate kinematics extraction via 2D Pose Estimation.

## 1. Environmental Setup
* **Lighting:** Ensure bright, even lighting. Avoid strong backlighting (windows behind the dancers) which turns bodies into silhouettes, as this degrades the pose estimator's confidence.
* **Camera Placement:** 
  * Use a single static camera on a tripod. 
  * Height: Approx 1.2m - 1.5m (chest height of an average standing person).
  * Framing: Wide enough to capture the entire usable floor space. Dancers must not exit the frame.
  * Angle: Straight on, avoiding extreme high/low angles to minimize perspective distortion on the vertical axis (which affects Center of Mass calculations).
* **Resolution & Framerate:** Minimum 1080p at 30 FPS (60 FPS preferred for highly accurate Jerk/Acceleration derivatives).
* **Attire:** Dancers should wear contrasting colors if possible (e.g., one in light colors, one in dark) to help the tracker maintain identity during brief occlusions. Avoid extremely baggy clothing that hides joints.

## 2. Participant Intake
Before filming, participants complete a brief survey mapping their "Training Background" (to be used later as a potential moderating variable):
* Years practicing Contact Improvisation.
* Average hours per week of CI practice.
* Years of formal/academic dance training (e.g., UNA, Ballet, Contemporary).
* Primary learning environment (Academic vs. Community/Jams).

## 3. The 10-Minute A-B-A Protocol
Each dyad undergoes a single, continuous 10-minute filmed session without stopping the camera.

### Phase A: The Baseline Solo (2 Minutes)
* **Instructions:** "Move continuously in the space. You may use the floor or remain standing, but do not make physical contact with your partner. Dance your own solo."
* **Purpose:** Establishes the baseline kinematics (Baseline Jerk, Baseline Kinetic Energy, Baseline Floor Usage) for each nervous system *before* interaction.

### Phase B: The CI Duet (5 Minutes)
* **Instructions:** "Begin Contact Improvisation. Explore weight sharing, momentum, and finding the rolling point of contact."
* **Purpose:** Forces the dancers to activate CI-specific Movement Algorithms (MA 1: The Yield, MA 2: Momentum Transfer) to manage shared gravity safely.

### Phase C: The Echo Solo (2 Minutes)
* **Instructions:** "Gently separate from your partner and return to dancing solo. Continue to move continuously."
* **Purpose:** The critical test phase. We measure whether the kinematics of Phase C statistically differ from Phase A, proving that the dyadic interaction temporarily rewrote their solo movement algorithms.

## 4. Post-Processing
* Videos are cropped to standard length and passed through the `run_analysis.py` pipeline.
* Phase intervals (e.g., `0-120s: Phase A`, `120-420s: Phase B`) are annotated in the corresponding CSV to allow the pipeline to compare Phase A vs. Phase C metrics automatically.
