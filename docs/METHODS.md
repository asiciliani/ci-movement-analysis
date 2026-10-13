# Methods: definitions, units and tests

This file is normative. If the thesis text and this file disagree, this file is wrong and must be fixed.

## 1. Pose and tracking
* Detector: YOLOv8-pose (COCO-17), `conf >= 0.25`. Tracker: BoT-SORT with appearance ReID
  (`configs/botsort_reid.yaml`, `track_buffer = 60`). The two foreground dancers are then
  assigned per frame by Hungarian matching on predicted torso position, bbox size and tracker-id
  continuity (`src/tracking/dancer_tracker.py`).
* Appearance cue: an HSV histogram of each dancer's torso quadrilateral, learnt only while the two
  are clearly apart, enters the assignment cost (`--appearance-weight`, default 0.5) once the two
  colour models are separable (Bhattacharyya distance > 0.2). It targets the two dominant errors
  seen in manual checks: A/B exchange after a lift and capture of a bystander. A hard gate refuses
  a detection whose torso colours clearly belong to the other dancer (Bhattacharyya > 0.45 and
  worse than the alternative by 0.15) or to neither (> 0.6 to both); the cue is skipped for
  detections whose boxes overlap another candidate (IoU > 0.3), where the crop is contaminated.
  Net effect on the benchmark clip: wrong labels in 22 sampled frames fell from ~8 to 1 while the
  detected fraction fell from 74/88 % to 66/74 % (missing beats wrong).
* Diagnostics per video (`*_tracking_quality.json`): detected fraction per dancer, dropouts,
  tracker-id switches, suspected A/B swaps, frames with extra people. These are proxies; identity
  accuracy must be measured against manual annotation (see §7).
* Occlusion is *measured*, not hidden: every downstream table carries `present_A/B` and
  `valid_deriv` flags, and every per-window metric reports the valid fraction.

## 2. Camera ego-motion
Per frame pair, sparse corners outside the person boxes are tracked (Lucas-Kanade) and a
similarity transform is fitted with RANSAC. Motion = max corner displacement induced by the
transform (full-res px). A video is **static** if at most 5 % of measured frame pairs move more
than 0.3 % of the frame width.

**Compensation.** For videos processed by `run_tracking.py` the per-frame transform is stored
(`camera_M`) and `run_features.py` computes kinematics on *compensated* trajectories: the dancer's
own displacement in frame t is `p_t − M_t(p_{t−1})`, accumulated into a virtual static frame
(§4 derivatives are unaffected by the arbitrary offset). Frames without a transform become gaps.
A moving-camera video is admitted to kinematic analysis only if >= 90 % of its detected frames
were compensated and the per-step zoom factor stays within 1 % (p95), because zoom changes the
px/bl scale over time. Videos processed from legacy CSVs cannot be compensated and stay excluded.
`videos.csv` records `camera_static`, `camera_compensated`, `camera_ok`.

## 3. Body scale and units
* `scale_X` = median trunk length (shoulder-mid to hip-mid) of dancer X over confidently detected
  frames, in px. Fallback: 0.3 x median bbox height.
* With a floor calibration, `--px-per-meter` replaces both scales and units are metres.
* Columns ending in `_u` are in calibrated units; inter-dancer distances use the mean of the two
  scales. Pixel columns are kept only for plotting and are **not** comparable across videos.

## 4. Derivatives
Positions (torso centre = mean of shoulders and hips; pelvis = hip midpoint) are differentiated
with a Savitzky-Golay filter (window 11 samples, polynomial order 3, `delta = 1/fps`) applied to
each contiguous run of detected frames. Gaps of <= 2 frames are filled linearly and flagged
(`filled_X`); longer gaps split the run. The 5 samples at each run edge are discarded. Single-frame
jumps > 1 bl and speeds > 15 bl/s are set to NaN (tracker glitches), never clipped.

Noise floor: per-axis jitter sigma is estimated from the magnitude of the smoothing residual
(Rayleigh: median/1.1774). The expected jerk magnitude from pure jitter is
`sqrt(pi/2) * ||c3|| * sigma`, where `c3` are the third-derivative filter coefficients. Reported as
`*_jerk_noise_floor_u` in `feature_info.json`. At 30 fps and window 11, sigma = 1 px gives
~2 600 px/s^3; typical YOLOv8n jitter is 2-4 px.

## 5. Smoothness (the quantities used for claims)
Computed on 4 s windows, step 1 s, only when the derivative is valid in 100 % of the window
(2 s windows gave adjacent-window autocorrelation ≈ 0 for SPARC, i.e. per-window values were
noise; at 4 s per-dancer medians are stable, split-half ρ = 0.87). SPARC/LDLJ must be aggregated
over minutes before comparison; never interpret a single window:
* **SPARC** of the speed profile (Balasubramanian et al. 2015; `fc = 6 Hz`, `amp_th = 0.05`). Dimensionless.
* **LDLJ** (velocity-based log dimensionless jerk). Dimensionless.
* `median_jerk_u` is reported for transparency but is noise-sensitive by construction.
Raw `jerk * kinetic_energy` ("Effort") was removed: it had units px^3/s^5, no mass, and does not
correspond to Laban Weight Effort as operationalised in the automated-LMA literature.

## 6. Interaction features
* Contact proxy: minimum distance between any confident keypoint pair; `contact_state = 1` when
  it is < 0.35 bl (median filter, 5 frames). Hand-to-hip distance as a secondary proxy.
* `ke_transfer_r`: Pearson r between d/dt(speed_A^2) and d/dt(speed_B^2) within a window. Negative
  values indicate one dancer decelerating while the other accelerates (a momentum hand-off).
* Lagged cross-correlation of speeds (±2 s). Positive lag = A precedes B (verified in tests).
  Significance by circular-shift surrogates (200 shifts >= 5 s): preserves each signal's
  autocorrelation, destroys alignment. A peak at the ±2 s window edge is reported as artifact-prone.
* Directional similarity: cosine of the two velocity vectors.
* Zero-lag, high correlation while in contact is the *null expectation* (two bodies moving as one),
  not evidence of anticipation. Lead/lag claims require the no-contact windows.

## 7. Hypotheses and how they are tested (`analyze_claims.py`)
Everything is tested within video first, then combined across videos; each video is one
observation in the combination.
* **H1 State-dependent smoothness.** Per video: median SPARC/LDLJ/jerk in windows with
  `contact_fraction >= 0.8` minus windows with `<= 0.2`, both dancers pooled; Cliff's delta as
  effect size. Across videos: sign test and Wilcoxon on the per-video differences; mixed model
  `metric ~ contact + (1 | video:dancer)`.
* **H2 Momentum transfer.** Fraction of contact windows with `ke_transfer_r < -0.2` vs no-contact windows.
* **H3 Coupling** (`analyze_coupling.py`, normative since 7 Oct). Statistic: peak |r| of the two
  torso speeds within ±2 s, computed gap-aware (each lag on its own jointly valid frames, never
  concatenating across gaps). A clip enters only if its tracked pair passed the visual pair audit
  (`videos/curation.csv: pair_ok`). Each clip is tested against a battery of nulls, each removing
  one alternative explanation: circular shifts ≥ 5 s (chance alignment); shifts of 3-10 s (slow
  shared modulation only); band-limited speeds (< 0.5, 0.5-1.5, > 1.5 Hz; shared jitter lives at
  high frequency); speeds partialled on camera motion, on the shared log trunk length (zoom, dolly,
  depth) and on the audio energy/onset envelopes (music); speeds in each dancer's own rolling
  trunk length; pseudo-pairs (dancer A of one clip vs dancer B of a clip from another source).
  Clip p-values are combined with Stouffer's method within source group (one recording event)
  and then across groups; groups are the unit of inference.
  **Why so many nulls:** on clips whose tracked "pair" was wrong (spectators, a wall shadow, an
  edited montage) the circular-shift test alone was significant in 3 of 5 (AUDIT 27). It is
  necessary, never sufficient.
* **Signals.** Torso speed (travel) *and* vertical torso velocity ("bounce"). On a public mocap
  dataset with a known null (Bigand et al. 2024; AUDIT 34) only the vertical signal carried the
  partner effect; speed did not.
* **H3b No-contact coupling.** The same battery restricted to frames with `contact_state == 0`,
  and binned by nearest-keypoint distance (0.35-1, 1-2, > 2 body lengths) so that keypoint mixing
  between overlapping bodies cannot carry it. Minimum 300 frames per test.
* **H3c Lead/lag — dropped as specified.** On CoMPAS3D, with known leader/follower roles and perfect
  mocap, the lag of whole-body cross-correlations does not identify the leader (AUDIT 36). Any
  leadership analysis must first be validated on that dataset with limb-level signals and a
  directional measure. A/B swaps would additionally corrupt the sign (AUDIT 30).
* **Somatic echo (A-B-A).** Not testable on the current corpus. Requires Phase-2 recordings;
  the analysis will compare Phase C vs Phase A per dancer with a mixed model and a pre-registered
  metric set (SPARC, LDLJ, floor-contact fraction, vertical CoG range), plus a control condition
  (solo with the partner present but no contact) to separate contact from warm-up/fatigue.

## 8. Inclusion rules for the corpus
Static or ego-motion-compensated camera; both dancers detected in >= 40 % of frames; >= 600
frames; body scale available; human content verdict `ci_dance` in `videos/curation.csv`; for
coupling analyses also `pair_ok == yes` (visual pair audit). Candidate screening additionally
requires full-body people, no shot cuts and <= 3 people on screen.
Applied by `aggregate_dataset.py`; the reason for every exclusion is stored in `videos.csv`.

## 9. Validation still required before the thesis
* Identity ground truth: the 7 Oct pair audit (AUDIT 25) was done by the assistant on contact
  sheets and must be repeated by a human annotator. `audit_identity.py` writes contact sheets (24 sampled frames per clip with
  A/B drawn) and a review CSV; annotate >= 10 clips x 30 s and report the fraction of frames with
  both labels on the right person, A/B exchanges, and bystander captures, with and without the
  appearance cue and ReID. The appearance-consistency score in `*_identity_audit.json` is a proxy
  only (it misses bystander captures when clothes are similar).
* Static-camera jitter test: a tripod recording of a motionless person gives the empirical noise floor.
* Metric calibration: floor grid / checkerboard in every Phase-2 recording.
