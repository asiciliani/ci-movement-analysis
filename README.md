# Contact Improvisation Movement Analysis

Video-based kinematics of Contact Improvisation (CI) duets. Licenciatura thesis in Computer
Science (UBA / FCEN - Exactas). The pipeline extracts 2-D skeletons from ordinary video,
tracks the two dancers through contact and occlusion, and derives calibrated, noise-aware
kinematic and smoothness features together with within-dyad statistical tests.

> Research question: which qualities of Contact Improvisation can be characterised from ordinary
> video, without sensors or new recordings: how a duet touches, shares weight, uses the floor and moves
> between these states, and how that differs from other partner dances?

Since 8 Oct 2026 the main line is **descriptive** (contact, weight sharing, floor, state grammar, CI vs
salsa), measured on public footage and checked against datasets with a known answer. The original
coupling question ("do the dancers listen to each other without touching?") is kept as a Phase-2 design
that needs new recordings.

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

Descriptive branch (on the pair-verified duets, full-length versions preferred):

```
describe_duets.py      contact + body regions, weight sharing, levels, descents, 1-s pose vocabulary  -> outputs/describe/
state_grammar.py       per-frame duet state (apart/near/contact/weight share/floor), transitions      -> outputs/grammar/
hand_check_contacts.py check sheets for contact releases; verdicts behind the SEP_BL release rule      -> outputs/grammar/contact_check*.csv
compare_genres.py      the same descriptors on CI vs salsa (CoMPAS3D renders, known answer)           -> outputs/compare_genres/
rolling_3d.py          rolling vs gripping on salsa mocap markers (region yes, travel no)             -> outputs/rolling_3d/
rolling_mesh.py        rolling vs gripping on SMPL-X body meshes (needs the licensed model files)     -> outputs/rolling_mesh/
demo_video.py          one-minute demo: duet with skeletons + live panel of what is measured          -> outputs/demo/ (not in git)
```

External ground truth: `analyze_external_bigand.py` (Bigand et al. 2024, free dance, known coupling),
`analyze_external_compas.py` (CoMPAS3D salsa, known roles). Data are downloaded by the scripts in
`data_external/*/` (not redistributed; the SMPL-X model files need a free academic licence from
smpl-x.is.tue.mpg.de).

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

Descriptive results (AUDIT 38-44): on 10 pair-verified duets (20.7 min) contact, weight sharing, levels
and the state grammar pass checks by eye and the salsa known-answer check; contact releases were
hand-checked (out-of-sample 71 % real after the release rule). Rolling vs gripping is not measurable from
2-D skeletons, nor from sparse 3-D markers; the mesh version is being validated on salsa. The pose
vocabulary does not yet identify duets ("signature" at chance).

Coupling: none of the hypotheses is "proven" by this repository. On public footage the coupling question is
not decidable (6 right-pair clips, almost all in contact; AUDIT 24-31); it is answered by the Phase-2 design with a
solo-solo block as a nuisance-matched null (`DATA_COLLECTION_PROTOCOL.md`). Current results:
`outputs/coupling/coupling_report.md`, `outputs/claims/claims_report.md`, discussed in `AUDIT.md`.
