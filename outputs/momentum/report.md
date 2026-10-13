# Idea A: momentum ride / energy hand-off

Signal: pelvis d(v^2)/dt per dancer (camera-compensated, body lengths from a rolling 5 s trunk length, rank -> normal scores). `r0` = lag-0 correlation between the two dancers; `rmin` = most negative r within ±1 s; `frac_neg` / `frac_pos` = share of 2-s windows with r < -0.5 / > +0.5. Nulls: B circularly shifted ≥ 5 s with the state mask fixed (`_null_mean`, `_p`). `campart` = after regressing out camera speed, zoom and shared scale change.

## CI duets (10 clips)

| video            |   contact_share |   contact_n_frames |   contact_r0 |   contact_r0_null_mean |   contact_r0_p |   contact_campart_r0 |   contact_campart_r0_p |   contact_nocomp_r0 |   apart_n_frames |   apart_r0 |   apart_r0_p |   apart_campart_r0 |   apart_campart_r0_p |   apart_nocomp_r0 |
|:-----------------|----------------:|-------------------:|-------------:|-----------------------:|---------------:|---------------------:|-----------------------:|--------------------:|-----------------:|-----------:|-------------:|-------------------:|---------------------:|------------------:|
| zQRF2sLK1vY      |           0.535 |                443 |       -0.063 |                  0.004 |          0.433 |               -0.058 |                  0.438 |               0.125 |              164 |     -0.072 |        0.49  |             -0.072 |                0.685 |            -0.018 |
| kxztAr2tQmE_full |           0.65  |                251 |        0.081 |                 -0.013 |          0.274 |                0.088 |                  0.368 |               0.081 |               88 |     -0.303 |        0.109 |             -0.283 |                0.16  |            -0.302 |
| swmrAJkYrlY_full |           0.568 |                822 |        0.052 |                 -0.006 |          0.209 |                0.057 |                  0.184 |               0.14  |              876 |      0.091 |        0.134 |              0.092 |                0.065 |             0.241 |
| hJQgFDsAms4_full |           0.608 |                695 |       -0.005 |                 -0.009 |          0.955 |               -0.008 |                  0.871 |               0.039 |              130 |      0.14  |        0.453 |              0.139 |                0.377 |             0.253 |
| iOEZ3i9rgYM_full |           0.816 |               1482 |        0.067 |                 -0.003 |          0.04  |                0.067 |                  0.045 |               0.059 |               73 |     -0.188 |        0.215 |             -0.166 |                0.225 |            -0.085 |
| dGPRMNAECKM_full |           0.642 |                616 |        0.013 |                  0.004 |          0.856 |                0.013 |                  0.736 |               0.007 |               71 |     -0.124 |        0.41  |             -0.124 |                0.401 |            -0.169 |
| Rc9vIJt00vs_full |           0.669 |                725 |        0.033 |                 -0     |          0.602 |                0.032 |                  0.532 |               0.033 |              108 |     -0.173 |        0.269 |             -0.151 |                0.253 |            -0.026 |
| vinlwkaIW4c_full |           0.588 |                649 |        0.176 |                  0.002 |          0.005 |                0.172 |                  0.005 |               0.179 |              438 |      0.172 |        0.01  |              0.174 |                0.02  |             0.151 |
| kMkJpfUGZz8_full |           0.47  |                679 |        0.141 |                 -0.006 |          0.005 |                0.138 |                  0.005 |               0.145 |              645 |      0.076 |        0.174 |              0.072 |                0.229 |             0.03  |
| uS1JQ-LY8Fs_full |           0.452 |                272 |        0.004 |                 -0.03  |          0.853 |                0.011 |                  1     |               0.1   |              357 |     -0.024 |        0.993 |             -0.023 |                1     |            -0.023 |


Windows (2 s): hand-off (r < -0.5) and co-moving (r > 0.5) shares vs the circular null

| video            |   contact_rmin |   contact_rmin_null_mean |   contact_rmin_p |   contact_frac_neg |   contact_frac_neg_null_mean |   contact_frac_neg_p |   contact_frac_pos |   contact_frac_pos_null_mean |   contact_frac_pos_p |   apart_frac_neg |   apart_frac_neg_null_mean |   apart_frac_neg_p |   contact_campart_frac_neg |   contact_campart_frac_neg_p |
|:-----------------|---------------:|-------------------------:|-----------------:|-------------------:|-----------------------------:|---------------------:|-------------------:|-----------------------------:|---------------------:|-----------------:|---------------------------:|-------------------:|---------------------------:|-----------------------------:|
| zQRF2sLK1vY      |         -0.187 |                   -0.188 |            0.527 |              0.154 |                        0.009 |                0.037 |              0     |                        0.014 |                1     |          nan     |                    nan     |            nan     |                      0.154 |                        0.049 |
| kxztAr2tQmE_full |         -0.234 |                   -0.191 |            0.254 |              0     |                        0.043 |                1     |              0     |                        0.028 |                1     |          nan     |                    nan     |            nan     |                      0     |                        1     |
| swmrAJkYrlY_full |         -0.177 |                   -0.093 |            0.005 |              0.069 |                        0.022 |                0.124 |              0.138 |                        0.037 |                0.07  |            0.048 |                      0.036 |              0.284 |                      0.034 |                        0.323 |
| hJQgFDsAms4_full |         -0.108 |                   -0.137 |            0.776 |              0     |                        0.006 |                1     |              0.095 |                        0.014 |                0.037 |            0     |                      0.029 |              1     |                      0     |                        1     |
| iOEZ3i9rgYM_full |         -0.104 |                   -0.067 |            0.045 |              0.009 |                        0.015 |                0.572 |              0.061 |                        0.016 |                0.06  |            0     |                      0.023 |              1     |                      0.009 |                        0.552 |
| dGPRMNAECKM_full |         -0.107 |                   -0.133 |            0.672 |              0.037 |                        0.017 |                0.1   |              0.333 |                        0.026 |                0.02  |          nan     |                    nan     |            nan     |                      0.037 |                        0.09  |
| Rc9vIJt00vs_full |         -0.107 |                   -0.137 |            0.741 |              0.056 |                        0.01  |                0.047 |              0     |                        0.017 |                1     |          nan     |                    nan     |            nan     |                      0.056 |                        0.049 |
| vinlwkaIW4c_full |         -0.125 |                   -0.109 |            0.279 |              0     |                        0.017 |                1     |              0.083 |                        0.029 |                0.119 |            0     |                      0.031 |              1     |                      0     |                        1     |
| kMkJpfUGZz8_full |         -0.218 |                   -0.1   |            0.005 |              0     |                        0.016 |                1     |              0.083 |                        0.023 |                0.09  |            0     |                      0.023 |              1     |                      0     |                        1     |
| uS1JQ-LY8Fs_full |         -0.141 |                   -0.318 |            0.988 |              0.154 |                        0     |                0.027 |              0.077 |                        0.042 |                0.081 |            0     |                      0.019 |              1     |                      0.154 |                        0.059 |


Summary across the 10 duets: contact_r0_med = 0.0427, contact_r0_pos = 8, apart_r0_med = -0.048, contact_vs_apart_p = 0.105, contact_campart_med = 0.0447, n_contact_r0_sig = 3, n_contact_campart_sig = 3, n_apart_r0_sig = 1, n_fracneg_sig = 3, n_fracneg_campart_sig = 2, n_fracpos_sig = 2, fracneg_excess_med = 0.00737, fracneg_excess_p = 0.275


## Pseudo-pairs (dancer A of one duet vs dancer B of another, all frames)

| video            |   true_r0_all |   pseudo_mean |   pseudo_sd |   pseudo_lo |   pseudo_hi |   n_pseudo |
|:-----------------|--------------:|--------------:|------------:|------------:|------------:|-----------:|
| zQRF2sLK1vY      |         0.077 |        -0.031 |       0.043 |      -0.117 |       0.018 |         18 |
| kxztAr2tQmE_full |         0.079 |         0.007 |       0.052 |      -0.079 |       0.109 |         18 |
| swmrAJkYrlY_full |         0.067 |        -0.009 |       0.05  |      -0.113 |       0.051 |         18 |
| hJQgFDsAms4_full |        -0.009 |         0.014 |       0.048 |      -0.077 |       0.098 |         18 |
| iOEZ3i9rgYM_full |         0.061 |         0.015 |       0.045 |      -0.04  |       0.103 |         18 |
| dGPRMNAECKM_full |        -0.004 |         0     |       0.055 |      -0.107 |       0.09  |         18 |
| Rc9vIJt00vs_full |         0.014 |        -0.013 |       0.054 |      -0.117 |       0.066 |         18 |
| vinlwkaIW4c_full |         0.144 |         0.01  |       0.058 |      -0.097 |       0.126 |         18 |
| kMkJpfUGZz8_full |         0.099 |        -0.013 |       0.046 |      -0.086 |       0.074 |         18 |
| uS1JQ-LY8Fs_full |        -0.004 |         0.009 |       0.058 |      -0.107 |       0.118 |         18 |


## Continuity: near-stopped fraction (pelvis < 0.25 bl/s) and SPARC, contact vs apart, per dancer

| video            | dancer   |   contact_n |   apart_n |   contact_jitter_bl |   apart_jitter_bl |   apart_nm_jitter_bl |   contact_stop_frac |   apart_stop_frac |   apart_nm_stop_frac |   contact_speed_med |   apart_speed_med |   contact_sparc |   apart_sparc |   apart_nm_sparc |
|:-----------------|:---------|------------:|----------:|--------------------:|------------------:|---------------------:|--------------------:|------------------:|---------------------:|--------------------:|------------------:|----------------:|--------------:|-----------------:|
| zQRF2sLK1vY      | A        |         543 |       219 |               0.024 |             0.02  |                0.024 |               0.116 |             0.128 |                0.114 |               0.659 |             0.861 |          -2.176 |       nan     |          nan     |
| zQRF2sLK1vY      | B        |         587 |       171 |               0.032 |             0.029 |                0.031 |               0.133 |             0.058 |                0.058 |               0.68  |             1.302 |          -1.973 |       nan     |          nan     |
| kxztAr2tQmE_full | A        |         397 |       100 |               0.034 |             0.024 |                0.033 |               0.111 |             0.23  |                0.21  |               0.98  |             0.691 |          -3.415 |       nan     |          nan     |
| kxztAr2tQmE_full | B        |         376 |       111 |               0.037 |             0.027 |                0.039 |               0.08  |             0.072 |                0.099 |               1.067 |             1.183 |          -3.046 |       nan     |          nan     |
| swmrAJkYrlY_full | A        |        1033 |       929 |               0.023 |             0.019 |                0.023 |               0.175 |             0.098 |                0.101 |               0.711 |             0.854 |          -4.658 |        -2.629 |           -2.639 |
| swmrAJkYrlY_full | B        |        1066 |      1029 |               0.023 |             0.017 |                0.024 |               0.247 |             0.126 |                0.121 |               0.584 |             0.949 |          -2.778 |        -2.595 |           -2.643 |
| hJQgFDsAms4_full | A        |        1169 |       154 |               0.038 |             0.02  |                0.039 |               0.207 |             0.409 |                0.325 |               0.607 |             0.415 |          -2.614 |       nan     |          nan     |
| hJQgFDsAms4_full | B        |        1118 |       167 |               0.037 |             0.014 |                0.039 |               0.21  |             0.587 |                0.449 |               0.541 |             0.208 |          -3.284 |        -4.009 |           -3.661 |
| iOEZ3i9rgYM_full | A        |        1703 |        90 |               0.028 |             0.01  |                0.028 |               0.247 |             0.567 |                0.533 |               0.459 |             0.183 |          -3.26  |       nan     |          nan     |
| iOEZ3i9rgYM_full | B        |        2096 |       122 |               0.024 |             0.02  |                0.024 |               0.251 |             0.32  |                0.295 |               0.454 |             0.382 |          -3.034 |       nan     |          nan     |
| dGPRMNAECKM_full | A        |         855 |       110 |               0.034 |             0.036 |                0.036 |               0.171 |             0.082 |                0.082 |               0.775 |             1.079 |          -3.091 |       nan     |          nan     |
| dGPRMNAECKM_full | B        |         859 |        79 |               0.035 |             0.024 |                0.035 |               0.172 |             0.203 |                0.152 |               0.696 |             0.542 |          -2.626 |       nan     |          nan     |
| Rc9vIJt00vs_full | A        |        1125 |       191 |               0.035 |             0.035 |                0.035 |               0.103 |             0.089 |                0.089 |               0.802 |             1.02  |          -2.078 |       nan     |          nan     |
| Rc9vIJt00vs_full | B        |        1062 |       186 |               0.037 |             0.036 |                0.037 |               0.137 |             0.07  |                0.07  |               0.734 |             0.913 |          -2.856 |       nan     |          nan     |
| vinlwkaIW4c_full | A        |        1095 |       513 |               0.048 |             0.036 |                0.049 |               0.073 |             0.097 |                0.09  |               0.962 |             0.934 |          -3.748 |       nan     |          nan     |
| vinlwkaIW4c_full | B        |        1014 |       558 |               0.045 |             0.037 |                0.045 |               0.095 |             0.099 |                0.077 |               0.892 |             0.886 |          -2.719 |       nan     |          nan     |
| kMkJpfUGZz8_full | A        |         929 |       687 |               0.028 |             0.019 |                0.028 |               0.258 |             0.066 |                0.058 |               0.878 |             1.077 |          -2.821 |        -2.716 |           -2.656 |
| kMkJpfUGZz8_full | B        |         914 |       698 |               0.029 |             0.019 |                0.03  |               0.254 |             0.146 |                0.117 |               0.818 |             0.949 |          -3.108 |        -2.345 |           -2.554 |
| uS1JQ-LY8Fs_full | A        |         329 |       357 |               0.012 |             0.005 |                0.012 |               0.587 |             0.754 |                0.734 |               0.215 |             0.117 |          -3.179 |       nan     |          nan     |
| uS1JQ-LY8Fs_full | B        |         345 |       374 |               0.013 |             0.014 |                0.014 |               0.635 |             0.406 |                0.406 |               0.185 |             0.319 |          -3.219 |       nan     |          nan     |


Per duet (mean of the two dancers), Wilcoxon across 10 duets: stop_contact_minus_apart_med = 0.03, p = 0.922, stop_contact_minus_apart_nm_med = 0.0393, p_nm = 0.77, sparc_contact_minus_apart_med = -0.434, p_sparc = nan, sparc_contact_minus_apart_nm_med = -0.359, p_sparc_nm = nan, jitter_ratio_contact_apart_med = 1.29


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