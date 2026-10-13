# Thesis Proposal: The Somatic Echo

**Title:** Physical listening in Contact Improvisation: measuring interpersonal coupling from video with a validated two-dancer tracker.  
**Degree:** Licenciatura en Ciencias de la Computación (UBA / Exactas)

---

> Revised 6-7 Oct 2026. The somatic-echo A-B-A study is kept as a secondary, conditional study
> (§3); the primary question is now the one the proof-of-concept data actually support
> (see `AUDIT.md` findings 17-21 and `PLAN_DE_TESIS_ES.md`).

## 0. Primary question (evidence-based choice, revised 7 Oct)
Does kinematic coupling between two CI dancers persist when they are *not* in physical contact?
Status of the evidence: the public-video proof of concept **cannot** answer it. After a visual pair
audit, 6 public clips track the right two people; there whole-clip coupling survives every null
including pseudo-pairs (5 of 6), but those clips are mostly in contact (rigid-body coupling, the
expected positive control); the circular-shift test alone also fires on clips that track
spectators or a shadow (AUDIT 27); and no-contact coupling could be tested in one clip only
(not significant). The question
is kept because it is the one the instrument can answer with designed data: Phase 2 records each
dyad in a solo-solo condition (same room, camera and silence, no relating) and a no-touch duet, so
the null shares every nuisance (`DATA_COLLECTION_PROTOCOL.md` §5). The thesis therefore
(i) builds and validates the instrument — two-dancer tracking in dense contact with a pair audit,
camera and scale controls, and a null battery shown to reject artifact-driven coupling — and
(ii) tests no-contact coupling and lead/lag within and across dyads on the Phase-2 recordings.

## 1. Abstract & Core Research Question (secondary study)

Contact Improvisation (CI) is a unique dyadic movement practice where dancers continuously share weight and momentum. To avoid injury and maintain flow, CI dancers program specific "Movement Algorithms" (MAs) into their nervous systems—specifically, algorithms for yielding to impact (collision avoidance) and conserving kinetic energy (using momentum rather than muscular force). 

This thesis investigates whether interacting with another human body temporarily rewrites a dancer's motor algorithms. 

**Core Question:** *How does the dyadic necessity of collision avoidance and momentum transfer in Contact Improvisation alter the mathematical kinematics of a dancer's subsequent solo movement?*

---

## 2. The Movement Algorithms (MAs) Analyzed

The computational pipeline will extract 2D kinematics to mathematically prove the existence and transfer of two primary CI algorithms:

### MA 1: "The Yield" (Collision Avoidance & Soft Landing)
* **Concept:** When encountering the floor or a partner, a CI dancer does not brace or crash; they spiral and absorb the force, extending the time of deceleration to prevent injury.
* **Mathematical Signature:** movement **smoothness** of the centre of mass around floor contacts and partner contacts, measured with dimensionless metrics (SPARC, log dimensionless jerk; Balasubramanian et al. 2015) on 2 s windows, in calibrated units (metres or body lengths). Raw jerk magnitude is noise-dominated at video resolution and is reported only as a diagnostic next to its noise floor.

### MA 2: "Momentum Ride" (Kinetic Energy Conservation)
* **Concept:** Beginners use muscular force (start-and-stop movement) to lift or push. Experts redirect existing momentum, keeping the kinetic energy of the system fluid and conserved.
* **Mathematical Signature:** the **KE-transfer correlation** between the dancers (Pearson r between d/dt v_A^2 and d/dt v_B^2 in a window: negative = hand-off) and the smoothness of the flyer's speed profile during annotated lifts. Without body mass and depth, absolute kinetic energy is not measurable from monocular video; only scale-free quantities are compared.

---

## 3. Experimental Protocol (The A-B-A Design)

To isolate how CI affects the nervous system, we will use a within-subjects A-B-A experimental design. Each dyad (approx. 10-15 pairs) will be filmed in a single 10-minute continuous session:

* **Phase A (Baseline Solo):** 2 minutes. Dancers move independently in the space. This captures their default movement algorithms (baseline jerk, baseline floor usage).
* **Phase B (The CI Duet):** 5 minutes. Dancers engage in Contact Improvisation. The necessity of sharing weight forces the activation of MA 1 (Yielding) and MA 2 (Momentum Transfer).
* **Phase C (The Echo Solo):** 2 minutes. Dancers separate and immediately return to solo improvisation. 

**The Test:** We statistically compare the kinematics of Phase A against Phase C for each dancer, with a control condition (solo with the partner present, no contact) to separate contact from warm-up and fatigue, pre-registered metrics (SPARC, LDLJ, floor-contact fraction, vertical CoG range) and a power analysis from pilot variance. 
* *Does their descent to the floor in Phase C exhibit mathematically lower Jerk than in Phase A?* 
* *Is their kinetic energy usage smoother and more conserved after the physical interaction?* 

This measures the "Somatic Echo"—the residue of the partner's physics left on the solo body.

---

## 4. Technical Computer Science Stack

To satisfy the requirements of a CS Licenciatura, the thesis relies on a robust computational architecture:
1. **Computer Vision & Tracking:** YOLOv8-Pose with BoT-SORT + ReID, a two-dancer assignment layer, camera ego-motion screening, and tracking diagnostics validated against manually annotated identity swaps.
2. **Kinematic Signal Processing:** Savitzky-Golay differentiation on contiguous detected runs only (no interpolation across occlusions), calibrated units (floor grid), estimator noise floor reported per recording.
3. **Time-Series Analysis:** Cross-correlation, Phase-Locking Values (Hilbert Transform), and Principal Component Analysis (PCA) to measure degrees of freedom.
4. **Statistical Modeling:** Linear Mixed-Effects Models (LMM) in Python (`statsmodels`) to account for within-dyad dependencies and determine the statistical significance of the Phase A vs Phase C differences.
