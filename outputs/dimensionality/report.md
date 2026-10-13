# Idea B: effective dimensionality of each dancer's pose trajectory

12 body keypoints, hip-centred, / window median trunk length; 5-s windows at 15 fps; conf >= 0.5 on all 12 keypoints. PR = participation ratio (1 = one dimension, 24 = isotropic 2-D noise). n90 = components for 90 % variance.

Median jitter per coordinate (from the smoothing residual): CI 0.0401 bl, salsa renders 0.0334 bl.

## 1. Validation on Bigand et al. 2024 (35 dyads x 8 trials x 2 dancers)

|   jitter_added_bl |   windows |   pr_3d |   pr_2d_raw |   pr_2d_denoised |   pr_2d_smooth |   n90_3d |   n90_2d_raw |   n90_2d_dn |   spearman_window_3d_vs_2d_raw |   spearman_window_3d_vs_2d_dn |   spearman_dancer_3d_vs_2d_raw |   spearman_dancer_3d_vs_2d_dn |
|------------------:|----------:|--------:|------------:|-----------------:|---------------:|---------:|-------------:|------------:|-------------------------------:|------------------------------:|-------------------------------:|------------------------------:|
|             0     |      6720 |   2.169 |       2.275 |            2.247 |          2.23  |        3 |            3 |           3 |                          0.534 |                         0.536 |                          0.412 |                         0.422 |
|             0.005 |      6720 |   2.169 |       2.857 |            2.561 |          2.628 |        3 |            4 |           4 |                          0.251 |                         0.42  |                          0.161 |                         0.231 |
|             0.01  |      6720 |   2.169 |       3.182 |            2.709 |          2.841 |        3 |            5 |           4 |                          0.138 |                         0.361 |                         -0.145 |                         0.207 |
|             0.02  |      6720 |   2.169 |       3.885 |            2.814 |          3.188 |        3 |            7 |           4 |                          0.015 |                         0.289 |                         -0.332 |                         0.075 |
|             0.04  |      6720 |   2.169 |       5.997 |            2.954 |          3.944 |        3 |           12 |           4 |                         -0.093 |                         0.241 |                         -0.423 |                         0.011 |


## 2. CI vs salsa vs Bigand, per dancer (median over the dancer's windows)

| source               |   dancers |   windows |   pr_raw |   pr_dn |   pr_smooth |   n90_raw |   n90_dn |   jitter_bl |   total_var |
|:---------------------|----------:|----------:|---------:|--------:|------------:|----------:|---------:|------------:|------------:|
| Bigand 2-D+CI jitter |        70 |      6720 |    5.627 |   2.98  |       3.816 |     11.25 |      4   |       0.049 |       0.095 |
| CI                   |        20 |       303 |    2.638 |   2.512 |       2.563 |      4    |      3   |       0.05  |       1.995 |
| salsa                |         5 |        11 |    2.483 |   2.365 |       2.329 |      4    |      3.5 |       0.033 |       1.286 |
| salsa+jitter         |         5 |        11 |    2.642 |   2.438 |       2.418 |      4.5  |      4   |       0.045 |       1.27  |


Mann-Whitney across dancers (dancers within a duet are not independent; treat p as descriptive):

| contrast                   | measure   |   ci_median |   other_median |   mannwhitney_p |   n_ci |   n_other |
|:---------------------------|:----------|------------:|---------------:|----------------:|-------:|----------:|
| CI vs salsa                | pr_raw    |      2.6382 |         2.4834 |          0.9215 |     20 |         5 |
| CI vs salsa                | pr_dn     |      2.5118 |         2.3648 |          0.8694 |     20 |         5 |
| CI vs salsa                | pr_smooth |      2.563  |         2.329  |          0.8694 |     20 |         5 |
| CI vs salsa+jitter         | pr_raw    |      2.6382 |         2.6419 |          0.9738 |     20 |         5 |
| CI vs salsa+jitter         | pr_dn     |      2.5118 |         2.4384 |          0.8694 |     20 |         5 |
| CI vs salsa+jitter         | pr_smooth |      2.563  |         2.4176 |          1      |     20 |         5 |
| CI vs Bigand 2-D+CI jitter | pr_raw    |      2.6382 |         5.6275 |          0      |     20 |        70 |
| CI vs Bigand 2-D+CI jitter | pr_dn     |      2.5118 |         2.9799 |          0      |     20 |        70 |
| CI vs Bigand 2-D+CI jitter | pr_smooth |      2.563  |         3.816  |          0      |     20 |        70 |


## 3. Within CI: by duet state (window majority state)

| state   |   windows |   pr_raw |   pr_dn |   jitter_bl |   total_var |
|:--------|----------:|---------:|--------:|------------:|------------:|
| apart   |        73 |    2.662 |   2.511 |       0.031 |       0.905 |
| contact |       146 |    2.628 |   2.462 |       0.039 |       1.491 |
| floor   |        37 |    2.555 |   2.441 |       0.068 |       3.666 |
| near    |        29 |    2.241 |   2.108 |       0.029 |       1.391 |
| none    |        17 |    2.573 |   2.314 |       0.053 |       2.717 |
| share   |         1 |    1.623 |   1.575 |       0.112 |      10.69  |


Per CI duet:

| video            |   windows |   pr_raw |   pr_dn |   jitter_bl |
|:-----------------|----------:|---------:|--------:|------------:|
| Rc9vIJt00vs_full |        15 |    2.261 |   2.177 |       0.072 |
| dGPRMNAECKM_full |        16 |    2.69  |   2.6   |       0.078 |
| hJQgFDsAms4_full |        16 |    3.031 |   2.735 |       0.032 |
| iOEZ3i9rgYM_full |        52 |    2.35  |   2.205 |       0.042 |
| kMkJpfUGZz8_full |        40 |    2.665 |   2.466 |       0.043 |
| kxztAr2tQmE_full |         8 |    2.695 |   2.51  |       0.052 |
| swmrAJkYrlY_full |        32 |    2.251 |   2.125 |       0.028 |
| uS1JQ-LY8Fs_full |        83 |    2.495 |   2.162 |       0.023 |
| vinlwkaIW4c_full |        31 |    3.175 |   2.983 |       0.068 |
| zQRF2sLK1vY      |        10 |    3.28  |   3.171 |       0.06  |


## 4. Selection bias: share of detected frames with all 12 keypoints at conf >= 0.5

|                    |   frames |   pass_frac |
|:-------------------|---------:|------------:|
| ('CI', 'apart')    |     6687 |       0.829 |
| ('CI', 'contact')  |    25168 |       0.728 |
| ('CI', 'floor')    |     7060 |       0.732 |
| ('CI', 'near')     |     5056 |       0.781 |
| ('CI', 'none')     |     4840 |       0.789 |
| ('CI', 'share')    |      929 |       0.826 |
| ('salsa', 'salsa') |     4405 |       0.636 |


Correlation across windows of jitter with PR (CI): raw r = 0.21, denoised r = 0.16 (Spearman)