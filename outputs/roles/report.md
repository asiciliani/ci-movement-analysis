# Role symmetry: who is on top (CI) / who travels or turns (salsa)

Method and caveats in the docstring of roles.py. Check sheets: outputs/roles/check_roles_*.jpg; verdicts role_check.csv.

## CI weight-sharing episodes (10 duets)

Detector episodes: 135. By eye: real 89, false 29, unclear 17; flyer identifiable by appearance in 85. All false positives are one dancer standing or kneeling next to a partner who is low (lying, seated, on all fours): 'pelvis above the partner's shoulders' without being on them.

Detector's role (which tracked body is on top) vs eye, where both known: the tracked 'top' body is the eye flyer in 69/83 (errors: the flyer folded over or inverted on a standing base, whose pelvis is then higher).
Tracked identity swaps between consecutive checked episodes of the same duet: 14/59.

Per duet (share_first = share of episodes with tracked A on top / with the duet's most frequent flyer on top; switches between consecutive episodes vs within-duet permutation):

| group            | labels                           |   n |   share_first |   binom_p |   switches |   switches_expected |   p_alternate_more |   p_alternate_less | main_flyer   |
|:-----------------|:---------------------------------|----:|--------------:|----------:|-----------:|--------------------:|-------------------:|-------------------:|:-------------|
| zQRF2sLK1vY      | tracked (all detector episodes)  |   5 |         0.6   |     1     |          3 |               2.415 |              0.51  |              0.9   | nan          |
| kxztAr2tQmE_full | tracked (all detector episodes)  |   2 |         1     |     0.5   |          0 |             nan     |            nan     |            nan     | nan          |
| swmrAJkYrlY_full | tracked (all detector episodes)  |   4 |         0.5   |     1     |          2 |               2.002 |              0.668 |              0.666 | nan          |
| hJQgFDsAms4_full | tracked (all detector episodes)  |  16 |         0.125 |     0.004 |          4 |               3.502 |              0.649 |              1     | nan          |
| iOEZ3i9rgYM_full | tracked (all detector episodes)  |  11 |         0.545 |     1     |          3 |               5.458 |              0.976 |              0.112 | nan          |
| dGPRMNAECKM_full | tracked (all detector episodes)  |   8 |         0.25  |     0.289 |          2 |               2.997 |              0.927 |              0.287 | nan          |
| Rc9vIJt00vs_full | tracked (all detector episodes)  |  26 |         0.385 |     0.327 |         16 |              12.313 |              0.091 |              0.964 | nan          |
| vinlwkaIW4c_full | tracked (all detector episodes)  |  14 |         0.714 |     0.18  |          1 |               5.707 |              1     |              0.002 | nan          |
| kMkJpfUGZz8_full | tracked (all detector episodes)  |  14 |         0.286 |     0.18  |          3 |               5.716 |              0.985 |              0.07  | nan          |
| YR2QCf5cL6Q_full | tracked (all detector episodes)  |  35 |         0.514 |     1     |         13 |              17.447 |              0.955 |              0.089 | nan          |
| zQRF2sLK1vY      | eye (real episodes, flyer known) |   3 |         0.667 |     1     |          1 |               1.332 |              1     |              0.668 | white        |
| kxztAr2tQmE_full | eye (real episodes, flyer known) |   2 |         1     |     0.5   |          0 |             nan     |            nan     |            nan     | grey         |
| swmrAJkYrlY_full | eye (real episodes, flyer known) |   3 |         0.667 |     1     |          2 |               1.341 |              0.341 |              1     | black        |
| hJQgFDsAms4_full | eye (real episodes, flyer known) |   9 |         0.667 |     0.508 |          1 |               3.991 |              1     |              0.024 | dark         |
| iOEZ3i9rgYM_full | eye (real episodes, flyer known) |   8 |         1     |     0.008 |          0 |             nan     |            nan     |            nan     | woman        |
| dGPRMNAECKM_full | eye (real episodes, flyer known) |   5 |         0.6   |     1     |          3 |               2.406 |              0.502 |              0.897 | navy         |
| Rc9vIJt00vs_full | eye (real episodes, flyer known) |  19 |         0.526 |     1     |          6 |               9.471 |              0.97  |              0.078 | red          |
| vinlwkaIW4c_full | eye (real episodes, flyer known) |   5 |         0.8   |     0.375 |          1 |               1.595 |              1     |              0.405 | black        |
| kMkJpfUGZz8_full | eye (real episodes, flyer known) |   7 |         0.714 |     0.453 |          3 |               2.849 |              0.664 |              0.716 | bun          |
| YR2QCf5cL6Q_full | eye (real episodes, flyer known) |  24 |         0.958 |     0     |          1 |               1.917 |              1     |              0.083 | white        |

- tracked labels: pooled switches 47 vs 57.6 expected (p alternate more = 0.989, less = 0.019); concentration on one flyer per duet 87 vs 81.0 under 50/50 coins (p = 0.069).
- eye labels: pooled switches 18 vs 24.9 expected (p alternate more = 0.995, less = 0.013); concentration on one flyer per duet 65 vs 53.5 under 50/50 coins (p = 0.000).
- What these counts can tell (episode counts per duet [19, 24, 5, 9, 8, 7, 2, 3, 5, 3]): if each duet had one dancer on top with probability p, p = 0.7: power 0.77, P(stat <= observed 65) = 0.876; p = 0.8: power 1.00, P(stat <= observed 65) = 0.195; p = 0.9: power 1.00, P(stat <= observed 65) = 0.000; p = 1.0: power 1.00, P(stat <= observed 65) = 0.000. Perfect alternation in every duet would give p = 0.001 on the switch test; a switch probability of 0.8 would be detected about half the time.
- On the same 85 eye-labelled episodes: tracked A/B labels give 35 role switches, the eye labels 18.

## Salsa, CoMPAS3D 3-D (roles known): who travels more / who turns more per annotated figure

35 sequences, 5 pairs, 1975 'Together' figures (>= 1 s); trunk yaw from markers in 35 sequences.

Known-answer check of the turn measure (annotation says who turns):

| turn_target   |    n |   follower_turns_more |   yaw_leader_med |   yaw_follower_med |
|:--------------|-----:|----------------------:|-----------------:|-------------------:|
| both          |  151 |                  0.81 |           298.56 |             427.18 |
| follower      |  629 |                  0.97 |           156.64 |             491.99 |
| leader        |   96 |                  0.58 |           306.1  |             302.79 |
| none          | 1085 |                  0.69 |           128.45 |             219.34 |
| other         |   14 |                  0.93 |           231.89 |             631.78 |

### travels_more (share = leader)

Pooled figures: 410/1975 = 21% (binomial p = 2.1e-158); per pair {'Pair1': 0.24, 'Pair2': 0.26, 'Pair3': 0.1, 'Pair4': 0.26, 'Pair5': 0.16}; sequences with binomial p < 0.05: 34/35.
Alternation (switches between consecutive figures, permuted within sequence): observed 569, expected 617.2, p(more) = 0.999, p(less) = 0.001.

### turns_more (share = follower)

Pooled figures: 1547/1975 = 78% (binomial p = 3.9e-148); per pair {'Pair1': 0.51, 'Pair2': 0.96, 'Pair3': 0.92, 'Pair4': 0.66, 'Pair5': 0.9}; sequences with binomial p < 0.05: 25/35.
Alternation (switches between consecutive figures, permuted within sequence): observed 489, expected 535.4, p(more) = 1.000, p(less) = 0.001.

## Salsa renders in 2-D (same pipeline as CI): who travels more per annotated figure

Identity oracle: one projective camera fitted to the 3-D root positions and the tracked 2-D hips, per-frame assignment (which track is the leader) chosen by the smaller reprojection error.

| seq               |   frames_both |   track0_is_leader |   swaps |   res_px_median |   res_other_px_median |
|:------------------|--------------:|-------------------:|--------:|----------------:|----------------------:|
| Pair1_song1_take1 |           760 |               0.74 |      44 |           46.29 |                 76    |
| Pair2_song2_take1 |          1539 |               0.93 |      12 |           38.01 |                102.58 |
| Pair5_song2_take1 |          1571 |               0.55 |      57 |           43.5  |                 84.62 |

- Pair1_song1_take1: 24 figures. 3-D truth: leader travels more in 12%. 2-D tracked labels (majority mapping): 62%, agreement with 3-D 42%; oracle-corrected: 42%, agreement 54%. Switches: tracked 7 (exp 11.2, p_more 0.98), corrected 6 (exp 11.7), 3-D 4 (exp 5.3).
- Pair2_song2_take1: 25 figures. 3-D truth: leader travels more in 24%. 2-D tracked labels (majority mapping): 88%, agreement with 3-D 36%; oracle-corrected: 72%, agreement 28%. Switches: tracked 6 (exp 5.3, p_more 0.57), corrected 9 (exp 10.1), 3-D 7 (exp 9.1).
- Pair5_song2_take1: 24 figures. 3-D truth: leader travels more in 17%. 2-D tracked labels (majority mapping): 58%, agreement with 3-D 42%; oracle-corrected: 75%, agreement 42%. Switches: tracked 5 (exp 11.7, p_more 1.00), corrected 6 (exp 9.0), 3-D 5 (exp 6.7).