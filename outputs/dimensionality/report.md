# Idea B: effective dimensionality of each dancer's pose trajectory

12 body keypoints, hip-centred, / window median trunk length; 5-s windows at 15 fps; conf >= 0.5 on all 12 keypoints. PR = participation ratio (1 = one dimension, 24 = isotropic 2-D noise). n90 = components for 90 % variance.

Median jitter per coordinate (from the smoothing residual): CI 0.0393 bl, salsa renders 0.0305 bl.

## 1. Validation on Bigand et al. 2024 (35 dyads x 8 trials x 2 dancers)

|   jitter_added_bl |   windows |   pr_3d |   pr_2d_raw |   pr_2d_denoised |   pr_2d_smooth |   n90_3d |   n90_2d_raw |   n90_2d_dn |   spearman_window_3d_vs_2d_raw |   spearman_window_3d_vs_2d_dn |   spearman_dancer_3d_vs_2d_raw |   spearman_dancer_3d_vs_2d_dn |
|------------------:|----------:|--------:|------------:|-----------------:|---------------:|---------:|-------------:|------------:|-------------------------------:|------------------------------:|-------------------------------:|------------------------------:|
|             0     |      6720 |   2.169 |       2.275 |            2.247 |          2.23  |        3 |            3 |           3 |                          0.534 |                         0.536 |                          0.412 |                         0.422 |
|             0.005 |      6720 |   2.169 |       2.857 |            2.561 |          2.628 |        3 |            4 |           4 |                          0.251 |                         0.42  |                          0.161 |                         0.231 |
|             0.01  |      6720 |   2.169 |       3.182 |            2.709 |          2.841 |        3 |            5 |           4 |                          0.138 |                         0.361 |                         -0.145 |                         0.207 |
|             0.02  |      6720 |   2.169 |       3.885 |            2.814 |          3.188 |        3 |            7 |           4 |                          0.015 |                         0.289 |                         -0.332 |                         0.075 |
|             0.039 |      6720 |   2.169 |       5.902 |            2.948 |          3.91  |        3 |           12 |           4 |                         -0.091 |                         0.241 |                         -0.425 |                         0.024 |


## 2. CI vs salsa vs Bigand, per dancer (median over the dancer's windows)

| source               |   dancers |   windows |   pr_raw |   pr_dn |   pr_smooth |   n90_raw |   n90_dn |   jitter_bl |   total_var |
|:---------------------|----------:|----------:|---------:|--------:|------------:|----------:|---------:|------------:|------------:|
| Bigand 2-D+CI jitter |        70 |      6720 |    5.552 |   2.98  |       3.805 |        11 |        4 |       0.048 |       0.094 |
| CI                   |        22 |       306 |    2.577 |   2.446 |       2.462 |         4 |        3 |       0.041 |       2.366 |
| salsa                |         5 |         8 |    2.676 |   2.499 |       2.528 |         4 |        4 |       0.029 |       1.156 |
| salsa+jitter         |         5 |         8 |    2.811 |   2.566 |       2.598 |         4 |        4 |       0.042 |       1.156 |


Mann-Whitney across dancers (dancers within a duet are not independent; treat p as descriptive):

| contrast                   | measure   |   ci_median |   other_median |   mannwhitney_p |   n_ci |   n_other |
|:---------------------------|:----------|------------:|---------------:|----------------:|-------:|----------:|
| CI vs salsa                | pr_raw    |      2.5771 |         2.6758 |          0.9759 |     22 |         5 |
| CI vs salsa                | pr_dn     |      2.4455 |         2.4989 |          0.8325 |     22 |         5 |
| CI vs salsa                | pr_smooth |      2.4623 |         2.5276 |          0.8325 |     22 |         5 |
| CI vs salsa+jitter         | pr_raw    |      2.5771 |         2.8109 |          0.8799 |     22 |         5 |
| CI vs salsa+jitter         | pr_dn     |      2.4455 |         2.5662 |          0.9759 |     22 |         5 |
| CI vs salsa+jitter         | pr_smooth |      2.4623 |         2.5983 |          0.8799 |     22 |         5 |
| CI vs Bigand 2-D+CI jitter | pr_raw    |      2.5771 |         5.552  |          0      |     22 |        70 |
| CI vs Bigand 2-D+CI jitter | pr_dn     |      2.4455 |         2.98   |          0      |     22 |        70 |
| CI vs Bigand 2-D+CI jitter | pr_smooth |      2.4623 |         3.8045 |          0      |     22 |        70 |


## 3. Within CI: by duet state (window majority state)

| state   |   windows |   pr_raw |   pr_dn |   jitter_bl |   total_var |
|:--------|----------:|---------:|--------:|------------:|------------:|
| apart   |        60 |    2.68  |   2.63  |       0.022 |       0.666 |
| contact |       136 |    2.496 |   2.351 |       0.044 |       2.276 |
| floor   |        50 |    2.34  |   2.202 |       0.051 |       3.846 |
| near    |        20 |    2.279 |   2.235 |       0.021 |       1.843 |
| none    |        22 |    2.636 |   2.448 |       0.059 |       1.844 |
| share   |        18 |    2.807 |   2.62  |       0.118 |       5.441 |


Per CI duet:

| video            |   windows |   pr_raw |   pr_dn |   jitter_bl |
|:-----------------|----------:|---------:|--------:|------------:|
| Rc9vIJt00vs_full |        34 |    2.526 |   2.369 |       0.07  |
| YR2QCf5cL6Q_full |        25 |    2.622 |   2.395 |       0.057 |
| dGPRMNAECKM_full |        12 |    2.491 |   2.383 |       0.064 |
| hJQgFDsAms4_full |        44 |    2.329 |   2.157 |       0.048 |
| iOEZ3i9rgYM_full |        41 |    2.273 |   2.196 |       0.039 |
| kMkJpfUGZz8_full |        28 |    2.334 |   2.216 |       0.023 |
| kxztAr2tQmE_full |         5 |    2.882 |   2.809 |       0.026 |
| swmrAJkYrlY_full |        21 |    2.356 |   2.319 |       0.026 |
| uS1JQ-LY8Fs_full |        47 |    2.393 |   2.148 |       0.016 |
| vinlwkaIW4c_full |        41 |    2.9   |   2.709 |       0.052 |
| zQRF2sLK1vY      |         8 |    3.13  |   3.026 |       0.042 |


## 4. Selection bias: share of detected frames with all 12 keypoints at conf >= 0.5

|                    |   frames |   pass_frac |
|:-------------------|---------:|------------:|
| ('CI', 'apart')    |     7662 |       0.641 |
| ('CI', 'contact')  |    33436 |       0.551 |
| ('CI', 'floor')    |    12461 |       0.593 |
| ('CI', 'near')     |     5391 |       0.647 |
| ('CI', 'none')     |     4654 |       0.697 |
| ('CI', 'share')    |     4948 |       0.673 |
| ('salsa', 'salsa') |     4696 |       0.511 |


Correlation across windows of jitter with PR (CI): raw r = 0.27, denoised r = 0.21 (Spearman)