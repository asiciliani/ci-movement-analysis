# Descriptive PoC on the pair-verified CI clips

10 clips, 20.7 min with both dancers visible. Contact = nearest body segments < 0.25 body lengths (2-D: occlusion can fake contact). Levels from pelvis height above the own lowest foot.

## Per clip

| video            |   fps |   minutes_both_visible |   contact_frac |   contact_bouts_per_min |   contact_bout_median_s |   weight_share_per_min |   weight_share_median_s |   frac_standing |   frac_middle |   frac_floor |
|:-----------------|------:|-----------------------:|---------------:|------------------------:|------------------------:|-----------------------:|------------------------:|----------------:|--------------:|-------------:|
| zQRF2sLK1vY      | 29.97 |                   0.61 |           0.62 |                   24.66 |                    0.77 |                   3.29 |                    0.58 |            0.52 |          0.28 |         0.2  |
| kxztAr2tQmE_full | 15    |                   0.6  |           0.63 |                   36.73 |                    0.53 |                   3.34 |                    0.47 |            0.75 |          0.16 |         0.1  |
| swmrAJkYrlY_full | 15    |                   2.29 |           0.45 |                   18.78 |                    0.93 |                   0.44 |                    0.87 |            0.86 |          0.13 |         0.01 |
| hJQgFDsAms4_full | 15    |                   2.52 |           0.61 |                   32.19 |                    0.73 |                   1.19 |                    0.6  |            0.58 |          0.21 |         0.2  |
| iOEZ3i9rgYM_full | 15    |                   2.34 |           0.87 |                   21.37 |                    1.5  |                   2.56 |                    0.47 |            0.82 |          0.08 |         0.11 |
| dGPRMNAECKM_full | 15    |                   1.35 |           0.73 |                   37.9  |                    0.87 |                   4.46 |                    0.33 |            0.45 |          0.33 |         0.22 |
| Rc9vIJt00vs_full | 15    |                   1.79 |           0.63 |                   33.5  |                    0.87 |                   6.14 |                    0.53 |            0.61 |          0.22 |         0.17 |
| vinlwkaIW4c_full | 15    |                   1.93 |           0.5  |                   28.98 |                    0.67 |                   3.11 |                    0.5  |            0.71 |          0.19 |         0.11 |
| kMkJpfUGZz8_full | 15    |                   2.23 |           0.59 |                   19.29 |                    1.33 |                   1.79 |                    0.57 |            0.51 |          0.26 |         0.24 |
| uS1JQ-LY8Fs_full | 15    |                   5.03 |           0.33 |                   14.51 |                    0.93 |                   0.2  |                    0.33 |            0.77 |          0.17 |         0.06 |


## Where they touch (pooled share of contact frames by body-region pair)

|                    |   proportion |
|:-------------------|-------------:|
| ('arm', 'hand')    |        0.15  |
| ('arm', 'torso')   |        0.139 |
| ('hand', 'hand')   |        0.129 |
| ('hand', 'torso')  |        0.116 |
| ('torso', 'torso') |        0.096 |
| ('arm', 'arm')     |        0.078 |
| ('foot', 'foot')   |        0.063 |
| ('leg', 'torso')   |        0.035 |
| ('head', 'head')   |        0.033 |
| ('foot', 'leg')    |        0.029 |


## Events

| kind         |   count |   mean |   std |   min |   25% |   50% |   75% |   max |
|:-------------|--------:|-------:|------:|------:|------:|------:|------:|------:|
| contact      |     494 |   1.37 |  1.59 |  0.3  |  0.47 |  0.87 |  1.59 | 14.4  |
| descent      |     127 |   1.01 |  0.95 |  0.07 |  0.27 |  0.67 |  1.43 |  3.93 |
| weight_share |      42 |   0.6  |  0.36 |  0.33 |  0.33 |  0.5  |  0.67 |  2.33 |


Descents to the floor (standing → floor within 4 s): duration, drop and peak downward pelvis speed


| in_contact   |   dur_s |   drop_bl |   peak_down_speed_bl_s |
|:-------------|--------:|----------:|-----------------------:|
| False        |    0.87 |       1   |                   3.77 |
| True         |    0.32 |       0.7 |                   3.68 |


## Movement vocabulary (k-means on 1 s pose windows)

|   word |   trunk_tilt |   inverted |   knee_L |   knee_R |   hip_L |   hip_R |   elbow_L |   elbow_R |   arm_up_L |   arm_up_R |   level |   stance_width |   contact |   dist_bl |   rel_level |   motion |    n |
|-------:|-------------:|-----------:|---------:|---------:|--------:|--------:|----------:|----------:|-----------:|-----------:|--------:|---------------:|----------:|----------:|------------:|---------:|-----:|
|      0 |        14.63 |      -1.2  |    64.6  |    68.47 |   66.26 |   66.45 |    139.1  |    146.26 |      -0.65 |      -0.61 |    0.43 |           0.55 |         0 |      0.16 |       -0.19 |     0.96 |  296 |
|      1 |         4.46 |      -1.33 |   171.61 |   172.68 |  170.5  |  170.5  |    155.34 |    156.5  |      -0.89 |      -0.87 |    1.58 |           0.37 |         1 |      0.03 |        0    |     0.58 | 1207 |
|      2 |         3.45 |      -1.16 |   171.35 |   171.84 |  171.07 |  171.12 |    151.15 |    158.67 |      -0.62 |      -0.71 |    1.27 |           0.38 |         0 |      2.58 |       -0.03 |     0.62 |  652 |
|      3 |        86.03 |       0.18 |   146.1  |   146.24 |   83.67 |   85.62 |    154.62 |    149.51 |      -1.1  |      -1.01 |    1.35 |           0.61 |         0 |      0.02 |        0    |     1.03 |  283 |
|      4 |         9.38 |      -1.16 |   165.23 |   165.69 |  162.51 |  163.16 |    134.79 |    133.96 |      -0.28 |      -0.18 |    1.51 |           0.46 |         1 |      0.03 |        0.05 |     0.84 |  542 |
|      5 |         3.83 |      -1.43 |   172.68 |   173.6  |  170.53 |  170.42 |    154.9  |    156.11 |      -0.91 |      -0.92 |    1.63 |           0.48 |         0 |      0.38 |        0.06 |     0.53 | 1101 |
|      6 |        70.44 |      -0.34 |   141.72 |   141.94 |  132.21 |  134.24 |    132    |    131.34 |      -0.24 |      -0.16 |    0.23 |           0.14 |         0 |      0.03 |       -0.28 |     1.45 |  295 |
|      7 |         4.91 |      -1.33 |   169.65 |   170.69 |  169.91 |  170.45 |     78.93 |     81.5  |      -0.27 |      -0.28 |    1.62 |           0.44 |         1 |      0.04 |        0.03 |     0.63 |  497 |
|      8 |        21.5  |      -1.03 |   161.35 |   161.65 |  145.94 |  147.83 |    149.35 |    151.58 |      -0.74 |      -0.79 |    1.55 |           1.16 |         0 |      0.03 |        0.11 |     1.42 |  507 |
|      9 |        24.1  |      -0.93 |   116.42 |   115.01 |  116.22 |  119.87 |    148.91 |    147.99 |      -0.81 |      -0.81 |    0.75 |           0.48 |         1 |      0.04 |        0.01 |     0.94 |  438 |


Signature check (split-half): 3/10 clips' first half is closest to their own second half (chance 0.10). Camera angle also differs between clips, so this mixes dancer style and viewpoint.


## Validation sheets
check_weight_share.jpg, check_contact_regions.jpg, check_word_*.jpg — every detector must be eyeballed before use.