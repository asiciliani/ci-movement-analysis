# Mirror vs complement: frame-wise posture similarity between partners

Method in the docstring of mirroring.py. S = - mean |zA - zB| over robust-z posture descriptors (0 = identical; about -1.1 for independent standard normals). Excess = S minus the null mean (> 0: more similar than the null).

## Summary (medians over duets / sequences)

|                                            |   units |      S |   excess_shift |   n_p_shift_lt05 |   excess_pseudo |   n_p_pseudo_lt05 |
|:-------------------------------------------|--------:|-------:|---------------:|-----------------:|----------------:|------------------:|
| ('CI 2-D', 'all', 'all')                   |      11 | -0.91  |          0.225 |               11 |           0.239 |                10 |
| ('CI 2-D', 'all', 'apart')                 |       9 | -0.887 |          0.209 |                7 |           0.171 |                 3 |
| ('CI 2-D', 'all', 'contact')               |      11 | -0.915 |          0.236 |               11 |           0.242 |                 9 |
| ('CI 2-D', 'common7', 'all')               |      11 | -0.911 |          0.24  |               11 |           0.249 |                 9 |
| ('CI 2-D', 'common7', 'apart')             |       9 | -0.842 |          0.284 |                5 |           0.281 |                 5 |
| ('CI 2-D', 'common7', 'contact')           |      11 | -0.95  |          0.251 |               10 |           0.262 |                 8 |
| ('CI 2-D', 'shape', 'all')                 |      11 | -0.937 |          0.218 |               11 |           0.204 |                 8 |
| ('CI 2-D', 'shape', 'apart')               |       9 | -0.951 |          0.15  |                5 |           0.138 |                 2 |
| ('CI 2-D', 'shape', 'contact')             |      11 | -0.949 |          0.216 |               11 |           0.194 |                 8 |
| ('salsa 2-D render', 'all', 'all')         |       3 | -1.113 |          0.038 |                1 |           0.059 |                 2 |
| ('salsa 2-D render', 'all', 'contact')     |       3 | -1.111 |          0.035 |                1 |           0.044 |                 2 |
| ('salsa 2-D render', 'common7', 'all')     |       3 | -1.12  |          0.093 |                1 |           0.109 |                 2 |
| ('salsa 2-D render', 'common7', 'contact') |       3 | -1.113 |          0.094 |                1 |           0.082 |                 2 |
| ('salsa 2-D render', 'shape', 'all')       |       3 | -1.105 |          0.039 |                1 |           0.057 |                 1 |
| ('salsa 2-D render', 'shape', 'contact')   |       3 | -1.102 |          0.042 |                2 |           0.063 |                 2 |
| ('salsa 3-D mocap', 'all', 'all')          |      71 | -0.91  |          0.243 |               71 |           0.238 |                71 |
| ('salsa 3-D mocap', 'common7', 'all')      |      71 | -0.91  |          0.243 |               71 |           0.238 |                71 |

## CI per duet (all descriptors, all frames)

| unit             |   n_frames |      S |   excess_shift |   z_shift |   p_shift |   excess_pseudo |   p_pseudo |
|:-----------------|-----------:|-------:|---------------:|----------:|----------:|----------------:|-----------:|
| zQRF2sLK1vY      |       1343 | -0.994 |          0.181 |     2.866 |         0 |           0.102 |       0.04 |
| kxztAr2tQmE_full |        815 | -0.906 |          0.314 |     4.941 |         0 |           0.265 |       0.02 |
| swmrAJkYrlY_full |       1910 | -0.987 |          0.195 |     3.975 |         0 |           0.16  |       0    |
| hJQgFDsAms4_full |       4142 | -0.87  |          0.225 |     5.944 |         0 |           0.239 |       0    |
| iOEZ3i9rgYM_full |       2629 | -0.93  |          0.344 |     6.2   |         0 |           0.26  |       0    |
| dGPRMNAECKM_full |       1548 | -0.797 |          0.266 |     5.007 |         0 |           0.321 |       0    |
| Rc9vIJt00vs_full |       3181 | -0.882 |          0.284 |     8.062 |         0 |           0.263 |       0    |
| vinlwkaIW4c_full |       2812 | -0.92  |          0.219 |     7.322 |         0 |           0.225 |       0    |
| kMkJpfUGZz8_full |       2381 | -0.801 |          0.377 |     5.398 |         0 |           0.358 |       0    |
| uS1JQ-LY8Fs_full |       4648 | -1.107 |          0.1   |     3.918 |         0 |           0.026 |       0.32 |
| YR2QCf5cL6Q_full |       2712 | -0.91  |          0.176 |     4.017 |         0 |           0.189 |       0    |

## Per descriptor: lag-0 Spearman between partners vs shift null (+ mirror / - complement; counts of units with |z| > 2)

|                                    |   r_median |   null_median |   z_median |   n_pos |   n_neg |   n |
|:-----------------------------------|-----------:|--------------:|-----------:|--------:|--------:|----:|
| ('CI 2-D', 'armup_max')            |       0.14 |          0    |       1.8  |       5 |       0 |  11 |
| ('CI 2-D', 'armup_min')            |       0.19 |         -0    |       1.85 |       5 |       0 |  11 |
| ('CI 2-D', 'elbow_max')            |       0.09 |         -0    |       1.59 |       3 |       0 |  11 |
| ('CI 2-D', 'elbow_min')            |       0.14 |         -0    |       2.42 |       7 |       0 |  11 |
| ('CI 2-D', 'hip_max')              |       0.33 |         -0.01 |       3    |      11 |       0 |  11 |
| ('CI 2-D', 'hip_min')              |       0.4  |         -0.01 |       3.33 |       9 |       0 |  11 |
| ('CI 2-D', 'inverted')             |       0.47 |         -0.02 |       3.24 |      10 |       0 |  11 |
| ('CI 2-D', 'knee_max')             |       0.24 |         -0.01 |       2.31 |       8 |       0 |  11 |
| ('CI 2-D', 'knee_min')             |       0.33 |         -0.02 |       2.38 |      11 |       0 |  11 |
| ('CI 2-D', 'level')                |       0.38 |         -0.02 |       2.88 |      10 |       0 |  11 |
| ('CI 2-D', 'openness')             |       0.24 |         -0.01 |       2.9  |       8 |       0 |  11 |
| ('CI 2-D', 'stance')               |       0.13 |         -0    |       1.68 |       3 |       0 |  11 |
| ('CI 2-D', 'trunk_tilt')           |       0.4  |         -0.02 |       3.15 |      10 |       0 |  11 |
| ('salsa 2-D render', 'armup_max')  |       0.27 |          0    |       1.57 |       1 |       0 |   3 |
| ('salsa 2-D render', 'armup_min')  |       0.14 |         -0.01 |       1.32 |       1 |       0 |   3 |
| ('salsa 2-D render', 'elbow_max')  |       0.13 |          0    |       1.53 |       0 |       0 |   3 |
| ('salsa 2-D render', 'elbow_min')  |      -0.13 |          0    |      -1.1  |       0 |       1 |   3 |
| ('salsa 2-D render', 'hip_max')    |       0.01 |         -0    |       0.38 |       0 |       0 |   3 |
| ('salsa 2-D render', 'hip_min')    |       0    |          0.01 |      -0.05 |       0 |       0 |   3 |
| ('salsa 2-D render', 'inverted')   |       0.04 |         -0.01 |       0.46 |       1 |       0 |   3 |
| ('salsa 2-D render', 'knee_max')   |       0.02 |          0    |       0.17 |       0 |       0 |   3 |
| ('salsa 2-D render', 'knee_min')   |      -0.03 |          0    |      -0.48 |       0 |       0 |   3 |
| ('salsa 2-D render', 'level')      |      -0.02 |          0    |      -0.35 |       0 |       1 |   3 |
| ('salsa 2-D render', 'openness')   |       0.03 |          0    |       0.44 |       1 |       0 |   3 |
| ('salsa 2-D render', 'stance')     |       0.02 |          0.01 |       0.18 |       0 |       0 |   3 |
| ('salsa 2-D render', 'trunk_tilt') |      -0.07 |          0.01 |      -0.76 |       0 |       0 |   3 |
| ('salsa 3-D mocap', 'armup_max')   |       0.72 |         -0.01 |       9.78 |      71 |       0 |  71 |
| ('salsa 3-D mocap', 'armup_min')   |       0.47 |         -0.01 |       6.86 |      70 |       0 |  71 |
| ('salsa 3-D mocap', 'inverted')    |       0.13 |         -0    |       1.76 |      33 |       0 |  71 |
| ('salsa 3-D mocap', 'level')       |       0.3  |         -0    |       4.56 |      67 |       0 |  71 |
| ('salsa 3-D mocap', 'openness')    |       0.29 |         -0.01 |       3.74 |      56 |       1 |  71 |
| ('salsa 3-D mocap', 'stance')      |       0.18 |         -0    |       3.14 |      53 |       0 |  71 |
| ('salsa 3-D mocap', 'trunk_tilt')  |       0.14 |         -0    |       2.42 |      43 |       0 |  71 |

## 2-D measure vs 3-D truth on the salsa renders (1 s smoothed S(t), 7 common descriptors)

| seq               |   n |   r_2d_3d |   null_mean |     p |
|:------------------|----:|----------:|------------:|------:|
| Pair1_song1_take1 | 447 |     0.215 |      -0.007 | 0.155 |
| Pair2_song2_take1 | 824 |     0.166 |       0.003 | 0.12  |
| Pair5_song2_take1 | 880 |     0.142 |      -0.001 | 0.145 |
## Controls (CI: overlap, apart, state; local 1-3 s null; salsa 3-D for comparison)

|                                                               |   units |   frames_n |   excess_median |   n_p_lt05 |
|:--------------------------------------------------------------|--------:|-----------:|----------------:|-----------:|
| ('CI 2-D', 'all', 'all', 'local 1-3s')                        |      11 |      28121 |           0.064 |          9 |
| ('CI 2-D', 'all', 'all', 'shift>=5s')                         |      11 |      28121 |           0.23  |         11 |
| ('CI 2-D', 'all', 'apart(>1bl)', 'local 1-3s')                |       9 |       4570 |           0.063 |          4 |
| ('CI 2-D', 'all', 'apart(>1bl)', 'shift>=5s')                 |       9 |       4570 |           0.205 |          6 |
| ('CI 2-D', 'all', 'boxes_IoU<0.2', 'local 1-3s')              |      11 |      16232 |           0.061 |          7 |
| ('CI 2-D', 'all', 'boxes_IoU<0.2', 'shift>=5s')               |      11 |      16232 |           0.206 |         11 |
| ('CI 2-D', 'all', 'floor_state', 'local 1-3s')                |      10 |       5193 |           0.043 |          3 |
| ('CI 2-D', 'all', 'floor_state', 'shift>=5s')                 |      10 |       5193 |           0.128 |          6 |
| ('CI 2-D', 'all', 'not_floor_or_share_state', 'local 1-3s')   |      11 |      20630 |           0.095 |         10 |
| ('CI 2-D', 'all', 'not_floor_or_share_state', 'shift>=5s')    |      11 |      20630 |           0.294 |         11 |
| ('CI 2-D', 'shape', 'all', 'local 1-3s')                      |      11 |      28122 |           0.06  |          9 |
| ('CI 2-D', 'shape', 'all', 'shift>=5s')                       |      11 |      28122 |           0.217 |         11 |
| ('CI 2-D', 'shape', 'apart(>1bl)', 'local 1-3s')              |       9 |       4571 |           0.061 |          3 |
| ('CI 2-D', 'shape', 'apart(>1bl)', 'shift>=5s')               |       9 |       4571 |           0.157 |          5 |
| ('CI 2-D', 'shape', 'boxes_IoU<0.2', 'local 1-3s')            |      11 |      16233 |           0.048 |          8 |
| ('CI 2-D', 'shape', 'boxes_IoU<0.2', 'shift>=5s')             |      11 |      16233 |           0.176 |          9 |
| ('CI 2-D', 'shape', 'floor_state', 'local 1-3s')              |      10 |       5193 |           0.033 |          3 |
| ('CI 2-D', 'shape', 'floor_state', 'shift>=5s')               |      10 |       5193 |           0.107 |          6 |
| ('CI 2-D', 'shape', 'not_floor_or_share_state', 'local 1-3s') |      11 |      20631 |           0.078 |         10 |
| ('CI 2-D', 'shape', 'not_floor_or_share_state', 'shift>=5s')  |      11 |      20631 |           0.243 |         11 |
| ('salsa 3-D mocap', 'common7', 'all', 'local 1-3s')           |      71 |     159862 |           0.191 |         71 |
| ('salsa 3-D mocap', 'common7', 'all', 'shift>=5s')            |      71 |     159862 |           0.242 |         71 |

## Variant (v2, face keypoints not required): segment directions in each torso frame (+-2 frame best match, 10 deg tolerance, core weighted; only frames with both bodies fully in shot)

Distances in degrees (lower = more similar); excess = null - observed (> 0: more similar than the null). Mirror = B reflected left/right. In 2-D a same-side movement of two dancers facing each other looks mirrored in the image and vice versa: mirror vs same-side cannot be read as imitation style without the facing direction.

|                                   |   units |   full_frames |   mean_deg |   excess_shift_deg |   n_p_shift_lt05 |   excess_pseudo_deg |   n_p_pseudo_lt05 |   calibrated_pct |
|:----------------------------------|--------:|--------------:|-----------:|-------------------:|-----------------:|--------------------:|------------------:|-----------------:|
| ('CI 2-D', 'mirror')              |      11 |         15505 |      42.67 |               3.78 |                4 |                3.79 |                 1 |            21.67 |
| ('CI 2-D', 'same-side')           |      11 |         15505 |      38.04 |               8.63 |               10 |                8.97 |                 4 |            29.15 |
| ('salsa 2-D render', 'mirror')    |       3 |          1929 |      21.23 |               0.98 |                0 |                1.32 |                 1 |             9.88 |
| ('salsa 2-D render', 'same-side') |       3 |          1929 |      21.05 |               1.41 |                0 |                2.11 |                 2 |            12.95 |

Per unit:

| genre            | unit                    | mode      |   n_full |   mean_deg |   shift_mean |   excess_shift_deg |   p_shift |   pseudo_mean |   excess_pseudo_deg |   p_pseudo |   calibrated_score_pct |
|:-----------------|:------------------------|:----------|---------:|-----------:|-------------:|-------------------:|----------:|--------------:|--------------------:|-----------:|-----------------------:|
| CI 2-D           | zQRF2sLK1vY             | same-side |      877 |     38.035 |       47.762 |              9.727 |     0     |        47.005 |               8.97  |      0.067 |                 35.854 |
| CI 2-D           | zQRF2sLK1vY             | mirror    |      877 |     44.263 |       47.188 |              2.926 |     0.11  |        47.156 |               2.893 |      0.233 |                 10.798 |
| CI 2-D           | kxztAr2tQmE_full        | same-side |      485 |     31.597 |       42.433 |             10.836 |     0     |        45.642 |              14.045 |      0.033 |                 23.602 |
| CI 2-D           | kxztAr2tQmE_full        | mirror    |      485 |     41.592 |       43.363 |              1.772 |     0.33  |        45.381 |               3.789 |      0.3   |                 24.884 |
| CI 2-D           | swmrAJkYrlY_full        | same-side |      887 |     21.995 |       30.171 |              8.175 |     0     |        38.699 |              16.704 |      0.033 |                 29.152 |
| CI 2-D           | swmrAJkYrlY_full        | mirror    |      887 |     26.881 |       30.664 |              3.783 |     0.11  |        37.795 |              10.915 |      0.1   |                 27.527 |
| CI 2-D           | hJQgFDsAms4_full        | same-side |     2279 |     41.225 |       51.641 |             10.417 |     0     |        51.168 |               9.944 |      0.1   |                 34.246 |
| CI 2-D           | hJQgFDsAms4_full        | mirror    |     2279 |     42.671 |       50.57  |              7.899 |     0.02  |        50.235 |               7.564 |      0.133 |                 27.805 |
| CI 2-D           | iOEZ3i9rgYM_full        | same-side |     1478 |     36.674 |       42.788 |              6.114 |     0.01  |        40.553 |               3.878 |      0.433 |                 36.825 |
| CI 2-D           | iOEZ3i9rgYM_full        | mirror    |     1478 |     40.957 |       42.956 |              1.998 |     0.23  |        39.466 |              -1.491 |      0.533 |                 14.488 |
| CI 2-D           | dGPRMNAECKM_full        | same-side |      697 |     45.175 |       53.801 |              8.626 |     0     |        47.11  |               1.935 |      0.267 |                 26.999 |
| CI 2-D           | dGPRMNAECKM_full        | mirror    |      697 |     45.405 |       54.221 |              8.816 |     0.02  |        46.221 |               0.816 |      0.467 |                 35.603 |
| CI 2-D           | Rc9vIJt00vs_full        | same-side |     1549 |     38.44  |       49.488 |             11.048 |     0     |        45.542 |               7.102 |      0.167 |                 34.477 |
| CI 2-D           | Rc9vIJt00vs_full        | mirror    |     1549 |     43.762 |       49.132 |              5.37  |     0.02  |        45.732 |               1.97  |      0.367 |                 20.586 |
| CI 2-D           | vinlwkaIW4c_full        | same-side |     2051 |     46.328 |       53.109 |              6.78  |     0     |        49.938 |               3.609 |      0.233 |                 17.786 |
| CI 2-D           | vinlwkaIW4c_full        | mirror    |     2051 |     45.82  |       53.111 |              7.292 |     0     |        49.854 |               4.034 |      0.2   |                 20.24  |
| CI 2-D           | kMkJpfUGZz8_full        | same-side |     1213 |     26.727 |       41.075 |             14.348 |     0     |        42.398 |              15.671 |      0     |                 42.005 |
| CI 2-D           | kMkJpfUGZz8_full        | mirror    |     1213 |     37.002 |       40.377 |              3.375 |     0.22  |        42.556 |               5.554 |      0.2   |                 29.069 |
| CI 2-D           | uS1JQ-LY8Fs_full        | same-side |     2519 |     13.412 |       16.395 |              2.983 |     0.01  |        34.081 |              20.669 |      0     |                 20.871 |
| CI 2-D           | uS1JQ-LY8Fs_full        | mirror    |     2519 |     14.839 |       16.281 |              1.442 |     0.19  |        32.241 |              17.402 |      0     |                 21.669 |
| CI 2-D           | YR2QCf5cL6Q_full        | same-side |     1470 |     46.558 |       52.191 |              5.633 |     0.05  |        51.781 |               5.223 |      0.2   |                 18.808 |
| CI 2-D           | YR2QCf5cL6Q_full        | mirror    |     1470 |     48.105 |       52.58  |              4.475 |     0.1   |        49.201 |               1.096 |      0.433 |                 16.043 |
| salsa 2-D render | salsa_Pair1_song1_take1 | same-side |      159 |     17.476 |       23.848 |              6.372 |     0.202 |        22.182 |               4.706 |      0     |                 42.382 |
| salsa 2-D render | salsa_Pair1_song1_take1 | mirror    |      159 |     20.073 |       22.421 |              2.347 |     0.333 |        21.394 |               1.321 |      0.333 |                 40.152 |
| salsa 2-D render | salsa_Pair2_song2_take1 | same-side |      902 |     21.43  |       22.015 |              0.585 |     0.26  |        22.803 |               1.373 |      0.167 |                 12.954 |
| salsa 2-D render | salsa_Pair2_song2_take1 | mirror    |      902 |     21.233 |       22.126 |              0.893 |     0.17  |        25.32  |               4.088 |      0     |                 -0.912 |
| salsa 2-D render | salsa_Pair5_song2_take1 | same-side |      868 |     21.046 |       22.456 |              1.41  |     0.08  |        23.153 |               2.107 |      0     |                  7.769 |
| salsa 2-D render | salsa_Pair5_song2_take1 | mirror    |      868 |     21.962 |       22.94  |              0.978 |     0.16  |        22.418 |               0.456 |      0.667 |                  9.881 |

## Segment variant, CI controls (overlap removed, local 1-3 s null)

|                                               |   units |   frames_n |   excess_deg |   n_p_lt05 |
|:----------------------------------------------|--------:|-----------:|-------------:|-----------:|
| ('mirror', 'full', 'local 1-3s')              |      11 |      15505 |         0.03 |          3 |
| ('mirror', 'full', 'shift>=5s')               |      11 |      15505 |         3.86 |          3 |
| ('mirror', 'full & IoU<0.2', 'local 1-3s')    |      11 |       9036 |         1.66 |          5 |
| ('mirror', 'full & IoU<0.2', 'shift>=5s')     |      11 |       9036 |         8.64 |          5 |
| ('same-side', 'full', 'local 1-3s')           |      11 |      15505 |         5.22 |          9 |
| ('same-side', 'full', 'shift>=5s')            |      11 |      15505 |         9.06 |         10 |
| ('same-side', 'full & IoU<0.2', 'local 1-3s') |      11 |       9036 |         1.31 |          2 |
| ('same-side', 'full & IoU<0.2', 'shift>=5s')  |      11 |       9036 |         5.63 |          5 |
