# Mirror vs complement: frame-wise posture similarity between partners

Method in the docstring of mirroring.py. S = - mean |zA - zB| over robust-z posture descriptors (0 = identical; about -1.1 for independent standard normals). Excess = S minus the null mean (> 0: more similar than the null).

## Summary (medians over duets / sequences)

|                                            |   units |      S |   excess_shift |   n_p_shift_lt05 |   excess_pseudo |   n_p_pseudo_lt05 |
|:-------------------------------------------|--------:|-------:|---------------:|-----------------:|----------------:|------------------:|
| ('CI 2-D', 'all', 'all')                   |      10 | -0.822 |          0.372 |               10 |           0.372 |                 9 |
| ('CI 2-D', 'all', 'apart')                 |       6 | -0.927 |          0.213 |                3 |           0.327 |                 4 |
| ('CI 2-D', 'all', 'contact')               |      10 | -0.794 |          0.405 |               10 |           0.407 |                 9 |
| ('CI 2-D', 'common7', 'all')               |      10 | -0.805 |          0.422 |                9 |           0.385 |                 9 |
| ('CI 2-D', 'common7', 'apart')             |       6 | -0.902 |          0.275 |                4 |           0.339 |                 4 |
| ('CI 2-D', 'common7', 'contact')           |      10 | -0.8   |          0.408 |               10 |           0.407 |                 9 |
| ('CI 2-D', 'shape', 'all')                 |      10 | -0.853 |          0.335 |               10 |           0.313 |                 9 |
| ('CI 2-D', 'shape', 'apart')               |       6 | -0.948 |          0.203 |                2 |           0.276 |                 4 |
| ('CI 2-D', 'shape', 'contact')             |      10 | -0.831 |          0.378 |               10 |           0.36  |                 9 |
| ('salsa 2-D render', 'all', 'all')         |       3 | -1.183 |          0.007 |                0 |           0.007 |                 0 |
| ('salsa 2-D render', 'all', 'contact')     |       3 | -1.172 |          0.013 |                0 |           0.02  |                 0 |
| ('salsa 2-D render', 'common7', 'all')     |       3 | -1.156 |         -0.002 |                0 |          -0     |                 0 |
| ('salsa 2-D render', 'common7', 'contact') |       3 | -1.153 |         -0.007 |                0 |           0.003 |                 0 |
| ('salsa 2-D render', 'shape', 'all')       |       3 | -1.175 |          0.018 |                0 |           0.019 |                 0 |
| ('salsa 2-D render', 'shape', 'contact')   |       3 | -1.155 |          0.028 |                0 |           0.033 |                 0 |
| ('salsa 3-D mocap', 'all', 'all')          |      71 | -0.91  |          0.244 |               71 |           0.24  |                71 |
| ('salsa 3-D mocap', 'common7', 'all')      |      71 | -0.91  |          0.242 |               71 |           0.239 |                71 |

## CI per duet (all descriptors, all frames)

| unit             |   n_frames |      S |   excess_shift |   z_shift |   p_shift |   excess_pseudo |   p_pseudo |
|:-----------------|-----------:|-------:|---------------:|----------:|----------:|----------------:|-----------:|
| zQRF2sLK1vY      |       1094 | -0.852 |          0.28  |     2.886 |         0 |           0.275 |      0     |
| kxztAr2tQmE_full |        539 | -0.83  |          0.481 |     5.271 |         0 |           0.377 |      0     |
| swmrAJkYrlY_full |       2044 | -0.914 |          0.338 |     7.198 |         0 |           0.309 |      0     |
| hJQgFDsAms4_full |       2234 | -0.815 |          0.355 |     6.528 |         0 |           0.368 |      0     |
| iOEZ3i9rgYM_full |       2100 | -0.775 |          0.462 |     7.805 |         0 |           0.399 |      0     |
| dGPRMNAECKM_full |       1095 | -0.74  |          0.389 |     6.7   |         0 |           0.406 |      0     |
| Rc9vIJt00vs_full |       1535 | -0.756 |          0.434 |     5.96  |         0 |           0.381 |      0     |
| vinlwkaIW4c_full |       1737 | -0.897 |          0.228 |     6.018 |         0 |           0.241 |      0     |
| kMkJpfUGZz8_full |       1987 | -0.748 |          0.438 |     6.073 |         0 |           0.384 |      0     |
| uS1JQ-LY8Fs_full |       4448 | -1.131 |          0.098 |     3.311 |         0 |           0.078 |      0.244 |

## Per descriptor: lag-0 Spearman between partners vs shift null (+ mirror / - complement; counts of units with |z| > 2)

|                                    |   r_median |   null_median |   z_median |   n_pos |   n_neg |   n |
|:-----------------------------------|-----------:|--------------:|-----------:|--------:|--------:|----:|
| ('CI 2-D', 'armup_max')            |       0.44 |         -0    |       4.42 |       8 |       0 |  10 |
| ('CI 2-D', 'armup_min')            |       0.36 |         -0.01 |       3.67 |       8 |       0 |  10 |
| ('CI 2-D', 'elbow_max')            |       0.14 |         -0.01 |       2.25 |       6 |       0 |  10 |
| ('CI 2-D', 'elbow_min')            |       0.23 |         -0    |       3.24 |       7 |       0 |  10 |
| ('CI 2-D', 'hip_max')              |       0.43 |         -0.01 |       3.94 |      10 |       0 |  10 |
| ('CI 2-D', 'hip_min')              |       0.58 |         -0.02 |       4.17 |       9 |       0 |  10 |
| ('CI 2-D', 'inverted')             |       0.49 |         -0.02 |       3.69 |       9 |       0 |  10 |
| ('CI 2-D', 'knee_max')             |       0.32 |         -0.01 |       3.52 |      10 |       0 |  10 |
| ('CI 2-D', 'knee_min')             |       0.42 |         -0.01 |       3.44 |      10 |       0 |  10 |
| ('CI 2-D', 'level')                |       0.49 |         -0.02 |       3.47 |      10 |       0 |  10 |
| ('CI 2-D', 'openness')             |       0.27 |         -0.01 |       2.77 |       8 |       0 |  10 |
| ('CI 2-D', 'stance')               |       0.16 |         -0.01 |       2.4  |       8 |       0 |  10 |
| ('CI 2-D', 'trunk_tilt')           |       0.41 |         -0.01 |       3.52 |       9 |       0 |  10 |
| ('salsa 2-D render', 'armup_max')  |       0.17 |          0.02 |       1.54 |       0 |       0 |   3 |
| ('salsa 2-D render', 'armup_min')  |       0.18 |         -0    |       1.53 |       1 |       0 |   3 |
| ('salsa 2-D render', 'elbow_max')  |       0.17 |          0    |       2.18 |       2 |       0 |   3 |
| ('salsa 2-D render', 'elbow_min')  |       0.09 |         -0    |       1.38 |       0 |       0 |   3 |
| ('salsa 2-D render', 'hip_max')    |      -0.08 |          0.01 |      -1.24 |       0 |       1 |   3 |
| ('salsa 2-D render', 'hip_min')    |      -0.17 |          0    |      -1.95 |       0 |       1 |   3 |
| ('salsa 2-D render', 'inverted')   |       0.01 |          0    |       0.04 |       0 |       0 |   3 |
| ('salsa 2-D render', 'knee_max')   |      -0.08 |          0.01 |      -1.07 |       0 |       1 |   3 |
| ('salsa 2-D render', 'knee_min')   |      -0.08 |          0.01 |      -1.08 |       0 |       1 |   3 |
| ('salsa 2-D render', 'level')      |      -0.17 |          0.06 |      -1.68 |       0 |       1 |   3 |
| ('salsa 2-D render', 'openness')   |      -0.11 |          0.02 |      -1.49 |       0 |       0 |   3 |
| ('salsa 2-D render', 'stance')     |      -0.07 |          0.01 |      -0.59 |       0 |       0 |   3 |
| ('salsa 2-D render', 'trunk_tilt') |       0.07 |          0.01 |       0.89 |       0 |       1 |   3 |
| ('salsa 3-D mocap', 'armup_max')   |       0.72 |         -0.01 |       9.33 |      71 |       0 |  71 |
| ('salsa 3-D mocap', 'armup_min')   |       0.47 |         -0.01 |       6.72 |      70 |       0 |  71 |
| ('salsa 3-D mocap', 'inverted')    |       0.13 |         -0    |       1.72 |      33 |       0 |  71 |
| ('salsa 3-D mocap', 'level')       |       0.3  |         -0    |       4.66 |      66 |       0 |  71 |
| ('salsa 3-D mocap', 'openness')    |       0.29 |         -0    |       3.94 |      55 |       1 |  71 |
| ('salsa 3-D mocap', 'stance')      |       0.18 |         -0    |       3.16 |      51 |       0 |  71 |
| ('salsa 3-D mocap', 'trunk_tilt')  |       0.14 |         -0    |       2.28 |      41 |       0 |  71 |

## 2-D measure vs 3-D truth on the salsa renders (1 s smoothed S(t), 7 common descriptors)

| seq               |   n |   r_2d_3d |   null_mean |     p |
|:------------------|----:|----------:|------------:|------:|
| Pair1_song1_take1 | 431 |     0.476 |      -0.032 | 0     |
| Pair2_song2_take1 | 799 |     0.24  |      -0.02  | 0     |
| Pair5_song2_take1 | 876 |     0.169 |      -0.015 | 0.035 |
## Controls (CI: overlap, apart, state; local 1-3 s null; salsa 3-D for comparison)

|                                                          |   units |   frames_n |   excess_median |   n_p_lt05 |
|:---------------------------------------------------------|--------:|-----------:|----------------:|-----------:|
| ('CI 2-D', 'all', 'all', 'local 1-3s')                   |      10 |      18813 |           0.149 |         10 |
| ('CI 2-D', 'all', 'all', 'shift>=5s')                    |      10 |      18813 |           0.374 |         10 |
| ('CI 2-D', 'all', 'apart(>1bl)', 'local 1-3s')           |       6 |       3599 |           0.066 |          2 |
| ('CI 2-D', 'all', 'apart(>1bl)', 'shift>=5s')            |       6 |       3599 |           0.227 |          3 |
| ('CI 2-D', 'all', 'both_standing_state', 'local 1-3s')   |      10 |      15546 |           0.146 |         10 |
| ('CI 2-D', 'all', 'both_standing_state', 'shift>=5s')    |      10 |      15546 |           0.379 |         10 |
| ('CI 2-D', 'all', 'boxes_IoU<0.2', 'local 1-3s')         |      10 |      11065 |           0.074 |          8 |
| ('CI 2-D', 'all', 'boxes_IoU<0.2', 'shift>=5s')          |      10 |      11065 |           0.338 |         10 |
| ('CI 2-D', 'all', 'floor_state', 'local 1-3s')           |       9 |       2762 |           0.133 |          6 |
| ('CI 2-D', 'all', 'floor_state', 'shift>=5s')            |       9 |       2762 |           0.292 |          6 |
| ('CI 2-D', 'shape', 'all', 'local 1-3s')                 |      10 |      18814 |           0.134 |         10 |
| ('CI 2-D', 'shape', 'all', 'shift>=5s')                  |      10 |      18814 |           0.338 |         10 |
| ('CI 2-D', 'shape', 'apart(>1bl)', 'local 1-3s')         |       6 |       3599 |           0.066 |          1 |
| ('CI 2-D', 'shape', 'apart(>1bl)', 'shift>=5s')          |       5 |       3599 |           0.147 |          2 |
| ('CI 2-D', 'shape', 'both_standing_state', 'local 1-3s') |      10 |      15547 |           0.145 |         10 |
| ('CI 2-D', 'shape', 'both_standing_state', 'shift>=5s')  |      10 |      15547 |           0.355 |         10 |
| ('CI 2-D', 'shape', 'boxes_IoU<0.2', 'local 1-3s')       |      10 |      11065 |           0.067 |          8 |
| ('CI 2-D', 'shape', 'boxes_IoU<0.2', 'shift>=5s')        |      10 |      11065 |           0.285 |          9 |
| ('CI 2-D', 'shape', 'floor_state', 'local 1-3s')         |       9 |       2762 |           0.103 |          4 |
| ('CI 2-D', 'shape', 'floor_state', 'shift>=5s')          |       9 |       2762 |           0.243 |          6 |
| ('salsa 3-D mocap', 'common7', 'all', 'local 1-3s')      |      71 |     159862 |           0.188 |         71 |
| ('salsa 3-D mocap', 'common7', 'all', 'shift>=5s')       |      71 |     159862 |           0.243 |         71 |

## Variant (v2, face keypoints not required): segment directions in each torso frame (+-2 frame best match, 10 deg tolerance, core weighted; only frames with both bodies fully in shot)

Distances in degrees (lower = more similar); excess = null - observed (> 0: more similar than the null). Mirror = B reflected left/right. In 2-D a same-side movement of two dancers facing each other looks mirrored in the image and vice versa: mirror vs same-side cannot be read as imitation style without the facing direction.

|                                   |   units |   full_frames |   mean_deg |   excess_shift_deg |   n_p_shift_lt05 |   excess_pseudo_deg |   n_p_pseudo_lt05 |   calibrated_pct |
|:----------------------------------|--------:|--------------:|-----------:|-------------------:|-----------------:|--------------------:|------------------:|-----------------:|
| ('CI 2-D', 'mirror')              |      10 |         15873 |      30.61 |               4.47 |                4 |                4.85 |                 1 |            31.11 |
| ('CI 2-D', 'same-side')           |      10 |         15873 |      21.77 |              12.6  |               10 |               12.52 |                 8 |            49.01 |
| ('salsa 2-D render', 'mirror')    |       3 |          2323 |      20.6  |              -0.7  |                0 |               -0.85 |                 0 |            -8.82 |
| ('salsa 2-D render', 'same-side') |       3 |          2323 |      17.08 |               2.31 |                1 |                3.57 |                 2 |            18.93 |

Per unit:

| genre            | unit                    | mode      |   n_full |   mean_deg |   shift_mean |   excess_shift_deg |   p_shift |   pseudo_mean |   excess_pseudo_deg |   p_pseudo |   calibrated_score_pct |
|:-----------------|:------------------------|:----------|---------:|-----------:|-------------:|-------------------:|----------:|--------------:|--------------------:|-----------:|-----------------------:|
| CI 2-D           | zQRF2sLK1vY             | same-side |      980 |     26.002 |       39.159 |             13.156 |      0    |        33.999 |               7.996 |      0.111 |                 46.541 |
| CI 2-D           | zQRF2sLK1vY             | mirror    |      980 |     34.844 |       38.594 |              3.75  |      0.14 |        35.207 |               0.363 |      0.444 |                 24.202 |
| CI 2-D           | kxztAr2tQmE_full        | same-side |      513 |     19.149 |       32.496 |             13.348 |      0    |        34.506 |              15.358 |      0     |                 47.212 |
| CI 2-D           | kxztAr2tQmE_full        | mirror    |      513 |     28.375 |       33.25  |              4.875 |      0.07 |        34.889 |               6.514 |      0.222 |                 44.067 |
| CI 2-D           | swmrAJkYrlY_full        | same-side |     1859 |     14.404 |       21.328 |              6.924 |      0    |        29.103 |              14.699 |      0     |                 33.215 |
| CI 2-D           | swmrAJkYrlY_full        | mirror    |     1859 |     18.138 |       21.226 |              3.088 |      0    |        28.951 |              10.813 |      0.111 |                 35.164 |
| CI 2-D           | hJQgFDsAms4_full        | same-side |     1566 |     23.571 |       40.189 |             16.617 |      0    |        35.862 |              12.291 |      0     |                 62.32  |
| CI 2-D           | hJQgFDsAms4_full        | mirror    |     1566 |     32.843 |       39.512 |              6.668 |      0.05 |        35.925 |               3.082 |      0.296 |                 37.59  |
| CI 2-D           | iOEZ3i9rgYM_full        | same-side |     1909 |     21.969 |       33.484 |             11.515 |      0    |        34.025 |              12.056 |      0     |                 50.8   |
| CI 2-D           | iOEZ3i9rgYM_full        | mirror    |     1909 |     27.642 |       32.885 |              5.243 |      0.04 |        32.253 |               4.611 |      0.259 |                 27.989 |
| CI 2-D           | dGPRMNAECKM_full        | same-side |      754 |     31.523 |       49.597 |             18.074 |      0    |        42.978 |              11.455 |      0.037 |                 56.621 |
| CI 2-D           | dGPRMNAECKM_full        | mirror    |      754 |     36.839 |       48.675 |             11.836 |      0    |        42.556 |               5.717 |      0.185 |                 33.896 |
| CI 2-D           | Rc9vIJt00vs_full        | same-side |     1070 |     21.579 |       40.89  |             19.311 |      0    |        34.338 |              12.759 |      0.074 |                 60.923 |
| CI 2-D           | Rc9vIJt00vs_full        | mirror    |     1070 |     36.244 |       41.163 |              4.918 |      0.1  |        35.06  |              -1.184 |      0.519 |                 28.327 |
| CI 2-D           | vinlwkaIW4c_full        | same-side |     1626 |     33.371 |       44.08  |             10.709 |      0    |        43.335 |               9.963 |      0     |                 37.901 |
| CI 2-D           | vinlwkaIW4c_full        | mirror    |     1626 |     39.581 |       43.644 |              4.063 |      0.01 |        42.191 |               2.61  |      0.259 |                 19.902 |
| CI 2-D           | kMkJpfUGZz8_full        | same-side |     1728 |     19.553 |       31.601 |             12.048 |      0    |        33.197 |              13.644 |      0     |                 57.658 |
| CI 2-D           | kMkJpfUGZz8_full        | mirror    |     1728 |     27.198 |       30.985 |              3.787 |      0.12 |        32.279 |               5.081 |      0.296 |                 50.298 |
| CI 2-D           | uS1JQ-LY8Fs_full        | same-side |     3868 |     12.155 |       14.48  |              2.325 |      0    |        26.538 |              14.383 |      0     |                 13.138 |
| CI 2-D           | uS1JQ-LY8Fs_full        | mirror    |     3868 |     13.859 |       14.401 |              0.542 |      0.35 |        27.093 |              13.234 |      0     |                 17.379 |
| salsa 2-D render | salsa_Pair1_song1_take1 | same-side |      214 |     13.483 |       16.629 |              3.146 |      0.18 |        18.501 |               5.018 |      0     |                 25.471 |
| salsa 2-D render | salsa_Pair1_song1_take1 | mirror    |      214 |     15.722 |       16.887 |              1.165 |      0.47 |        17.621 |               1.899 |      0.167 |                 14.608 |
| salsa 2-D render | salsa_Pair2_song2_take1 | same-side |     1003 |     18.448 |       19.754 |              1.306 |      0.17 |        19.292 |               0.844 |      0.333 |                 11.993 |
| salsa 2-D render | salsa_Pair2_song2_take1 | mirror    |     1003 |     20.597 |       19.901 |             -0.696 |      0.71 |        18.969 |              -1.629 |      1     |                -19.523 |
| salsa 2-D render | salsa_Pair5_song2_take1 | same-side |     1106 |     17.076 |       19.382 |              2.306 |      0    |        20.648 |               3.572 |      0     |                 18.932 |
| salsa 2-D render | salsa_Pair5_song2_take1 | mirror    |     1106 |     21.027 |       20.101 |             -0.926 |      0.86 |        20.176 |              -0.851 |      0.833 |                 -8.825 |

## Segment variant, CI controls (overlap removed, local 1-3 s null)

|                                               |   units |   frames_n |   excess_deg |   n_p_lt05 |
|:----------------------------------------------|--------:|-----------:|-------------:|-----------:|
| ('mirror', 'full', 'local 1-3s')              |      10 |      15873 |         0.14 |          1 |
| ('mirror', 'full', 'shift>=5s')               |      10 |      15873 |         4.46 |          5 |
| ('mirror', 'full & IoU<0.2', 'local 1-3s')    |      10 |       9625 |         1.86 |          4 |
| ('mirror', 'full & IoU<0.2', 'shift>=5s')     |      10 |       9625 |         7.33 |          7 |
| ('same-side', 'full', 'local 1-3s')           |      10 |      15873 |         5.32 |         10 |
| ('same-side', 'full', 'shift>=5s')            |      10 |      15873 |        12.52 |         10 |
| ('same-side', 'full & IoU<0.2', 'local 1-3s') |      10 |       9625 |         0.64 |          4 |
| ('same-side', 'full & IoU<0.2', 'shift>=5s')  |      10 |       9625 |         7.38 |          6 |

## By-eye check of the extremes (check_high.jpg, check_low.jpg; verdicts in examples_check.csv)

Highest 1-s similarity, 2 per duet (20): 15 are both dancers standing upright and quiet (often the start or end of the piece),
1 both kneeling apart (the only shared non-default shape), 4 overlapping bodies where the pose model merges or mixes the two skeletons.
None shows one dancer imitating an unusual shape of the other. Lowest similarity (20): 14 real complements (one standing or high,
the other lying, kneeling or on all fours), 3 pose errors in overlaps, 3 not complementary by eye.
Reading: the low end of S means "one up, one down" (it is the level contrast); the high end mostly means "both at their default
upright posture at the same time" (robust z puts each dancer's typical posture at 0), plus overlap artefacts.
