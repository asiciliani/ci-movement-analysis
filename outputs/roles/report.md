# Role symmetry: who is on top (CI) / who travels or turns (salsa)

Method and caveats in the docstring of roles.py. Check sheets: outputs/roles/check_roles_*.jpg; verdicts role_check.csv.

## CI weight-sharing episodes (10 duets)

Detector episodes: 42. By eye: real 28, false 8, unclear 6; flyer identifiable by appearance in 26. All false positives are one dancer standing or kneeling next to a partner who is low (lying, seated, on all fours): 'pelvis above the partner's shoulders' without being on them.

Detector's role (which tracked body is on top) vs eye, where both known: the tracked 'top' body is the eye flyer in 19/21 (errors: the flyer folded over or inverted on a standing base, whose pelvis is then higher).
Tracked identity swaps between consecutive checked episodes of the same duet: 3/12.

Per duet (share_first = share of episodes with tracked A on top / with the duet's most frequent flyer on top; switches between consecutive episodes vs within-duet permutation):

| group            | labels                           |   n |   share_first |   binom_p |   switches |   switches_expected |   p_alternate_more |   p_alternate_less | main_flyer   |
|:-----------------|:---------------------------------|----:|--------------:|----------:|-----------:|--------------------:|-------------------:|-------------------:|:-------------|
| zQRF2sLK1vY      | tracked (all detector episodes)  |   2 |         0.5   |     1     |          1 |             nan     |            nan     |            nan     | nan          |
| kxztAr2tQmE_full | tracked (all detector episodes)  |   2 |         1     |     0.5   |          0 |             nan     |            nan     |            nan     | nan          |
| swmrAJkYrlY_full | tracked (all detector episodes)  |   1 |         0     |     1     |          0 |             nan     |            nan     |            nan     | nan          |
| hJQgFDsAms4_full | tracked (all detector episodes)  |   3 |         0.333 |     1     |          1 |               1.331 |              1     |              0.669 | nan          |
| iOEZ3i9rgYM_full | tracked (all detector episodes)  |   6 |         0.167 |     0.219 |          1 |               1.667 |              1     |              0.333 | nan          |
| dGPRMNAECKM_full | tracked (all detector episodes)  |   6 |         0.167 |     0.219 |          1 |               1.67  |              1     |              0.33  | nan          |
| Rc9vIJt00vs_full | tracked (all detector episodes)  |  11 |         0.455 |     1     |          5 |               5.465 |              0.741 |              0.517 | nan          |
| vinlwkaIW4c_full | tracked (all detector episodes)  |   6 |         0.667 |     0.688 |          1 |               2.662 |              1     |              0.135 | nan          |
| kMkJpfUGZz8_full | tracked (all detector episodes)  |   4 |         0     |     0.125 |          0 |             nan     |            nan     |            nan     | nan          |
| uS1JQ-LY8Fs_full | tracked (all detector episodes)  |   1 |         0     |     1     |          0 |             nan     |            nan     |            nan     | nan          |
| kxztAr2tQmE_full | eye (real episodes, flyer known) |   2 |         1     |     0.5   |          0 |             nan     |            nan     |            nan     | grey         |
| swmrAJkYrlY_full | eye (real episodes, flyer known) |   1 |         1     |     1     |          0 |             nan     |            nan     |            nan     | orange       |
| hJQgFDsAms4_full | eye (real episodes, flyer known) |   2 |         1     |     0.5   |          0 |             nan     |            nan     |            nan     | light        |
| iOEZ3i9rgYM_full | eye (real episodes, flyer known) |   5 |         1     |     0.062 |          0 |             nan     |            nan     |            nan     | woman        |
| dGPRMNAECKM_full | eye (real episodes, flyer known) |   4 |         0.5   |     1     |          3 |               2.004 |              0.337 |              1     | navy         |
| Rc9vIJt00vs_full | eye (real episodes, flyer known) |   8 |         0.5   |     1     |          3 |               3.998 |              0.884 |              0.372 | blue         |
| vinlwkaIW4c_full | eye (real episodes, flyer known) |   2 |         1     |     0.5   |          0 |             nan     |            nan     |            nan     | black        |
| kMkJpfUGZz8_full | eye (real episodes, flyer known) |   2 |         1     |     0.5   |          0 |             nan     |            nan     |            nan     | man          |

- tracked labels: pooled switches 10 vs 13.8 expected (p alternate more = 0.984, less = 0.048); concentration on one flyer per duet 31 vs 28.7 under 50/50 coins (p = 0.175).
- eye labels: pooled switches 6 vs 6.0 expected (p alternate more = 0.624, less = 0.634); concentration on one flyer per duet 20 vs 18.3 under 50/50 coins (p = 0.219).
- What these counts can tell (episode counts per duet [8, 4, 2, 5, 2, 2, 1, 2]): if each duet had one dancer on top with probability p, p = 0.7: power 0.17, P(stat <= observed 20) = 0.659; p = 0.8: power 0.50, P(stat <= observed 20) = 0.291; p = 0.9: power 0.92, P(stat <= observed 20) = 0.023; p = 1.0: power 1.00, P(stat <= observed 20) = 0.000. Perfect alternation in every duet would give p = 0.001 on the switch test; a switch probability of 0.8 would be detected about half the time.
- On the same 26 eye-labelled episodes: tracked A/B labels give 7 role switches, the eye labels 6.

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
Alternation (switches between consecutive figures, permuted within sequence): observed 569, expected 617.3, p(more) = 0.999, p(less) = 0.001.

### turns_more (share = follower)

Pooled figures: 1547/1975 = 78% (binomial p = 3.9e-148); per pair {'Pair1': 0.51, 'Pair2': 0.96, 'Pair3': 0.92, 'Pair4': 0.66, 'Pair5': 0.9}; sequences with binomial p < 0.05: 25/35.
Alternation (switches between consecutive figures, permuted within sequence): observed 489, expected 535.4, p(more) = 1.000, p(less) = 0.001.

## Salsa renders in 2-D (same pipeline as CI): who travels more per annotated figure

Identity oracle: one projective camera fitted to the 3-D root positions and the tracked 2-D hips, per-frame assignment (which track is the leader) chosen by the smaller reprojection error.

| seq               |   frames_both |   track0_is_leader |   swaps |   res_px_median |   res_other_px_median |
|:------------------|--------------:|-------------------:|--------:|----------------:|----------------------:|
| Pair1_song1_take1 |           567 |               0.59 |      38 |           52.51 |                 81.68 |
| Pair2_song2_take1 |          1407 |               0.54 |      18 |           38.47 |                102.91 |
| Pair5_song2_take1 |          1397 |               0.52 |      53 |           43.75 |                 82.59 |

- Pair1_song1_take1: 24 figures. 3-D truth: leader travels more in 12%. 2-D tracked labels (majority mapping): 50%, agreement with 3-D 46%; oracle-corrected: 50%, agreement 54%. Switches: tracked 5 (exp 12.0, p_more 1.00), corrected 8 (exp 12.0), 3-D 4 (exp 5.2).
- Pair2_song2_take1: 25 figures. 3-D truth: leader travels more in 24%. 2-D tracked labels (majority mapping): 56%, agreement with 3-D 44%; oracle-corrected: 68%, agreement 24%. Switches: tracked 6 (exp 12.3, p_more 1.00), corrected 10 (exp 10.9), 3-D 7 (exp 9.1).
- Pair5_song2_take1: 24 figures. 3-D truth: leader travels more in 17%. 2-D tracked labels (majority mapping): 67%, agreement with 3-D 42%; oracle-corrected: 62%, agreement 46%. Switches: tracked 9 (exp 10.7, p_more 0.85), corrected 8 (exp 11.3), 3-D 5 (exp 6.7).