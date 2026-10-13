# Brainstorming & Idea Log
*Created: October 2026*

This document serves as a repository for all the conceptual directions, mathematical ideas, and experimental designs we brainstormed. Even if the final thesis narrows its focus, these ideas are documented here for future exploration, potential PhD work, or alternative thesis directions.

---

## 1. Core Concept: "Movement Algorithms" (MAs)
Contact Improvisation is essentially a practice of reprogramming the nervous system to solve complex physical problems (gravity, momentum, shared weight) safely. 
We defined several MAs that CI dancers develop:
* **The "Yield" / Collision Avoidance:** Absorbing impact by extending the time of deceleration. Measured via minimizing **Jerk** (the 3rd derivative of position, $da/dt$).
* **Momentum Ride / Energy Conservation:** Using existing momentum rather than muscular force. Measured via **Kinetic Energy** ($E_k \approx v^2$) variance and flow.
* **The "Rolling Point of Contact":** Moving across a partner without sliding. Measured via topological distance matrices across the skeletal graph (the point of minimum distance migrates but never breaks zero).
* **Spherical Space / Degrees of Freedom:** Moving in 3D rather than 2D. Measured via **Principal Component Analysis (PCA)** of the 17 skeletal joints to see dimensionality expansion.
* **Falling as Flying:** Spiraling to the floor safely. Measured via Center of Mass (CoM) vertical velocity curves.

## 2. Experimental Designs Discussed

### A. The "Somatic Echo" (A-B-A Design) - *Current Frontrunner*
* **Design:** Solo (Phase A) $\to$ CI Duet (Phase B) $\to$ Solo (Phase C).
* **Question:** What is the residue of the contact? Does the dancer retain the CI Movement Algorithms (e.g., lower jerk, lower CoM) in their Phase C solo? 

### B. Task Constraints ("Rules of the Game")
* **Design:** Duets under different rules (Baseline vs Eyes Closed vs No Hands).
* **Question:** How do physical/sensory constraints alter dyadic phase-locking and cross-correlation?

### C. Signatures of Expertise (Training Background)
* **Design:** Formally trained (e.g., UNA) dyads vs Community-trained dyads.
* **Question:** Can computational kinematics mathematically distinguish between different institutional training backgrounds in open improvisation?

### D. The Topology of Roles (Initiating vs Following)
* **Question:** Can asymmetric temporal cross-correlation ($\tau^* \ne 0$) or Transfer Entropy mathematically identify moments of "leading" and "following" in a leaderless dance?

### E. Unsupervised State Discovery (Machine Learning)
* **Question:** Can Hidden Markov Models (HMM) or K-Means clustering automatically segment a CI duet into states (Floorwork, Lifts, Counterbalance, Separation) based purely on kinematics?

## 3. Scaling: Trios, Quartets, and Jams
We explored analyzing 3+ dancers. 
* **The Concept:** Moving from "coupled pendulums" to **Network/Graph Theory** (centrality, multi-agent synchronization).
* **The Technical Limitation:** 2D Pose Estimators (YOLO/MMPose) suffer from severe occlusion and identity-swapping when 3+ people are in tight physical contact. 
* **Conclusion:** Tracking full skeletons in a CI trio with a single camera is currently an unsolved problem in Computer Vision. If attempted, the analysis would have to rely on Center of Mass (bounding boxes) rather than detailed joints. Best left as Future Work or a PhD topic.
