# Data Collection Protocol (Phase 2) — revised after the October 2026 audit

## 0. Ethics first
* Ethics-committee approval (FCEN) and written informed consent from every participant before
  any recording. Consent covers pose extraction, storage of skeleton data, and (separately,
  opt-in) use of stills in the thesis. No minors.
* Participants are identified by a dyad code only. Raw video stays on an encrypted drive in
  `tesis_escritura/06_Dataset_Crudo/` and is never pushed to a public repository.

## 1. Cameras (two, synchronized)
* **Side camera**, tripod, lens height 1.3 m, 60 fps, 1080p or better, wide enough that both
  dancers stay in frame for the whole session. This view carries the vertical axis (lifts, falls,
  CoG height) and is the source of all kinematics.
* **Ceiling camera** (GoPro-class, wide lens), 30 fps, straight down. Used only for floor-plane
  position / distance in metres and for jam topology. Pose estimation is *not* run on this view.
* Why not top-down only: COCO pose models degrade badly from above and the vertical axis, where
  yielding and lifts happen, disappears.
* Sync: a clap at the start of every session, visible in both views.

## 2. Calibration (mandatory, 2 minutes per session)
* Place a 1 m floor grid or a checkerboard on the floor in both views; record 10 s.
* Record 20 s of a **motionless** person standing in the side view: this gives the empirical
  keypoint-jitter noise floor for that camera/lighting (see METHODS.md §4).
* Store `px_per_meter` for the side camera and the floor homography for the ceiling camera in
  `calibration.json` next to the videos; pass `--px-per-meter` to the pipeline.

## 3. Environment and attire
* Even lighting, no backlit windows; plain background if possible (improves ReID and ego-motion masks).
* Contrasting tops for the two dancers (dark vs light); no baggy clothing over joints.
* No spectators inside the frame.

## 4. Intake survey
Years of CI practice, weekly hours, formal dance training (years, institution), primary learning
context. Used as covariates in the mixed models.

## 5. Session design (~30 minutes, revised 7 Oct after AUDIT 27-29)
The primary question is whether coupling exists **without contact**. Public footage cannot answer it:
camera motion, editing, music and wrong-person tracking all produce "coupling" (AUDIT 27). The session
therefore contains its own null: a condition with the same room, camera, light, sound and dancers,
in which the two dancers move at the same time but are asked *not* to relate to each other.

| Block | Duration | Instruction | Role |
|---|---|---|---|
| S  solo-solo | 4 min | "Both of you improvise at the same time, each in your own half of the room. Do not relate to your partner; keep your attention on your own movement." | nuisance-matched null |
| N  no-touch duet | 4 min | "Improvise together, listening to each other, but without touching." | **primary test** (H3b) |
| B  CI duet | 5 min | "Contact Improvisation: weight sharing, momentum, rolling point of contact." | contact coupling (positive control) |
| A / C  solo before / after B | 3 + 3 min | as in the A-B-A design | secondary study (somatic echo) |

* **Short repeated trials instead of one long block** (validated on Bigand et al. 2024, AUDIT 34): run S
  and N as 8 trials of 60 s each, interleaved in randomized pairs, rather than one 4-min block each. The
  partner effect in that dataset (Δ peak|r| ≈ 0.04) was detectable with 10 dyads only because of
  this repetition. For S, a curtain or back-to-back facing is a stronger "no relating" manipulation
  than an instruction alone.
* Order: S/N trials interleaved and counterbalanced; A-B-C last so the duet cannot contaminate S/N.
* **Silence** in S and N (no music): removes the shared-music explanation entirely. An optional
  extra N block with music measures how much music adds.
* Primary contrast, pre-registered: per dyad, peak |r| (±2 s) of **vertical torso velocity ("bounce")**
  and of torso speed, mean over trials, in N minus in S; across dyads, Wilcoxon signed-rank on the differences, plus the pseudo-pair null (dancer A of
  dyad i in N with dancer B of dyad j in N). Secondary: lead/lag in N on identity-verified frames.
* Size: **15-20 dyads with 8 one-minute trials per condition.** Empirical power from the Bigand et al.
  (2024) data with the same contrast, degraded to video quality (AUDIT 37): 15 dyads 0.81-0.93,
  20 dyads 0.89-0.98, 10 dyads 0.60-0.77; with only 2 trials per condition 20 dyads give 0.50-0.63.
  That reference effect is for non-expert dancers seeing vs not seeing each other (Δ peak|r| ≈ 0.03);
  CI dancers trained in peripheral attention may differ. The pilot (2-3 dyads) checks it.

## 6. Pre-registered outcome metrics
Coupling (primary): peak |r| of torso speeds in m/s within ±2 s, gap-aware, no-contact frames,
with the null battery of `METHODS.md` §7 (H3/H3b). Smoothness (secondary, A-B-C only): SPARC and
LDLJ aggregated over each phase (4 s windows, never interpreted singly), floor-contact fraction,
vertical CoG range (m). Mixed models with dancer and dyad random effects. No raw pixel jerk.

## 7. Processing
`run_tracking.py` -> `run_features.py --px-per-meter ...` -> phase annotations
(`annotations/<dyad>.csv`, labels `block_S`, `block_N`, `phase_A`, `phase_B`, `phase_C`) ->
`analyze_coupling.py` / `analyze_claims.py`. Run `audit_identity.py` on every session and review the
contact sheets before analysis (the pair audit gate of `METHODS.md` §8). Check `tracking_quality.json` for every session before analysis; sessions
with suspected identity swaps during Phase B get a manual swap annotation.
