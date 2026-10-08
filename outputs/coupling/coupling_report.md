# Coupling with controls

Statistic: peak |r| of torso speeds (body lengths/s) within ±2 s. Each test compares it with a null; `p` per clip, combined by Stouffer within source group and then across groups (groups are the unit of inference).

| test | what it rules out |
|---|---|
| circ | chance alignment of autocorrelated series (circular shifts ≥ 5 s) |
| local | slow shared modulation only (shifts 3-10 s keep it, break moment-to-moment alignment) |
| low/mid/high band | high-frequency shared jitter or compression artifacts |
| cam_partial | residual camera ego-motion (speeds regressed on camera motion first) |
| scale_partial / local_bl | zoom, dolly or depth changes that scale both dancers' speeds together (shared log trunk length regressed out / speeds in each dancer's own rolling 5 s trunk length) |
| audio_partial | both dancers following the music (speeds regressed on the audio energy / onset envelopes first) |
| contact / free | rigid-body coupling while touching / coupling without touch |
| dist_x-y bl | keypoint mixing between overlapping bodies (free frames binned by nearest-keypoint distance) |
| pseudo | generic CI movement statistics (A of one clip vs B of a clip from another source) |


## primary set: 3 clips, 3 source groups (pair_ok: ('yes',))

| test               |   n_clips |   n_groups |   groups_sig |   stouffer_z |   p_stouffer |   p_binom_groups |   median_r |
|:-------------------|----------:|-----------:|-------------:|-------------:|-------------:|-----------------:|-----------:|
| circ               |         3 |          3 |            3 |       4.9862 |       0      |           0.0001 |     0.3367 |
| local              |         3 |          3 |            3 |       4.9862 |       0      |           0.0001 |     0.3367 |
| low_<0.5Hz         |         3 |          3 |            0 |       0.4259 |       0.3351 |           1      |     0.6125 |
| mid_0.5-1.5Hz      |         3 |          3 |            0 |       1.8173 |       0.0346 |           1      |     0.6824 |
| high_>1.5Hz        |         3 |          3 |            0 |       0.8973 |       0.1848 |           1      |     0.2641 |
| cam_partial        |         3 |          3 |            3 |       4.9862 |       0      |           0.0001 |     0.3373 |
| scale_partial      |         3 |          3 |            3 |       4.2857 |       0      |           0.0001 |     0.3345 |
| local_bl           |         3 |          3 |            1 |       3.1    |       0.001  |           0.1426 |     0.3588 |
| free_local_bl      |         1 |          1 |            0 |       0.9876 |       0.1617 |           1      |     0.2518 |
| audio_partial      |         3 |          3 |            2 |       4.0781 |       0      |           0.0073 |     0.3282 |
| contact            |         3 |          3 |            1 |       1.353  |       0.088  |           0.1426 |     0.3852 |
| free               |         1 |          1 |            0 |       0.8218 |       0.2056 |           1      |     0.2155 |
| free_local         |         1 |          1 |            0 |       0.3926 |       0.3473 |           1      |     0.2155 |
| free_audio_partial |         1 |          1 |            0 |       0.3711 |       0.3553 |           1      |     0.1828 |
| bounce_circ        |         3 |          3 |            3 |       4.3634 |       0      |           0.0001 |     0.3192 |
| bounce_free        |         1 |          1 |            1 |       2.3271 |       0.01   |           0.05   |     0.2509 |
| dist_0.35-1bl      |         1 |          1 |            1 |       2.0977 |       0.018  |           0.05   |     0.8685 |
| dist_1-2bl         |       nan |          0 |          nan |     nan      |     nan      |         nan      |   nan      |
| dist_2-infbl       |         1 |          1 |            0 |       0.3657 |       0.3573 |           1      |     0.21   |
| pseudo             |         3 |          3 |            2 |       2.9329 |       0.0017 |           0.0073 |     0.3477 |


Peak lag in free (no-contact) frames: median -0.13 s, |lag| <= 0.2 s in 1 of 1 clips.


## secondary set: 8 clips, 8 source groups (pair_ok: ('yes', 'partial'))

| test               |   n_clips |   n_groups |   groups_sig |   stouffer_z |   p_stouffer |   p_binom_groups |   median_r |
|:-------------------|----------:|-----------:|-------------:|-------------:|-------------:|-----------------:|-----------:|
| circ               |         8 |          8 |            6 |       6.6358 |       0      |           0      |     0.3703 |
| local              |         8 |          8 |            7 |       7.2731 |       0      |           0      |     0.3703 |
| low_<0.5Hz         |         8 |          8 |            1 |       1.8737 |       0.0305 |           0.3366 |     0.6596 |
| mid_0.5-1.5Hz      |         8 |          8 |            0 |       1.367  |       0.0858 |           1      |     0.4312 |
| high_>1.5Hz        |         8 |          8 |            0 |       1.2653 |       0.1029 |           1      |     0.2508 |
| cam_partial        |         8 |          8 |            6 |       6.7825 |       0      |           0      |     0.3163 |
| scale_partial      |         8 |          8 |            6 |       6.2088 |       0      |           0      |     0.3377 |
| local_bl           |         8 |          8 |            5 |       6.3335 |       0      |           0      |     0.3391 |
| free_local_bl      |         2 |          2 |            1 |       2.7339 |       0.0031 |           0.0975 |     0.4629 |
| audio_partial      |         8 |          8 |            5 |       6.1126 |       0      |           0      |     0.3274 |
| contact            |         8 |          8 |            2 |       2.8071 |       0.0025 |           0.0572 |     0.3957 |
| free               |         2 |          2 |            0 |       1.6469 |       0.0498 |           1      |     0.3823 |
| free_local         |         2 |          2 |            1 |       2.0545 |       0.02   |           0.0975 |     0.3823 |
| free_audio_partial |         2 |          2 |            0 |       1.3869 |       0.0827 |           1      |     0.3748 |
| bounce_circ        |         8 |          8 |            6 |       5.9405 |       0      |           0      |     0.2654 |
| bounce_free        |         2 |          2 |            1 |       2.5062 |       0.0061 |           0.0975 |     0.3726 |
| dist_0.35-1bl      |         1 |          1 |            1 |       2.0977 |       0.018  |           0.05   |     0.8685 |
| dist_1-2bl         |       nan |          0 |          nan |     nan      |     nan      |         nan      |   nan      |
| dist_2-infbl       |         1 |          1 |            0 |       0.3657 |       0.3573 |           1      |     0.21   |
| pseudo             |         8 |          8 |            5 |       4.0312 |       0      |           0      |     0.3808 |


Peak lag in free (no-contact) frames: median +0.75 s, |lag| <= 0.2 s in 1 of 2 clips.


## failed set: 3 clips, 3 source groups (pair_ok: ('no',))

| test               |   n_clips |   n_groups |   groups_sig |   stouffer_z |   p_stouffer |   p_binom_groups |   median_r |
|:-------------------|----------:|-----------:|-------------:|-------------:|-------------:|-----------------:|-----------:|
| circ               |         3 |          3 |            1 |       1.9418 |       0.0261 |           0.1426 |     0.2705 |
| local              |         3 |          3 |            1 |       1.4098 |       0.0793 |           0.1426 |     0.2705 |
| low_<0.5Hz         |         1 |          1 |            1 |       2.8788 |       0.002  |           0.05   |     0.7955 |
| mid_0.5-1.5Hz      |         1 |          1 |            1 |       2.8788 |       0.002  |           0.05   |     0.5619 |
| high_>1.5Hz        |         1 |          1 |            1 |       2.8788 |       0.002  |           0.05   |     0.3427 |
| cam_partial        |         3 |          3 |            0 |      -0.3617 |       0.6412 |           1      |     0.2298 |
| scale_partial      |         3 |          3 |            1 |       1.5334 |       0.0626 |           0.1426 |     0.2756 |
| local_bl           |         3 |          3 |            1 |       0.9652 |       0.1672 |           0.1426 |     0.3165 |
| free_local_bl      |       nan |          0 |          nan |     nan      |     nan      |         nan      |   nan      |
| audio_partial      |         3 |          3 |            1 |       2.0638 |       0.0195 |           0.1426 |     0.263  |
| contact            |         2 |          2 |            1 |       2.2016 |       0.0138 |           0.0975 |     0.4252 |
| free               |       nan |          0 |          nan |     nan      |     nan      |         nan      |   nan      |
| free_local         |       nan |          0 |          nan |     nan      |     nan      |         nan      |   nan      |
| free_audio_partial |       nan |          0 |          nan |     nan      |     nan      |         nan      |   nan      |
| bounce_circ        |         3 |          3 |            1 |       1.9783 |       0.0239 |           0.1426 |     0.2815 |
| bounce_free        |       nan |          0 |          nan |     nan      |     nan      |         nan      |   nan      |
| dist_0.35-1bl      |       nan |          0 |          nan |     nan      |     nan      |         nan      |   nan      |
| dist_1-2bl         |       nan |          0 |          nan |     nan      |     nan      |         nan      |   nan      |
| dist_2-infbl       |       nan |          0 |          nan |     nan      |     nan      |         nan      |   nan      |
| pseudo             |         3 |          3 |            1 |       2.0343 |       0.021  |           0.1426 |     0.2537 |

## all set: 21 clips, 19 source groups (pair_ok: any)

| test               |   n_clips |   n_groups |   groups_sig |   stouffer_z |   p_stouffer |   p_binom_groups |   median_r |
|:-------------------|----------:|-----------:|-------------:|-------------:|-------------:|-----------------:|-----------:|
| circ               |        21 |         19 |           12 |       8.8293 |       0      |           0      |     0.2893 |
| local              |        21 |         19 |           14 |       9.5621 |       0      |           0      |     0.2893 |
| low_<0.5Hz         |        19 |         17 |            4 |       2.3579 |       0.0092 |           0.0088 |     0.5123 |
| mid_0.5-1.5Hz      |        19 |         17 |            4 |       2.2137 |       0.0134 |           0.0088 |     0.3754 |
| high_>1.5Hz        |        19 |         17 |            6 |       5.4598 |       0      |           0.0001 |     0.3185 |
| cam_partial        |        21 |         19 |           11 |       7.4592 |       0      |           0      |     0.2298 |
| scale_partial      |        21 |         19 |           12 |       8.0503 |       0      |           0      |     0.2756 |
| local_bl           |        21 |         19 |            9 |       7.6346 |       0      |           0      |     0.2849 |
| free_local_bl      |         7 |          6 |            4 |       5.1832 |       0      |           0.0001 |     0.2505 |
| audio_partial      |        21 |         19 |           11 |       8.5432 |       0      |           0      |     0.2825 |
| contact            |        16 |         15 |            5 |       4.2818 |       0      |           0.0006 |     0.4014 |
| free               |        10 |          9 |            3 |       3.9179 |       0      |           0.0084 |     0.2659 |
| free_local         |        10 |          9 |            4 |       4.1498 |       0      |           0.0006 |     0.2659 |
| free_audio_partial |        10 |          9 |            3 |       3.7889 |       0.0001 |           0.0084 |     0.2444 |
| bounce_circ        |        21 |         19 |           10 |       5.2181 |       0      |           0      |     0.202  |
| bounce_free        |        10 |          9 |            4 |       3.2086 |       0.0007 |           0.0006 |     0.2232 |
| dist_0.35-1bl      |         6 |          5 |            2 |       2.1785 |       0.0147 |           0.0226 |     0.4113 |
| dist_1-2bl         |         5 |          4 |            1 |       1.0465 |       0.1477 |           0.1855 |     0.3837 |
| dist_2-infbl       |         8 |          7 |            4 |       4.0325 |       0      |           0.0002 |     0.4267 |
| pseudo             |        21 |         19 |            9 |       5.6109 |       0      |           0      |     0.2862 |


Peak lag in free (no-contact) frames: median +0.00 s, |lag| <= 0.2 s in 8 of 10 clips.


## Per clip

| video             | source_group        | pair_ok      |   n_frames |   contact_frac |   scale_range_log |   peak_lag_s |   peak_r |   circ_p |   local_p |   mid_0.5-1.5Hz_p |   high_>1.5Hz_p |   cam_partial_p |   scale_partial_p |   local_bl_p |   free_local_bl_p |   free_n |   free_r_obs |   free_p |   free_lag_s |   audio_A_p |   audio_B_p |   audio_partial_p |   free_audio_partial_p |   bounce_circ_p |   bounce_free_r_obs |   bounce_free_p |   dist_1-2bl_p |   dist_2-infbl_p |   p_pseudo |
|:------------------|:--------------------|:-------------|-----------:|---------------:|------------------:|-------------:|---------:|---------:|----------:|------------------:|----------------:|----------------:|------------------:|-------------:|------------------:|---------:|-------------:|---------:|-------------:|------------:|------------:|------------------:|-----------------------:|----------------:|--------------------:|----------------:|---------------:|-----------------:|-----------:|
| 65S9nuRzK4Q       | 65S9nuRzK4Q         | no           |        621 |          0.454 |             0.851 |       -1.733 |    0.271 |    0.204 |     0.393 |           nan     |         nan     |           0.717 |             0.168 |        0.096 |           nan     |      112 |      nan     |  nan     |      nan     |       0.341 |       0.405 |             0.204 |                nan     |           0.449 |             nan     |         nan     |        nan     |          nan     |      0.195 |
| QdKZlryJ4HY       | QdKZlryJ4HY         | no           |        463 |          0.191 |             1.082 |       -1.96  |    0.226 |    0.635 |     0.76  |           nan     |         nan     |           0.924 |             0.882 |        0.994 |           nan     |      283 |      nan     |  nan     |      nan     |       0.455 |       0.455 |             0.553 |                nan     |           0.337 |             nan     |         nan     |        nan     |          nan     |      0.244 |
| Rc9vIJt00vs       | Rc9vIJt00vs         | partial      |       1680 |          0.395 |             0.667 |        0     |    0.42  |    0.002 |     0.002 |             0.33  |           0.83  |           0.002 |             0.002 |        0.002 |           nan     |      254 |      nan     |  nan     |      nan     |       0.054 |       0.261 |             0.002 |                nan     |           0.15  |             nan     |         nan     |        nan     |          nan     |      0.049 |
| X-7izu2QpqA       | X-7izu2QpqA         | not_reviewed |        856 |          0     |             0.874 |        0     |    0.167 |    0.531 |     0.25  |             0.772 |           0.683 |           0.866 |             0.427 |        0.121 |           nan     |      851 |        0.167 |    0.699 |        0     |       0.034 |       0.683 |             0.479 |                  0.687 |           0.489 |               0.141 |           0.707 |        nan     |            0.754 |      0.341 |
| ci_duet_sample    | cellist_performance | not_reviewed |        231 |          0.42  |             0.608 |        0     |    0.397 |    0.459 |     0.463 |             0.068 |           0.004 |           0.517 |             0.511 |        0.002 |           nan     |       32 |      nan     |  nan     |      nan     |       0.882 |       0.413 |             0.489 |                nan     |           0.002 |             nan     |         nan     |        nan     |          nan     |      0.162 |
| dGPRMNAECKM       | dGPRMNAECKM         | partial      |        771 |          0.456 |             1.092 |        0.567 |    0.515 |    0.002 |     0.002 |             0.687 |           0.287 |           0.002 |             0.002 |        0.002 |           nan     |      104 |      nan     |  nan     |      nan     |       0.443 |       0.098 |             0.002 |                nan     |           0.032 |             nan     |         nan     |        nan     |          nan     |      0.024 |
| exploration_video | exploration_video   | not_reviewed |       4501 |          0.071 |             0.933 |        0     |    0.27  |    0.002 |     0.002 |             0.88  |           0.002 |           0.002 |             0.002 |        0.002 |             0.002 |     4093 |        0.26  |    0.002 |        0     |       0.782 |       0.178 |             0.002 |                  0.002 |           0.002 |               0.264 |           0.002 |          0.012 |            0.022 |      0.049 |
| f1o6FJL8bxM       | f1o6FJL8bxM         | not_reviewed |       1049 |          0.552 |             0.377 |        0     |    0.244 |    0.084 |     0.002 |             0.002 |           0.002 |           0.002 |             0.174 |        0.1   |           nan     |      233 |      nan     |  nan     |      nan     |       0.405 |       0.85  |             0.084 |                nan     |           0.469 |             nan     |         nan     |        nan     |          nan     |      0.073 |
| hJQgFDsAms4       | hJQgFDsAms4         | yes          |        664 |          0.386 |             0.599 |        1.401 |    0.323 |    0.002 |     0.002 |             0.174 |           0.276 |           0.002 |             0.048 |        0.116 |           nan     |      132 |      nan     |  nan     |      nan     |       0.565 |       0.064 |             0.002 |                nan     |           0.002 |             nan     |         nan     |        nan     |          nan     |      0.073 |
| iOEZ3i9rgYM       | iOEZ3i9rgYM         | partial      |        863 |          0.549 |             0.807 |       -1.969 |    0.205 |    0.15  |     0.337 |             0.579 |           0.293 |           0.148 |             0.15  |        0.152 |           nan     |       40 |      nan     |  nan     |      nan     |       0.23  |       0.086 |             0.186 |                nan     |           0.275 |             nan     |         nan     |        nan     |          nan     |      0.244 |
| iYdwYBTa4Kk       | iYdwYBTa4Kk         | not_reviewed |        684 |          0.165 |             1.514 |       -0.04  |    0.518 |    0.002 |     0.002 |             0.048 |           0.003 |           0.002 |             0.002 |        0.1   |           nan     |      501 |        0.679 |    0.058 |        0     |       0.144 |       0.555 |             0.002 |                  0.058 |           0.581 |               0.789 |           0.022 |        nan     |            0.026 |      0.024 |
| ibiza_ci          | ibiza               | not_reviewed |       3279 |          0.208 |             1.246 |        0     |    0.256 |    0.002 |     0.002 |             0.25  |           0.002 |           0.002 |             0.002 |        0.042 |             0.008 |     2604 |        0.272 |    0.002 |        0     |       0.018 |       0.05  |             0.002 |                  0.002 |           0.469 |              -0.086 |           0.593 |          0.747 |            0.002 |      0.073 |
| kxztAr2tQmE       | kxztAr2tQmE         | yes          |        704 |          0.381 |             0.39  |       -0.067 |    0.404 |    0.002 |     0.002 |             0.096 |           0.559 |           0.002 |             0.002 |        0.098 |           nan     |      198 |      nan     |  nan     |      nan     |       0.922 |       0.301 |             0.096 |                nan     |           0.002 |             nan     |         nan     |        nan     |          nan     |      0.049 |
| oB8MuarHT8E       | oB8MuarHT8E         | not_reviewed |        716 |          0.223 |             1.357 |        0     |    0.196 |    0.439 |     0.413 |             0.856 |           0.333 |           0.794 |             0.675 |        0.665 |           nan     |      480 |        0.206 |    0.828 |        0     |       0.527 |       0.433 |             0.465 |                  0.844 |           1     |               0.239 |           0.894 |        nan     |          nan     |      0.366 |
| public_ci_video   | cellist_performance | not_reviewed |       2575 |          0.239 |             0.792 |        0     |    0.289 |    0.002 |     0.002 |             0.19  |           0.002 |           0.002 |             0.002 |        0.002 |             0.018 |     1867 |        0.28  |    0.002 |        0     |       0.864 |       0.573 |             0.002 |                  0.002 |           0.002 |               0.207 |           0.036 |          0.357 |            0.036 |      0.027 |
| swmrAJkYrlY       | swmrAJkYrlY         | yes          |       3443 |          0.376 |             0.82  |        0     |    0.337 |    0.002 |     0.002 |             0.184 |           0.134 |           0.002 |             0.002 |        0.002 |             0.162 |     1820 |        0.216 |    0.206 |       -0.134 |       0.002 |       0.146 |             0.002 |                  0.355 |           0.036 |               0.251 |           0.01  |        nan     |            0.357 |      0.024 |
| user_ci_video     | user_field          | not_reviewed |       3094 |          0.194 |             0.929 |        0.067 |    0.12  |    0.002 |     0.002 |             0.998 |           0.559 |           0.142 |             0.012 |        0.216 |             0.491 |     2207 |        0.105 |    0.695 |       -1.834 |       0.285 |       0.639 |             0.002 |                  0.691 |           0.044 |              -0.127 |           0.383 |          0.78  |            0.056 |      0.707 |
| vinlwkaIW4c       | vinlwkaIW4c         | partial      |       1018 |          0.412 |             0.538 |        0.667 |    0.175 |    0.323 |     0.002 |             0.359 |           0.182 |           0.194 |             0.321 |        0.002 |             0.002 |      417 |        0.549 |    0.066 |        1.625 |       0.591 |       0.842 |             0.244 |                  0.056 |           0.002 |               0.494 |           0.112 |        nan     |          nan     |      0.488 |
| whole             | cellist_performance | not_reviewed |       4973 |          0.228 |             0.812 |        0     |    0.304 |    0.002 |     0.002 |             0.002 |           0.002 |           0.002 |             0.002 |        0.002 |             0.002 |     3631 |        0.286 |    0.002 |        0     |       0.625 |       0.733 |             0.002 |                  0.002 |           0.002 |               0.143 |           0.01  |          0.076 |            0.034 |      0.027 |
| yI_UKzqbrbw       | yI_UKzqbrbw         | no           |       1409 |          0.7   |             1.532 |        0     |    0.426 |    0.002 |     0.002 |             0.002 |           0.002 |           0.084 |             0.002 |        0.002 |           nan     |      220 |      nan     |  nan     |      nan     |       0.002 |       0.068 |             0.002 |                nan     |           0.002 |             nan     |         nan     |        nan     |          nan     |      0.024 |
| zQRF2sLK1vY       | zQRF2sLK1vY         | partial      |        910 |          0.446 |             0.772 |        0     |    0.456 |    0.002 |     0.002 |             0.273 |           0.168 |           0.002 |             0.002 |        0.002 |           nan     |      229 |      nan     |  nan     |      nan     |       0.784 |       0.932 |             0.002 |                nan     |           0.002 |             nan     |         nan     |        nan     |          nan     |      0.024 |