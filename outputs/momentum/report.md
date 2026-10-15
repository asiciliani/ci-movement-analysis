# Idea A: momentum ride / energy hand-off

Signal: pelvis d(v^2)/dt per dancer (camera-compensated, body lengths from a rolling 5 s trunk length, rank -> normal scores). `r0` = lag-0 correlation between the two dancers; `rmin` = most negative r within ±1 s; `frac_neg` / `frac_pos` = share of 2-s windows with r < -0.5 / > +0.5. Nulls: B circularly shifted ≥ 5 s with the state mask fixed (`_null_mean`, `_p`). `campart` = after regressing out camera speed, zoom and shared scale change.

## CI duets (10 clips)

| video            |   contact_share |   contact_n_frames |   contact_r0 |   contact_r0_null_mean |   contact_r0_p |   contact_campart_r0 |   contact_campart_r0_p |   contact_nocomp_r0 |   apart_n_frames |   apart_r0 |   apart_r0_p |   apart_campart_r0 |   apart_campart_r0_p |   apart_nocomp_r0 |
|:-----------------|----------------:|-------------------:|-------------:|-----------------------:|---------------:|---------------------:|-----------------------:|--------------------:|-----------------:|-----------:|-------------:|-------------------:|---------------------:|------------------:|
| zQRF2sLK1vY      |           0.472 |                497 |        0.129 |                  0     |          0.104 |                0.134 |                  0.045 |               0.201 |              230 |      0.011 |        0.905 |              0.012 |                0.896 |             0.036 |
| kxztAr2tQmE_full |           0.686 |                471 |        0.277 |                 -0.003 |          0.005 |                0.284 |                  0.005 |               0.277 |               93 |      0.232 |        0.184 |              0.258 |                0.09  |             0.232 |
| swmrAJkYrlY_full |           0.484 |                761 |        0.127 |                 -0.001 |          0.01  |                0.128 |                  0.01  |               0.227 |              912 |      0.112 |        0.015 |              0.114 |                0.015 |             0.239 |
| hJQgFDsAms4_full |           0.583 |               1451 |        0.099 |                 -0     |          0.015 |                0.097 |                  0.035 |               0.062 |              244 |      0.004 |        0.99  |              0.004 |                0.94  |             0.042 |
| iOEZ3i9rgYM_full |           0.854 |               2028 |        0.103 |                 -0.001 |          0.005 |                0.105 |                  0.005 |               0.103 |               66 |     -0.17  |        0.178 |             -0.163 |                0.283 |            -0.178 |
| dGPRMNAECKM_full |           0.675 |               1030 |        0.037 |                  0.008 |          0.458 |                0.013 |                  0.692 |               0.014 |               59 |     -0.203 |      nan     |             -0.254 |              nan     |            -0.125 |
| Rc9vIJt00vs_full |           0.653 |               1696 |        0.042 |                 -0.002 |          0.179 |                0.048 |                  0.149 |              -0.001 |              529 |      0.055 |        0.438 |              0.042 |                0.498 |             0.073 |
| vinlwkaIW4c_full |           0.623 |               1485 |        0.194 |                 -0.003 |          0.005 |                0.198 |                  0.005 |               0.224 |              602 |      0.085 |        0.174 |              0.096 |                0.189 |             0.057 |
| kMkJpfUGZz8_full |           0.45  |                986 |        0.075 |                 -0.004 |          0.05  |                0.069 |                  0.095 |               0.23  |              695 |      0.017 |        0.756 |              0.016 |                0.801 |             0.033 |
| uS1JQ-LY8Fs_full |           0.507 |                349 |       -0.077 |                 -0.011 |          0.688 |               -0.071 |                  0.741 |               0.023 |              334 |     -0.022 |        0.928 |             -0.022 |                0.878 |            -0.042 |
| YR2QCf5cL6Q_full |           0.642 |               1130 |        0.115 |                 -0.002 |          0.025 |                0.113 |                  0.02  |               0.158 |              192 |     -0.074 |        0.58  |             -0.077 |                0.598 |            -0.006 |


Windows (2 s): hand-off (r < -0.5) and co-moving (r > 0.5) shares vs the circular null

| video            |   contact_rmin |   contact_rmin_null_mean |   contact_rmin_p |   contact_frac_neg |   contact_frac_neg_null_mean |   contact_frac_neg_p |   contact_frac_pos |   contact_frac_pos_null_mean |   contact_frac_pos_p |   apart_frac_neg |   apart_frac_neg_null_mean |   apart_frac_neg_p |   contact_campart_frac_neg |   contact_campart_frac_neg_p |
|:-----------------|---------------:|-------------------------:|-----------------:|-------------------:|-----------------------------:|---------------------:|-------------------:|-----------------------------:|---------------------:|-----------------:|---------------------------:|-------------------:|---------------------------:|-----------------------------:|
| zQRF2sLK1vY      |         -0.211 |                   -0.166 |            0.169 |              0     |                        0.012 |                1     |              0.077 |                        0.01  |                0.067 |          nan     |                    nan     |            nan     |                      0     |                        1     |
| kxztAr2tQmE_full |         -0.185 |                   -0.132 |            0.114 |              0     |                        0.024 |                1     |              0.417 |                        0.03  |                0.005 |            0.333 |                      0.04  |              0.106 |                      0     |                        1     |
| swmrAJkYrlY_full |         -0.089 |                   -0.092 |            0.483 |              0     |                        0.021 |                1     |              0.027 |                        0.026 |                0.338 |            0.029 |                      0.035 |              0.448 |                      0     |                        1     |
| hJQgFDsAms4_full |         -0.097 |                   -0.087 |            0.353 |              0     |                        0.007 |                1     |              0.031 |                        0.015 |                0.171 |            0     |                      0.009 |              1     |                      0     |                        1     |
| iOEZ3i9rgYM_full |         -0.088 |                   -0.054 |            0.01  |              0     |                        0.011 |                1     |              0.095 |                        0.015 |                0.005 |            0     |                      0.017 |              1     |                      0     |                        1     |
| dGPRMNAECKM_full |         -0.085 |                   -0.086 |            0.463 |              0     |                        0.013 |                1     |              0.136 |                        0.026 |                0.02  |          nan     |                    nan     |            nan     |                      0     |                        1     |
| Rc9vIJt00vs_full |         -0.079 |                   -0.062 |            0.179 |              0     |                        0.017 |                1     |              0     |                        0.023 |                1     |            0     |                      0.032 |              1     |                      0     |                        1     |
| vinlwkaIW4c_full |         -0.131 |                   -0.071 |            0.005 |              0.018 |                        0.023 |                0.483 |              0.036 |                        0.027 |                0.313 |            0     |                      0.034 |              1     |                      0.018 |                        0.403 |
| kMkJpfUGZz8_full |         -0.096 |                   -0.085 |            0.318 |              0     |                        0.016 |                1     |              0.054 |                        0.019 |                0.09  |            0     |                      0.019 |              1     |                      0.036 |                        0.139 |
| uS1JQ-LY8Fs_full |         -0.199 |                   -0.303 |            0.859 |              0.136 |                        0.05  |                0.086 |              0     |                        0.027 |                1     |            0     |                      0     |              1     |                      0.182 |                        0.081 |
| YR2QCf5cL6Q_full |         -0.09  |                   -0.099 |            0.597 |              0     |                        0.02  |                1     |              0.064 |                        0.026 |                0.154 |            0     |                      0.013 |              1     |                      0     |                        1     |


Summary across the 10 duets: contact_r0_med = 0.103, contact_r0_pos = 10, apart_r0_med = 0.011, contact_vs_apart_p = 0.00977, contact_campart_med = 0.105, n_contact_r0_sig = 7, n_contact_campart_sig = 7, n_apart_r0_sig = 1, n_fracneg_sig = 0, n_fracneg_campart_sig = 0, n_fracpos_sig = 3, fracneg_excess_med = -0.0133, fracneg_excess_p = 0.0537


## Pseudo-pairs (dancer A of one duet vs dancer B of another, all frames)

| video            |   true_r0_all |   pseudo_mean |   pseudo_sd |   pseudo_lo |   pseudo_hi |   n_pseudo |
|:-----------------|--------------:|--------------:|------------:|------------:|------------:|-----------:|
| zQRF2sLK1vY      |         0.049 |        -0.016 |       0.079 |      -0.182 |       0.081 |         20 |
| kxztAr2tQmE_full |         0.251 |         0.005 |       0.062 |      -0.106 |       0.098 |         20 |
| swmrAJkYrlY_full |         0.125 |        -0.009 |       0.045 |      -0.113 |       0.049 |         20 |
| hJQgFDsAms4_full |         0.054 |         0.018 |       0.034 |      -0.032 |       0.086 |         20 |
| iOEZ3i9rgYM_full |         0.083 |        -0.008 |       0.039 |      -0.095 |       0.054 |         20 |
| dGPRMNAECKM_full |         0.026 |         0.008 |       0.04  |      -0.079 |       0.077 |         20 |
| Rc9vIJt00vs_full |         0.059 |        -0.014 |       0.032 |      -0.075 |       0.039 |         20 |
| vinlwkaIW4c_full |         0.128 |         0.012 |       0.038 |      -0.037 |       0.089 |         20 |
| kMkJpfUGZz8_full |         0.057 |        -0.001 |       0.035 |      -0.064 |       0.064 |         20 |
| uS1JQ-LY8Fs_full |        -0.039 |        -0.025 |       0.074 |      -0.207 |       0.039 |         20 |
| YR2QCf5cL6Q_full |         0.046 |         0.004 |       0.047 |      -0.075 |       0.096 |         20 |


## Continuity: near-stopped fraction (pelvis < 0.25 bl/s) and SPARC, contact vs apart, per dancer

| video            | dancer   |   contact_n |   apart_n |   contact_jitter_bl |   apart_jitter_bl |   apart_nm_jitter_bl |   contact_stop_frac |   apart_stop_frac |   apart_nm_stop_frac |   contact_speed_med |   apart_speed_med |   contact_sparc |   apart_sparc |   apart_nm_sparc |
|:-----------------|:---------|------------:|----------:|--------------------:|------------------:|---------------------:|--------------------:|------------------:|---------------------:|--------------------:|------------------:|----------------:|--------------:|-----------------:|
| zQRF2sLK1vY      | A        |         574 |       230 |               0.021 |             0.018 |                0.022 |               0.091 |             0.078 |                0.065 |               0.669 |             0.925 |          -3.111 |       nan     |          nan     |
| zQRF2sLK1vY      | B        |         636 |       270 |               0.028 |             0.019 |                0.028 |               0.107 |             0.081 |                0.074 |               0.883 |             1.332 |          -2.65  |       nan     |          nan     |
| kxztAr2tQmE_full | A        |         567 |        93 |               0.023 |             0.018 |                0.023 |               0.173 |             0.075 |                0.097 |               0.963 |             0.885 |          -3.591 |       nan     |          nan     |
| kxztAr2tQmE_full | B        |         568 |        93 |               0.028 |             0.019 |                0.029 |               0.113 |             0.065 |                0.054 |               1.071 |             1.41  |          -2.903 |       nan     |          nan     |
| swmrAJkYrlY_full | A        |         990 |       967 |               0.02  |             0.013 |                0.02  |               0.175 |             0.118 |                0.104 |               0.857 |             1.038 |          -2.81  |        -2.53  |           -2.628 |
| swmrAJkYrlY_full | B        |         824 |       965 |               0.019 |             0.014 |                0.019 |               0.157 |             0.132 |                0.132 |               0.904 |             0.905 |          -2.408 |        -2.457 |           -2.242 |
| hJQgFDsAms4_full | A        |        2013 |       278 |               0.032 |             0.008 |                0.033 |               0.235 |             0.622 |                0.5   |               0.566 |             0.118 |          -3.73  |        -3.035 |           -3.642 |
| hJQgFDsAms4_full | B        |        1883 |       262 |               0.03  |             0.017 |                0.03  |               0.279 |             0.439 |                0.382 |               0.471 |             0.286 |          -3.364 |        -3.109 |           -3.089 |
| iOEZ3i9rgYM_full | A        |        2319 |        66 |               0.018 |             0.006 |                0.019 |               0.288 |             0.53  |                0.439 |               0.385 |             0.224 |          -2.894 |       nan     |          nan     |
| iOEZ3i9rgYM_full | B        |        2332 |        69 |               0.021 |             0.007 |                0.021 |               0.293 |             0.812 |                0.652 |               0.409 |             0.11  |          -3.116 |       nan     |          nan     |
| dGPRMNAECKM_full | A        |        1267 |        96 |               0.026 |             0.021 |                0.027 |               0.141 |             0.156 |                0.146 |               0.835 |             0.607 |          -2.737 |       nan     |          nan     |
| dGPRMNAECKM_full | B        |        1241 |       133 |               0.024 |             0.016 |                0.024 |               0.188 |             0.203 |                0.18  |               0.654 |             0.717 |          -2.653 |       nan     |          nan     |
| Rc9vIJt00vs_full | A        |        2230 |       548 |               0.029 |             0.024 |                0.03  |               0.137 |             0.15  |                0.144 |               0.819 |             0.899 |          -3.012 |        -3.417 |           -3.555 |
| Rc9vIJt00vs_full | B        |        2284 |       596 |               0.035 |             0.022 |                0.036 |               0.155 |             0.156 |                0.134 |               0.864 |             0.839 |          -2.879 |        -2.937 |           -3.175 |
| vinlwkaIW4c_full | A        |        1711 |       602 |               0.027 |             0.024 |                0.028 |               0.133 |             0.156 |                0.15  |               0.722 |             0.866 |          -2.94  |        -2.214 |           -2.205 |
| vinlwkaIW4c_full | B        |        1711 |       602 |               0.032 |             0.022 |                0.032 |               0.112 |             0.159 |                0.156 |               0.796 |             0.8   |          -3.112 |        -2.384 |           -2.252 |
| kMkJpfUGZz8_full | A        |        1111 |       731 |               0.021 |             0.013 |                0.021 |               0.269 |             0.096 |                0.092 |               0.872 |             0.992 |          -3.001 |        -2.67  |           -2.771 |
| kMkJpfUGZz8_full | B        |        1125 |       695 |               0.022 |             0.013 |                0.024 |               0.257 |             0.154 |                0.117 |               0.867 |             0.957 |          -2.819 |        -2.091 |           -2.265 |
| uS1JQ-LY8Fs_full | A        |         418 |       345 |               0.01  |             0.005 |                0.011 |               0.612 |             0.733 |                0.719 |               0.189 |             0.116 |          -2.727 |       nan     |          nan     |
| uS1JQ-LY8Fs_full | B        |         361 |       343 |               0.012 |             0.013 |                0.013 |               0.626 |             0.362 |                0.362 |               0.196 |             0.347 |          -3.019 |       nan     |          nan     |
| YR2QCf5cL6Q_full | A        |        1466 |       207 |               0.027 |             0.025 |                0.028 |               0.156 |             0.179 |                0.179 |               0.716 |             0.743 |          -2.959 |       nan     |          nan     |
| YR2QCf5cL6Q_full | B        |        1472 |       215 |               0.033 |             0.027 |                0.034 |               0.173 |             0.112 |                0.116 |               0.649 |             0.943 |          -3.707 |       nan     |          nan     |


Per duet (mean of the two dancers), Wilcoxon across 10 duets: stop_contact_minus_apart_med = 0.0189, p = 0.765, stop_contact_minus_apart_nm_med = 0.0165, p_nm = 0.577, sparc_contact_minus_apart_med = -0.475, p_sparc = 0.188, sparc_contact_minus_apart_nm_med = -0.181, p_sparc_nm = 0.438, jitter_ratio_contact_apart_med = 1.39


## Ground truth 1: Bigand et al. 2024 (free dance, never touching)

|              |   trials |   r0_mean |   r0_null_mean |   r0_sig |   frac_neg |   frac_neg_null |   frac_neg_sig |   frac_pos |   frac_pos_null |   stop_frac |   sparc |
|:-------------|---------:|----------:|---------------:|---------:|-----------:|----------------:|---------------:|-----------:|----------------:|------------:|--------:|
| (0.0, 0, 0)  |      279 |     0.005 |             -0 |    0.108 |      0.039 |           0.037 |          0.047 |      0.046 |           0.042 |       0.594 |  -2.774 |
| (0.0, 0, 1)  |      280 |     0.015 |             -0 |    0.168 |      0.037 |           0.037 |          0.057 |      0.055 |           0.043 |       0.584 |  -2.761 |
| (0.0, 1, 0)  |      281 |     0.007 |              0 |    0.125 |      0.04  |           0.037 |          0.057 |      0.051 |           0.043 |       0.578 |  -2.77  |
| (0.0, 1, 1)  |      280 |     0.043 |             -0 |    0.211 |      0.035 |           0.036 |          0.046 |      0.065 |           0.043 |       0.581 |  -2.778 |
| (0.02, 0, 0) |      279 |     0.008 |             -0 |    0.133 |      0.018 |           0.013 |          0.05  |      0.025 |           0.017 |       0.626 |  -3.146 |
| (0.02, 0, 1) |      280 |     0.019 |             -0 |    0.15  |      0.017 |           0.013 |          0.054 |      0.037 |           0.017 |       0.617 |  -3.144 |
| (0.02, 1, 0) |      281 |     0.007 |              0 |    0.128 |      0.02  |           0.013 |          0.089 |      0.03  |           0.018 |       0.612 |  -3.141 |
| (0.02, 1, 1) |      280 |     0.045 |             -0 |    0.204 |      0.015 |           0.013 |          0.082 |      0.046 |           0.017 |       0.614 |  -3.143 |


`r0_sig` / `frac_neg_sig` = share of trials with circular-null p < 0.05 (two-sided for r0, one-sided for frac_neg); with no channel (curtain + different music) these are false-positive rates, nominal 0.05.


## Ground truth 2: CoMPAS3D salsa pelvis translation (hand-hold partner dance)

|   jitter_bl |   seqs |   r0_mean |   r0_median |   r0_null_mean |   r0_sig |   frac_neg |   frac_neg_null |   frac_neg_sig |   frac_pos |   frac_pos_null |
|------------:|-------:|----------:|------------:|---------------:|---------:|-----------:|----------------:|---------------:|-----------:|----------------:|
|        0    |     71 |     0.211 |       0.207 |         -0.003 |    0.746 |      0.016 |           0.051 |          0.014 |      0.254 |           0.057 |
|        0.02 |     71 |     0.14  |       0.111 |         -0.001 |    0.662 |      0.01  |           0.021 |          0     |      0.118 |           0.031 |


### Same salsa performances through the video pipeline vs their own mocap (first 60 s)

| video                   | assignment   |   speed_r_video_mocap |   speed_peak_lag_s |   both_present |   video_r0 |   video_rmin |   video_frac_neg |   video_frac_pos |   video_n_win |   video_n_frames |   video_r0_null_mean |   video_r0_p |   video_rmin_null_mean |   video_rmin_p |   mocap_r0 |   mocap_rmin |   mocap_frac_neg |   mocap_frac_pos |   mocap_n_win |   mocap_n_frames |   mocap_r0_null_mean |   mocap_r0_p |   mocap_rmin_null_mean |   mocap_rmin_p |   mocap_frac_neg_null_mean |   mocap_frac_neg_p |   mocap_frac_pos_null_mean |   mocap_frac_pos_p |
|:------------------------|:-------------|----------------------:|-------------------:|---------------:|-----------:|-------------:|-----------------:|-----------------:|--------------:|-----------------:|---------------------:|-------------:|-----------------------:|---------------:|-----------:|-------------:|-----------------:|-----------------:|--------------:|-----------------:|---------------------:|-------------:|-----------------------:|---------------:|---------------------------:|-------------------:|---------------------------:|-------------------:|
| salsa_Pair1_song1_take1 | A=leader     |                 0.228 |              0.767 |          0.344 |     -0.008 |       -0.226 |              nan |              nan |             0 |              303 |               -0.004 |        0.98  |                 -0.137 |          0.01  |      0.211 |       -0.246 |            0.052 |            0.252 |           115 |             1786 |                0.016 |        0.04  |                 -0.173 |          0.069 |                      0.046 |              0.337 |                      0.071 |              0.01  |
| salsa_Pair2_song2_take1 | A=leader     |                 0.237 |             -0.133 |          0.782 |      0.156 |       -0.198 |                0 |                0 |             5 |              732 |               -0.008 |        0.089 |                 -0.173 |          0.307 |      0.136 |       -0.171 |            0.009 |            0.157 |           115 |             1786 |               -0     |        0.02  |                 -0.104 |          0.01  |                      0.041 |              0.881 |                      0.049 |              0.01  |
| salsa_Pair5_song2_take1 | A=leader     |                 0.165 |             -1     |          0.777 |      0.144 |       -0.169 |              nan |              nan |             0 |              642 |               -0.005 |        0.099 |                 -0.171 |          0.495 |      0.02  |       -0.275 |            0.07  |            0.078 |           115 |             1786 |               -0     |        0.693 |                 -0.1   |          0.01  |                      0.035 |              0.109 |                      0.049 |              0.198 |