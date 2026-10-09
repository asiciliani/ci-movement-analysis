# Descriptive PoC on the pair-verified CI clips

8 clips, 6.6 min with both dancers visible. Contact = nearest body segments < 0.25 body lengths (2-D: occlusion can fake contact). Levels from pelvis height above the own lowest foot.

## Per clip

| video       |   fps |   minutes_both_visible |   contact_frac |   contact_bouts_per_min |   contact_bout_median_s |   weight_share_per_min |   weight_share_median_s |   frac_standing |   frac_middle |   frac_floor |
|:------------|------:|-----------------------:|---------------:|------------------------:|------------------------:|-----------------------:|------------------------:|----------------:|--------------:|-------------:|
| dGPRMNAECKM | 29.97 |                   0.53 |           0.63 |                   34.22 |                    1.02 |                   3.8  |                    0.35 |            0.77 |          0.12 |         0.1  |
| hJQgFDsAms4 | 29.97 |                   0.51 |           0.61 |                   25.44 |                    0.7  |                   0    |                  nan    |            0.57 |          0.14 |         0.29 |
| iOEZ3i9rgYM | 29.97 |                   0.57 |           0.88 |                   33.07 |                    1.5  |                   3.48 |                    0.47 |            0.98 |          0.02 |         0    |
| kxztAr2tQmE | 29.97 |                   0.51 |           0.63 |                   33.12 |                    0.7  |                   5.84 |                    0.33 |            0.7  |          0.19 |         0.11 |
| swmrAJkYrlY | 29.92 |                   2.27 |           0.46 |                   21.58 |                    0.74 |                   0.88 |                    0.7  |            0.87 |          0.13 |         0.01 |
| zQRF2sLK1vY | 29.97 |                   0.61 |           0.6  |                   24.66 |                    0.73 |                   3.29 |                    0.58 |            0.52 |          0.28 |         0.2  |
| Rc9vIJt00vs | 59.94 |                   0.67 |           0.63 |                   45.96 |                    0.75 |                   7.41 |                    0.42 |            0.68 |          0.19 |         0.13 |
| vinlwkaIW4c | 24    |                   0.95 |           0.52 |                   29.47 |                    0.92 |                   3.16 |                    0.46 |            0.69 |          0.2  |         0.11 |


## Where they touch (pooled share of contact frames by body-region pair)

|                    |   proportion |
|:-------------------|-------------:|
| ('hand', 'hand')   |        0.149 |
| ('arm', 'hand')    |        0.137 |
| ('arm', 'torso')   |        0.124 |
| ('hand', 'torso')  |        0.122 |
| ('torso', 'torso') |        0.085 |
| ('foot', 'foot')   |        0.076 |
| ('arm', 'arm')     |        0.064 |
| ('leg', 'torso')   |        0.044 |
| ('foot', 'leg')    |        0.032 |
| ('leg', 'leg')     |        0.028 |


## Events

| kind         |   count |   mean |   std |   min |   25% |   50% |   75% |   max |
|:-------------|--------:|-------:|------:|------:|------:|------:|------:|------:|
| contact      |     190 |   1.23 |  1.13 |  0.3  |  0.5  |  0.8  |  1.57 |  7.01 |
| descent      |      51 |   0.82 |  0.79 |  0.05 |  0.28 |  0.5  |  1.01 |  3.4  |
| weight_share |      19 |   0.46 |  0.17 |  0.3  |  0.35 |  0.42 |  0.51 |  1.04 |


Descents to the floor (standing → floor within 4 s): duration, drop and peak downward pelvis speed


| in_contact   |   dur_s |   drop_bl |   peak_down_speed_bl_s |
|:-------------|--------:|----------:|-----------------------:|
| False        |    0.57 |      0.84 |                   5.06 |
| True         |    0.47 |      0.67 |                   3.97 |


## Movement vocabulary (k-means on 1 s pose windows)

|   word |   trunk_tilt |   inverted |   knee_L |   knee_R |   hip_L |   hip_R |   elbow_L |   elbow_R |   arm_up_L |   arm_up_R |   level |   stance_width |   contact |   dist_bl |   rel_level |   motion |   n |
|-------:|-------------:|-----------:|---------:|---------:|--------:|--------:|----------:|----------:|-----------:|-----------:|--------:|---------------:|----------:|----------:|------------:|---------:|----:|
|      0 |         5.82 |      -1.25 |   170.52 |   170.45 |  169.81 |  168.11 |    149.29 |    157.72 |      -0.81 |      -0.78 |    1.56 |           0.38 |         1 |      0.03 |        0.01 |     0.91 | 414 |
|      1 |        28.77 |      -0.91 |    80.25 |    81.91 |   84    |   87.17 |    149.11 |    143.58 |      -0.86 |      -0.81 |    0.62 |           0.48 |         0 |      0.32 |       -0.01 |     1.37 | 101 |
|      2 |         3.26 |      -1.24 |   167.3  |   167.33 |  170.51 |  171.5  |    144.33 |    151.59 |      -0.71 |      -0.75 |    1.31 |           0.43 |         0 |      3.58 |       -0.02 |     0.92 | 176 |
|      3 |        68.06 |      -0.1  |   141.69 |   147.17 |   94.9  |  104.65 |    157.1  |    149.9  |      -0.94 |      -0.92 |    1.42 |           0.65 |         0 |      0.02 |        0.25 |     1.81 | 110 |
|      4 |         4.45 |      -1.35 |   164.74 |   168.01 |  170.94 |  170.6  |     78.97 |     79.73 |      -0.29 |      -0.28 |    1.6  |           0.46 |         1 |      0.07 |        0.03 |     1.06 | 188 |
|      5 |        79.2  |      -0.18 |   135.58 |   137.62 |  141.1  |  146.76 |    124.72 |    136.15 |      -0.31 |      -0.14 |    0.21 |           0.14 |         0 |      0.04 |       -0.03 |     1.89 |  74 |
|      6 |         6.83 |      -1.29 |   168.41 |   170.1  |  166.5  |  167.67 |    148.6  |    154.58 |      -0.8  |      -0.82 |    1.55 |           0.41 |         0 |      0.29 |        0.03 |     1.03 | 280 |
|      7 |        63.91 |      -0.41 |   114.14 |   132.44 |   66.89 |   81.28 |    158.4  |    157.18 |      -3.32 |      -2.73 |    2.82 |           0.92 |         1 |      0.04 |        0.51 |     5.9  |  11 |
|      8 |         6.64 |      -2.01 |   172.07 |   171.27 |  170.64 |  169.38 |    156.88 |    155.7  |      -1.51 |      -1.46 |    2.36 |           0.6  |         1 |      0.02 |        0.21 |     1    | 115 |
|      9 |        22.77 |      -1.06 |   158.92 |   161.1  |  138.86 |  149.97 |    145.68 |    146.6  |      -0.62 |      -0.58 |    1.51 |           1.17 |         0 |      0.03 |       -0.01 |     1.49 | 234 |


Signature check (split-half): 2/8 clips' first half is closest to their own second half (chance 0.12). Camera angle also differs between clips, so this mixes dancer style and viewpoint.


## Validation sheets
check_weight_share.jpg, check_contact_regions.jpg, check_word_*.jpg — every detector must be eyeballed before use.