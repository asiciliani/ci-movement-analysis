# Descriptive PoC on the pair-verified CI clips

11 clips, 31.5 min with both dancers visible. Contact = nearest body segments < 0.25 body lengths (2-D: occlusion can fake contact). Levels from pelvis height above the own lowest foot.

## Per clip

| video            |   fps |   minutes_both_visible |   contact_frac |   contact_bouts_per_min |   contact_bout_median_s |   weight_share_per_min |   weight_share_median_s |   frac_standing |   frac_middle |   frac_floor |
|:-----------------|------:|-----------------------:|---------------:|------------------------:|------------------------:|-----------------------:|------------------------:|----------------:|--------------:|-------------:|
| zQRF2sLK1vY      | 29.97 |                   0.75 |           0.6  |                   19.92 |                    1.03 |                   6.64 |                    0.77 |            0.57 |          0.19 |         0.24 |
| kxztAr2tQmE_full | 15    |                   0.91 |           0.69 |                   22.09 |                    1.27 |                   2.21 |                    0.53 |            0.7  |          0.17 |         0.13 |
| swmrAJkYrlY_full | 15    |                   2.15 |           0.42 |                   13.96 |                    1.17 |                   1.86 |                    0.83 |            0.85 |          0.13 |         0.02 |
| hJQgFDsAms4_full | 15    |                   4.82 |           0.61 |                   21.8  |                    0.93 |                   3.32 |                    0.67 |            0.57 |          0.2  |         0.23 |
| iOEZ3i9rgYM_full | 15    |                   2.93 |           0.92 |                   14.32 |                    2.67 |                   3.75 |                    1.2  |            0.81 |          0.06 |         0.13 |
| dGPRMNAECKM_full | 15    |                   2.15 |           0.78 |                   21.44 |                    1.63 |                   3.73 |                    0.53 |            0.32 |          0.42 |         0.26 |
| Rc9vIJt00vs_full | 15    |                   3.69 |           0.59 |                   26.3  |                    0.87 |                   7.05 |                    0.63 |            0.58 |          0.21 |         0.21 |
| vinlwkaIW4c_full | 15    |                   3.13 |           0.61 |                   21.06 |                    1.3  |                   4.47 |                    0.93 |            0.7  |          0.17 |         0.14 |
| kMkJpfUGZz8_full | 15    |                   2.68 |           0.63 |                   16.03 |                    1.87 |                   5.22 |                    0.63 |            0.5  |          0.27 |         0.23 |
| uS1JQ-LY8Fs_full | 15    |                   5.27 |           0.43 |                   11.19 |                    1.13 |                   0    |                  nan    |            0.81 |          0.17 |         0.02 |
| YR2QCf5cL6Q_full | 15    |                   3.06 |           0.71 |                   28.12 |                    1    |                  11.45 |                    0.87 |            0.52 |          0.22 |         0.26 |


## Where they touch (pooled share of contact frames by body-region pair)

|                    |   proportion |
|:-------------------|-------------:|
| ('arm', 'torso')   |        0.122 |
| ('hand', 'torso')  |        0.115 |
| ('hand', 'hand')   |        0.115 |
| ('torso', 'torso') |        0.109 |
| ('arm', 'hand')    |        0.1   |
| ('leg', 'torso')   |        0.057 |
| ('foot', 'foot')   |        0.055 |
| ('arm', 'arm')     |        0.054 |
| ('foot', 'leg')    |        0.044 |
| ('leg', 'leg')     |        0.032 |


## Events

| kind         |   count |   mean |   std |   min |   25% |   50% |   75% |   max |
|:-------------|--------:|-------:|------:|------:|------:|------:|------:|------:|
| contact      |     609 |   1.95 |  2.4  |  0.33 |  0.6  |  1.13 |  2.33 | 33.4  |
| descent      |     174 |   0.85 |  0.88 |  0.07 |  0.27 |  0.53 |  1.18 |  3.93 |
| weight_share |     135 |   0.97 |  0.87 |  0.33 |  0.47 |  0.73 |  1.13 |  5.93 |


Descents to the floor (standing → floor within 4 s): duration, drop and peak downward pelvis speed


| in_contact   |   dur_s |   drop_bl |   peak_down_speed_bl_s |
|:-------------|--------:|----------:|-----------------------:|
| False        |    0.47 |      0.94 |                   3.08 |
| True         |    0.67 |      0.76 |                   2.71 |


## Movement vocabulary (k-means on 1 s pose windows)

|   word |   trunk_tilt |   inverted |   knee_L |   knee_R |   hip_L |   hip_R |   elbow_L |   elbow_R |   arm_up_L |   arm_up_R |   level |   stance_width |   contact |   dist_bl |   rel_level |   motion |    n |
|-------:|-------------:|-----------:|---------:|---------:|--------:|--------:|----------:|----------:|-----------:|-----------:|--------:|---------------:|----------:|----------:|------------:|---------:|-----:|
|      0 |        19.94 |      -1.12 |   160.18 |   159.25 |  145.49 |  146.9  |    145.57 |    144.42 |      -0.82 |      -0.78 |    1.63 |           1.12 |         1 |      0.03 |        0.12 |     1.6  |  853 |
|      1 |        10.2  |      -1.16 |   165.72 |   163    |  162.06 |  161.59 |    144.29 |    145.62 |      -0.16 |       0.04 |    1.54 |           0.48 |         1 |      0.03 |        0.02 |     0.72 |  830 |
|      2 |         5.81 |      -1.32 |   171.21 |   169.94 |  168.36 |  168.21 |    159.07 |    156.3  |      -0.9  |      -0.88 |    1.61 |           0.42 |         1 |      0.03 |        0.02 |     0.58 | 1681 |
|      3 |        85.44 |      -0.16 |   147.76 |   146.02 |  141.2  |  134.84 |    125.56 |    129.81 |      -0.2  |       0.01 |    0.14 |           0.19 |         0 |      0.05 |       -0.31 |     1.23 |  502 |
|      4 |         4.15 |      -1.44 |   172.49 |   172.15 |  170.1  |  170.4  |    160.2  |    161.17 |      -0.93 |      -0.95 |    1.64 |           0.5  |         0 |      0.47 |        0.04 |     0.52 | 1234 |
|      5 |         3.93 |      -1.21 |   170.22 |   170.01 |  170.1  |  169.62 |    156.4  |    160.11 |      -0.61 |      -0.73 |    1.32 |           0.5  |         0 |      2.67 |        0.01 |     0.68 |  737 |
|      6 |        13.59 |      -1.15 |    60.43 |    61.49 |   62.38 |   59.45 |    133.77 |    134.35 |      -0.46 |      -0.46 |    0.35 |           0.51 |         0 |      0.07 |       -0.36 |     0.71 |  598 |
|      7 |        92.82 |       0.29 |   145.66 |   143.52 |   82.77 |   82.14 |    151.96 |    150.01 |      -0.96 |      -0.95 |    1.28 |           0.62 |         0 |      0.03 |        0.12 |     1.16 |  681 |
|      8 |         5.73 |      -1.3  |   169.24 |   168.48 |  168.05 |  167.2  |     81.5  |     80.05 |      -0.29 |      -0.28 |    1.61 |           0.5  |         1 |      0.03 |        0.05 |     0.58 |  946 |
|      9 |        36.31 |      -0.74 |    79.42 |    85.1  |  110.54 |  110.29 |    159.15 |    152.67 |      -0.99 |      -0.93 |    0.66 |           0.45 |         1 |      0.08 |        0    |     0.76 |  704 |


Signature check (split-half): 3/11 clips' first half is closest to their own second half (chance 0.09). Camera angle also differs between clips, so this mixes dancer style and viewpoint.


## Validation sheets
check_weight_share.jpg, check_contact_regions.jpg, check_word_*.jpg — every detector must be eyeballed before use.