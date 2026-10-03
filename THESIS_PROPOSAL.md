# Thesis Proposal: The Somatic Echo

**Title:** The Somatic Echo: Computational Kinematics of Energy Transfer and Injury Prevention Algorithms in Contact Improvisation.  
**Degree:** Licenciatura en Ciencias de la Computación (UBA / Exactas)

---

## 1. Abstract & Core Research Question

Contact Improvisation (CI) is a unique dyadic movement practice where dancers continuously share weight and momentum. To avoid injury and maintain flow, CI dancers program specific "Movement Algorithms" (MAs) into their nervous systems—specifically, algorithms for yielding to impact (collision avoidance) and conserving kinetic energy (using momentum rather than muscular force). 

This thesis investigates whether interacting with another human body temporarily rewrites a dancer's motor algorithms. 

**Core Question:** *How does the dyadic necessity of collision avoidance and momentum transfer in Contact Improvisation alter the mathematical kinematics of a dancer's subsequent solo movement?*

---

## 2. The Movement Algorithms (MAs) Analyzed

The computational pipeline will extract 2D kinematics to mathematically prove the existence and transfer of two primary CI algorithms:

### MA 1: "The Yield" (Collision Avoidance & Soft Landing)
* **Concept:** When encountering the floor or a partner, a CI dancer does not brace or crash; they spiral and absorb the force, extending the time of deceleration to prevent injury.
* **Mathematical Signature:** **Jerk** (the rate of change of acceleration, $\frac{da}{dt}$). A collision is a high-jerk spike. We will measure the peak deceleration and jerk of the Center of Mass (CoM) when transitioning to the floor. An active "Yield" algorithm mathematically minimizes jerk.

### MA 2: "Momentum Ride" (Kinetic Energy Conservation)
* **Concept:** Beginners use muscular force (start-and-stop movement) to lift or push. Experts redirect existing momentum, keeping the kinetic energy of the system fluid and conserved.
* **Mathematical Signature:** **Kinetic Energy Variance and Smoothness**. We will analyze the velocity vector fields of the dancers. Fluid energy use is characterized by continuous velocity curves (minimal zero-velocity states) and conservation of $E_k \approx v^2$ during directional transitions.

---

## 3. Experimental Protocol (The A-B-A Design)

To isolate how CI affects the nervous system, we will use a within-subjects A-B-A experimental design. Each dyad (approx. 10-15 pairs) will be filmed in a single 10-minute continuous session:

* **Phase A (Baseline Solo):** 2 minutes. Dancers move independently in the space. This captures their default movement algorithms (baseline jerk, baseline floor usage).
* **Phase B (The CI Duet):** 5 minutes. Dancers engage in Contact Improvisation. The necessity of sharing weight forces the activation of MA 1 (Yielding) and MA 2 (Momentum Transfer).
* **Phase C (The Echo Solo):** 2 minutes. Dancers separate and immediately return to solo improvisation. 

**The Test:** We statistically compare the kinematics of Phase A against Phase C for each dancer. 
* *Does their descent to the floor in Phase C exhibit mathematically lower Jerk than in Phase A?* 
* *Is their kinetic energy usage smoother and more conserved after the physical interaction?* 

This measures the "Somatic Echo"—the residue of the partner's physics left on the solo body.

---

## 4. Technical Computer Science Stack

To satisfy the requirements of a CS Licenciatura, the thesis relies on a robust computational architecture:
1. **Computer Vision & Tracking:** YOLOv8-Pose for multi-person skeletal extraction, combined with custom persistent identity tracking (bipartite Hungarian matching with occlusion handling).
2. **Kinematic Signal Processing:** Savitzky-Golay filtering for smoothing pose jitter before calculating high-order derivatives (Velocity, Acceleration, Jerk).
3. **Time-Series Analysis:** Cross-correlation, Phase-Locking Values (Hilbert Transform), and Principal Component Analysis (PCA) to measure degrees of freedom.
4. **Statistical Modeling:** Linear Mixed-Effects Models (LMM) in Python (`statsmodels`) to account for within-dyad dependencies and determine the statistical significance of the Phase A vs Phase C differences.
