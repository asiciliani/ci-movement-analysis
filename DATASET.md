# Dataset registry

The corpus is a convenience sample of public Contact Improvisation footage used to develop and
stress-test the pipeline. It is **not** the thesis experiment: Phase 2 (controlled, calibrated,
consented recordings, see `DATA_COLLECTION_PROTOCOL.md`) is.

## Sources
* Public YouTube clips (first 60-90 s), identified by video id only. Acquired with
  `scripts/acquire_*.sh`, which download candidates to `videos/candidates/` and keep a clip only
  if the camera is static, two full-body people (hips + an ankle visible) are present in >= 60 %
  of sampled frames, there are no shot cuts and at most 3 people on screen
  (`videos/candidates.csv` records every verdict).
* **Human verdicts** in `videos/curation.csv`: `content` (ci_dance / videoconference / ...),
  `setting` (duet / duet_bystanders / jam), `source_group` (same recording event = one unit of
  inference), and the pair audit `pair_ok` (yes / partial / no) with the number of checked labels
  and errors. Clips without a verdict are excluded (`not_curated`).
* Two field recordings (`user_ci_video`, `user_small`) and one benchmark clip (`ci_duet_sample`).
  No performer names are stored in this repository.

## Inclusion rules (applied by `aggregate_dataset.py`)
| Rule | Threshold | Why |
|---|---|---|
| static camera | <= 5 % of frame pairs with global motion > 0.3 % frame width | derivatives of positions are meaningless under ego-motion |
| both dancers detected | >= 40 % of frames | enough contiguous runs for windowed metrics |
| length | >= 600 frames | at least ~40 windows |
| body scale | trunk length measurable for both | needed for calibrated units |
| content | `curation.csv: content == ci_dance` | 10 videoconference clips passed every automatic rule |
| pair (coupling only) | `curation.csv: pair_ok == yes` | 5 of 10 "duets" tracked spectators, a shadow, a trio or a montage |

`outputs/dataset/videos.csv` lists every processed video with its resolution, fps, units,
scales, detection rates, jitter, jerk noise floor, camera verdict, tracking diagnostics, and the
exclusion reason when excluded. Frame-level (`frames.csv`) and window-level (`windows.csv`)
tables contain included videos only.

## State of the corpus after the audit (6 Oct 2026)
48 processed clips: 11 were duplicates of one file, 28 more fail the static-camera screen, 6 have
too few detections; **1 clip** (`kxztAr2tQmE`) satisfies every rule from legacy data. Re-tracking
with `scripts/process_queue.sh` stores camera transforms and lets moving-camera clips re-enter
through ego-motion compensation; candidate screening of new YouTube downloads accepted 1 of 14 in
the first pass. Conclusion: public footage can validate the instrument, not the hypotheses.

## State after the pair audit (7 Oct 2026)
59 processed clips -> 20 included CI clips (10 videoconference clips removed) -> 10 curated as
duets -> **3 with a verified pair** (kxztAr2tQmE, swmrAJkYrlY, hJQgFDsAms4) + 3 with the right
people but frequent A/B swaps (iOEZ3i9rgYM, dGPRMNAECKM, and zQRF2sLK1vY after re-tracking without
its bystanders). ci_duet_sample is an excerpt of whole and occlusion_test of user_ci_video
(frame-hash matches); they share a source group. Only kxztAr2tQmE has a truly static
camera. A third acquisition pass with the stricter screen is in `scripts/acquire_round3.sh`.

## Known limitations of the current corpus
* Most clips are 24-30 fps 2-D video from unknown lenses: no metric calibration, no depth.
* The field footage `user_ci_video` has a panning camera and is excluded from kinematics.
* Several YouTube clips are performances with camera moves; the screen removes them.
* Pose jitter is 2-4 px at these resolutions, so per-frame jerk is noise-dominated; use the
  window-level SPARC/LDLJ.

## Legacy
Pre-audit feature CSVs are kept as `<stem>_features_legacy.csv` (positions were interpolated
across gaps in those files). `scripts/convert_legacy.sh` rebuilds the new schema from them
until a video is re-tracked by `scripts/process_queue.sh`.
