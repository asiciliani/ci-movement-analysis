# CI vs partnering (partenaire): hypotheses written before looking at any partnering data

*Written 13 Oct 2026, before any partnering video was downloaded or tracked. The git history of this file is
the timestamp. Anything analysed later that is not listed here is exploratory and must be reported as such.*

## Why this comparison
Salsa differs from CI in whether weight is shared at all (AUDIT 40). Partnering (ballet pas de deux,
contemporary partnering) also lifts and carries, so the question becomes **how** weight is shared. The
working idea: partnering uses the partner's body as a support to show a form; CI uses it as a surface the
weight travels over. Several items restate, in measurable terms, what Paxton and Nancy Stark Smith say in
*Fall After Newton* (notes in the private writing repo).

## Material and inclusion (fixed in advance)
* Public video, one camera, both dancers in shot, single shot or cuts removed; same pipeline and the same
  screening rules as the CI corpus (`METHODS.md`, pair audit by eye).
* At least 8 partnering duets from at least 5 different sources, at least 15 minutes with both dancers
  visible; classical pas de deux and contemporary partnering reported separately and pooled.
* The CI side is the pair-verified corpus as it stands on the day partnering tracking starts.
* Unit of analysis: the duet. Tests: Mann-Whitney across duets, two-sided, alpha 0.05, no correction;
  the seven hypotheses below are all reported, whatever they show.

## Hypotheses (direction stated; "CI >" means larger in CI)
| # | Statement | Measure (existing code unless noted) | Expected |
|---|---|---|---|
| H1 | CI uses the floor, partnering does not | fraction of time with a dancer at floor level (`describe.level`) | CI > |
| H2 | In partnering the same person is lifted; in CI it varies | per duet, share of weight-sharing episodes with the more frequent flyer, identity by eye (`roles.py`) | partnering > |
| H3 | Partnering lifts are held as shapes; CI weight passes through | median duration of weight-sharing episodes; fraction of each episode with both pelvis speeds < 0.25 bl/s (to add) | partnering > for both |
| H4 | The base stays vertical in partnering | trunk inclination of the lower dancer during weight sharing (to add) | CI > (more inclined) |
| H5 | Partnering supports with the hands; CI with the trunk | share of weight-sharing frames whose contact involves a hand of the lower dancer vs trunk-trunk / trunk-leg (`describe.contact_regions`) | hand share: partnering >; trunk share: CI > |
| H6 | CI stays in contact around a lift; partnering separates or holds hands | state before and after each weight-sharing episode (`state_grammar`): share of episodes entered from and left to "contact" rather than "near/apart" | CI > |
| H7 | CI spends more time off the vertical axis | fraction of time with trunk inclination > 30 degrees while not at floor level, per dancer (to add) | CI > |

Secondary, exploratory by declaration (weak instruments): movement on the musical beat (`src/analysis/audio.py`
envelope vs pelvis speed), repetition of pose-word sequences (`novelty.py`), rate of full stops per minute.
Smoothness is **not** tested: jerk-based measures are at the noise floor on this kind of video (AUDIT 1-23,
50) and the expected direction is unclear (rehearsed choreography may well be smoother).

## Known threats, stated now
* Stage footage of ballet is often cut and filmed from far: fewer usable minutes, smaller bodies.
* Costumes (tutus, loose clothing) and pointe shoes degrade keypoints; the pair audit must be repeated.
* Weight-sharing detection has ~22 % false positives in CI (AUDIT 45) and was tuned on CI: check a sample of
  partnering episodes by eye before any comparison, and report the error rate per genre.
* 2-D: who is "over" whom depends on the camera; H2 uses identity by eye, not tracked labels.
