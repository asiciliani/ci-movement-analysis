# Contact Improvisation Movement Analysis

Video-based kinematics of Contact Improvisation (CI) duets. Licenciatura thesis in Computer
Science (UBA / FCEN - Exactas). The pipeline extracts 2-D skeletons from ordinary video,
tracks the two dancers through contact and occlusion, and derives calibrated, noise-aware
kinematic and smoothness features together with within-dyad statistical tests.

> Research question: how does interpersonal movement coordination emerge and change during
> Contact Improvisation, and which of its qualities can be characterised from video?

This repository was audited and restructured in October 2026. `AUDIT.md` lists what was wrong
before and what changed; `METHODS.md` is the normative definition of every feature.

## Pipeline

```
video ──► run_tracking.py ──► <stem>_tracks.npz          (YOLOv8-pose + BoT-SORT/ReID + 2-dancer assignment,
                               <stem>_detections.csv      camera ego-motion, tracking diagnostics)
                               <stem>_tracking_quality.json
       ──► run_features.py ──► <stem>_features.csv        (per frame: positions, gap-aware derivatives in px and
                               <stem>_windows.csv          calibrated units, contact state, dir. similarity)
                               <stem>_feature_info.json   (per window: SPARC, LDLJ, KE-transfer r, contact fraction)
       ──► audit_identity.py ──► contact sheets  ──► human verdicts in videos/curation.csv (content, pair_ok)
       ──► aggregate_dataset.py ──► outputs/dataset/{videos,frames,windows}.csv   (inclusion rules applied)
       ──► analyze_coupling.py ──► outputs/coupling/coupling_report.md            (coupling vs a battery of nulls)
       ──► analyze_claims.py ──► outputs/claims/claims_report.md                  (smoothness / within-video tests)
```

`run_analysis.py` chains stage 1 + 2 and renders the dashboard, trajectory plot, annotated
video and HTML report (same CLI as before). `run_group_analysis.py` builds a proximity graph
over all detections of a multi-person clip.

```bash
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
python run_tracking.py --video videos/ci_duet_sample.mp4
python run_features.py --tracks outputs/ci_duet_sample/ci_duet_sample_tracks.npz
python run_analysis.py --video videos/ci_duet_sample.mp4 --annotations annotations/ci_duet_sample.csv
python audit_identity.py --tracks outputs/<stem>/<stem>_tracks.npz --video videos/<stem>.mp4   # then edit videos/curation.csv
python aggregate_dataset.py && python analyze_coupling.py && python analyze_claims.py
python scripts/simulate_design.py      # Phase-2 design: naive-test false positives, N-S contrast power
python -m pytest tests -q
```

## What the features are (short version; see METHODS.md)

* **Units.** Everything is stored in pixels (`*_speed`, `*_jerk`, `dist_*`) *and* in calibrated
  units (`*_u`): metres when `--px-per-meter` is given, otherwise body lengths (bl), one bl being
  the dancer's median trunk length in that video. Only `_u` columns are comparable across videos.
* **Derivatives.** Savitzky-Golay (window 11, order 3) on contiguous detected runs only. Gaps
  longer than 2 frames are never interpolated; the half-window at each run edge is dropped.
  Implausible speeds are dropped, not clipped.
* **Noise floor.** Keypoint jitter is estimated from the filter residual and propagated through
  the third-derivative filter; `feature_info.json` reports the jerk noise floor next to the
  median jerk. Per-frame jerk below ~3x the floor is mostly pose noise.
* **Smoothness.** SPARC and LDLJ (Balasubramanian et al. 2015) on 4 s windows with complete
  derivatives, aggregated over minutes (single windows are noise at 24-30 fps).
* **Contact state.** Minimum inter-skeleton keypoint distance below 0.35 bl, median-filtered.
* **Coordination.** Gap-aware lagged cross-correlation of speeds tested against a battery of
  nulls (circular and local shifts, frequency bands, camera / apparent-scale / audio partialling,
  pseudo-pairs; `src/analysis/coupling_controls.py`). The circular-shift test alone also fires on
  wrongly tracked pairs (AUDIT 27), so it is never reported alone.
* **Camera.** Background ego-motion per frame (RANSAC similarity fit on masked optical flow),
  compensated in the kinematics when the fit is reliable; otherwise the clip is excluded.
* **Pair audit.** A clip enters coupling analyses only after a person has checked, on the
  contact sheets, that the two tracked people are the two dancers (spectators, shadows and edited
  montages were all found in the public corpus).

## Layout

```
src/pose/            YOLOv8-pose wrapper (default tracker: configs/botsort_reid.yaml)
src/tracking/        two-dancer assignment with diagnostics; camera ego-motion
src/features/        scale, kinematics, smoothness (SPARC/LDLJ), contact, LMA-shape descriptors
src/analysis/        coupling_controls (gap-aware xcorr + null battery), audio (music covariate), coordination, claims, group_graph
src/visualization/   dashboard, trajectories, overlay video, HTML report
src/io/              tracks file format
scripts/             process_queue.sh, acquire_*.sh, screen_candidates.py (full body, cuts, crowd), simulate_design.py
tests/               synthetic tests for gap handling, noise floor, scale invariance, lag sign, surrogates
```

## Status of the scientific claims

None of the hypotheses is "proven" by this repository. On public footage the coupling question is
not decidable (6 right-pair clips, almost all in contact; AUDIT 24-31); it is answered by the Phase-2 design with a
solo-solo block as a nuisance-matched null (`DATA_COLLECTION_PROTOCOL.md`). Current results:
`outputs/coupling/coupling_report.md`, `outputs/claims/claims_report.md`, discussed in `AUDIT.md`.
