# Yield: how CI dancers go down to the floor (falls.py)

## Validation

Round 1, describe_duets.py descents (25 random of 127):

| verdict        |   n |
|:---------------|----:|
| false          |  14 |
| kneel_to_floor |   4 |
| real_low       |   3 |
| real_floor     |   3 |
| unclear        |   1 |


Round 2 (revised detector; all its valid descents + 10 random rejected candidates, sheet blind to the decision):

| valid   |   false |   kneel_to_floor |   real_floor |   real_low |
|:--------|--------:|-----------------:|-------------:|-----------:|
| False   |       4 |                1 |            4 |          1 |
| True    |       0 |                0 |            4 |          7 |


## Per CI descent

| video            | dancer   |   start_s | hand_label   | hand_contact   |   drop_bl |   dur_10_90_s |   peak_down_v_bl_s |   peak_v_per_drop |   t_peak_frac |   peak_down_acc_g |   peak_brake_acc_g |   end_speed_ratio |   sparc |   sparc_jitter_sd |   ldlj |   ldlj_jitter_sd |   after_speed_med_bl_s |   after_moving_frac |   after_max_level |   after_trunk_rot_deg |   after_tracked |
|:-----------------|:---------|----------:|:-------------|:---------------|----------:|--------------:|-------------------:|------------------:|--------------:|------------------:|-------------------:|------------------:|--------:|------------------:|-------:|-----------------:|-----------------------:|--------------------:|------------------:|----------------------:|----------------:|
| Rc9vIJt00vs_full | A        |     90.27 | real_low     | True           |      0.71 |          0.33 |               2.24 |              3.17 |          0    |              0.37 |               0.84 |              0.27 |   -1.81 |              0.04 |  -8.14 |             0.14 |                   1.29 |                0.9  |              1.51 |                408.83 |            0.83 |
| dGPRMNAECKM_full | A        |     33.53 | real_floor   | True           |      0.9  |          0.93 |               1.16 |              1.3  |          0.64 |              0.22 |               0.21 |              0.15 |   -1.93 |              0.07 |  -8.56 |             0.19 |                   0.12 |                0.17 |              0.54 |                110.2  |            0.23 |
| hJQgFDsAms4_full | A        |    224    | real_floor   | True           |      0.61 |          1.13 |               1.02 |              1.69 |          0.76 |              0.28 |               0.23 |              0.22 |   -2.05 |              0.27 |  -9.34 |             0.38 |                   0.43 |                0.13 |              0.54 |                 26.39 |            0.3  |
| iOEZ3i9rgYM_full | B        |    174.13 | real_low     | True           |      0.69 |          1.13 |               0.77 |              1.11 |          0.59 |              0.14 |               0.8  |              0.25 |   -2.42 |              0.14 | -10.2  |             0.27 |                   0.65 |                0.7  |              0.64 |                 17.42 |            0.93 |
| kxztAr2tQmE_full | B        |     34.87 | real_low     | True           |      0.96 |          0.6  |               1.53 |              1.6  |          0.67 |              0.34 |               0.31 |              0.24 |   -1.91 |              0.14 |  -7.38 |             0.36 |                   0.31 |                0.4  |              1.16 |                 17.42 |            1    |
| uS1JQ-LY8Fs_full | A        |    327.07 | real_floor   | False          |      1.38 |          2.27 |               1.51 |              1.1  |          0.62 |              0.21 |               0.52 |              0.29 |   -2.53 |              0.11 | -11.01 |             0.16 |                   0.73 |                0.8  |              0.72 |                 38.25 |            1    |
| vinlwkaIW4c_full | B        |     73.33 | real_floor   | False          |      1.26 |          0.33 |               3.85 |              3.06 |          0.4  |              1.04 |               0.83 |              0.39 |   -1.6  |              0.06 |  -7.3  |             0.13 |                   2.18 |                0.93 |              1.74 |                 35.01 |            0.93 |
| vinlwkaIW4c_full | B        |    143.47 | real_low     | True           |      0.74 |          0.53 |               1.51 |              2.04 |          0.75 |              0.22 |               0.7  |              0.44 |   -2.72 |              0.15 |  -7.73 |             0.22 |                 nan    |              nan    |              1.74 |                 39.01 |            0.77 |
| zQRF2sLK1vY      | A        |     29.9  | real_low     | False          |      0.87 |          0.43 |               1.91 |              2.2  |          0.54 |              0.21 |               0.42 |              0.33 |   -1.71 |              0.09 |  -8.02 |             0.26 |                   1.25 |                0.93 |              0.98 |                 52.8  |            0.69 |
| zQRF2sLK1vY      | A        |     54.15 | real_low     | True           |      0.67 |          0.47 |               1.66 |              2.47 |          0.79 |              0.32 |               0.53 |              0.41 |   -2.25 |              0.07 |  -8.49 |             0.24 |                   0.79 |                0.73 |              1.04 |                 49.54 |            1    |
| zQRF2sLK1vY      | B        |     47.31 | real_low     | True           |      0.51 |          0.67 |               1.08 |              2.1  |          0.15 |              0.11 |               0.37 |              0.23 |   -1.79 |              0.07 |  -9.73 |             0.3  |                 nan    |              nan    |              0.5  |                 79.13 |            0.75 |


## Medians by source

|                      |    CI |   URFall-adl |   URFall-fall |
|:---------------------|------:|-------------:|--------------:|
| drop_bl              |  0.74 |         0.65 |          2.25 |
| dur_10_90_s          |  0.6  |         0.33 |          0.87 |
| peak_down_v_bl_s     |  1.51 |         1.78 |          3.21 |
| peak_v_per_drop      |  2.04 |         2.75 |          1.7  |
| t_peak_frac          |  0.62 |         0    |          0.76 |
| peak_down_acc_g      |  0.22 |        -0.19 |          0.59 |
| peak_brake_acc_g     |  0.52 |         0.44 |          0.69 |
| end_speed_ratio      |  0.27 |         0.18 |          0.36 |
| sparc                | -1.93 |        -1.65 |         -1.67 |
| sparc_jitter_sd      |  0.09 |         0.03 |          0.02 |
| ldlj                 | -8.49 |        -7.27 |         -8.21 |
| ldlj_jitter_sd       |  0.24 |         0.12 |          0.03 |
| after_speed_med_bl_s |  0.73 |         0.53 |          0.41 |
| after_moving_frac    |  0.73 |         0.5  |          0.38 |
| after_max_level      |  0.98 |         1.18 |          0.38 |
| after_trunk_rot_deg  | 39.01 |        42.84 |        176.03 |
| after_tracked        |  0.83 |         0.83 |          0.78 |


## CI: floor vs low, contact vs solo (medians; n tiny)

|                      |   real_floor |   real_low |
|:---------------------|-------------:|-----------:|
| drop_bl              |         1.08 |       0.71 |
| dur_10_90_s          |         1.03 |       0.53 |
| peak_down_v_bl_s     |         1.34 |       1.53 |
| peak_v_per_drop      |         1.49 |       2.1  |
| t_peak_frac          |         0.63 |       0.59 |
| peak_down_acc_g      |         0.25 |       0.22 |
| peak_brake_acc_g     |         0.38 |       0.53 |
| end_speed_ratio      |         0.26 |       0.27 |
| sparc                |        -1.99 |      -1.91 |
| sparc_jitter_sd      |         0.09 |       0.09 |
| ldlj                 |        -8.95 |      -8.14 |
| ldlj_jitter_sd       |         0.17 |       0.26 |
| after_speed_med_bl_s |         0.58 |       0.79 |
| after_moving_frac    |         0.48 |       0.73 |
| after_max_level      |         0.63 |       1.04 |
| after_trunk_rot_deg  |        36.63 |      49.54 |
| after_tracked        |         0.62 |       0.83 |



|                      |   False |   True |
|:---------------------|--------:|-------:|
| drop_bl              |    1.26 |   0.7  |
| dur_10_90_s          |    0.43 |   0.63 |
| peak_down_v_bl_s     |    1.91 |   1.33 |
| peak_v_per_drop      |    2.2  |   1.86 |
| t_peak_frac          |    0.54 |   0.65 |
| peak_down_acc_g      |    0.21 |   0.25 |
| peak_brake_acc_g     |    0.52 |   0.45 |
| end_speed_ratio      |    0.33 |   0.24 |
| sparc                |   -1.71 |  -1.99 |
| sparc_jitter_sd      |    0.09 |   0.11 |
| ldlj                 |   -8.02 |  -8.52 |
| ldlj_jitter_sd       |    0.16 |   0.25 |
| after_speed_med_bl_s |    1.25 |   0.54 |
| after_moving_frac    |    0.93 |   0.55 |
| after_max_level      |    0.98 |   0.84 |
| after_trunk_rot_deg  |   38.25 |  44.27 |
| after_tracked        |    0.93 |   0.8  |


## CI vs UR Fall (Mann-Whitney, uncorrected)

| metric           | vs          |   ci_median |   other_median |   n_ci |   n_other |   p_mannwhitney |
|:-----------------|:------------|------------:|---------------:|-------:|----------:|----------------:|
| dur_10_90_s      | URFall-fall |       0.6   |          0.867 |     11 |         8 |           0.32  |
| dur_10_90_s      | URFall-adl  |       0.6   |          0.333 |     11 |         3 |           0.528 |
| peak_down_v_bl_s | URFall-fall |       1.511 |          3.215 |     11 |         8 |           0.001 |
| peak_down_v_bl_s | URFall-adl  |       1.511 |          1.784 |     11 |         3 |           0.17  |
| peak_brake_acc_g | URFall-fall |       0.523 |          0.693 |     11 |         6 |           0.462 |
| peak_v_per_drop  | URFall-fall |       2.042 |          1.702 |     11 |         8 |           0.84  |
| peak_v_per_drop  | URFall-adl  |       2.042 |          2.753 |     11 |         3 |           0.368 |
| end_speed_ratio  | URFall-fall |       0.272 |          0.355 |     11 |         8 |           0.6   |
| end_speed_ratio  | URFall-adl  |       0.272 |          0.175 |     11 |         3 |           0.088 |
| sparc            | URFall-fall |      -1.929 |         -1.671 |     11 |         8 |           0.238 |
| sparc            | URFall-adl  |      -1.929 |         -1.649 |     11 |         3 |           0.659 |
| ldlj             | URFall-fall |      -8.488 |         -8.209 |     11 |         8 |           0.778 |
| ldlj             | URFall-adl  |      -8.488 |         -7.27  |     11 |         3 |           0.368 |
| peak_down_acc_g  | URFall-fall |       0.22  |          0.586 |     11 |         8 |           0.002 |
| peak_down_acc_g  | URFall-adl  |       0.22  |         -0.193 |     11 |         3 |           0.456 |
| drop_bl          | URFall-fall |       0.738 |          2.247 |     11 |         8 |           0     |
| drop_bl          | URFall-adl  |       0.738 |          0.648 |     11 |         3 |           0.659 |
| t_peak_frac      | URFall-fall |       0.618 |          0.76  |     11 |         8 |           0.16  |
| t_peak_frac      | URFall-adl  |       0.618 |          0     |     11 |         3 |           0.532 |
| after_max_level  | URFall-fall |       0.98  |          0.375 |     11 |         8 |           0.007 |
| after_max_level  | URFall-adl  |       0.98  |          1.18  |     11 |         3 |           0.769 |


UR Fall sequences:

| source      | video   | valid   | reject                 |   ci_rule_candidates |   ci_rule_valid |
|:------------|:--------|:--------|:-----------------------|---------------------:|----------------:|
| URFall-adl  | adl-10  | True    |                        |                    1 |               0 |
| URFall-adl  | adl-11  | True    |                        |                    1 |               0 |
| URFall-adl  | adl-21  | False   | pelvis_lost_or_no_drop |                    0 |               0 |
| URFall-adl  | adl-22  | False   | pelvis_lost_or_no_drop |                    1 |               0 |
| URFall-adl  | adl-23  | False   | pelvis_lost_or_no_drop |                    0 |               0 |
| URFall-adl  | adl-30  | True    |                        |                    0 |               0 |
| URFall-adl  | adl-36  | False   | pelvis_lost_or_no_drop |                    1 |               0 |
| URFall-adl  | adl-37  | False   | pelvis_lost_or_no_drop |                    0 |               0 |
| URFall-fall | fall-01 | True    |                        |                    0 |               0 |
| URFall-fall | fall-02 | False   | no_upright_before      |                    0 |               0 |
| URFall-fall | fall-03 | True    |                        |                    1 |               1 |
| URFall-fall | fall-05 | True    |                        |                    0 |               0 |
| URFall-fall | fall-07 | True    |                        |                    0 |               0 |
| URFall-fall | fall-09 | True    |                        |                    1 |               1 |
| URFall-fall | fall-10 | False   | no_upright_before      |                    0 |               0 |
| URFall-fall | fall-11 | True    |                        |                    1 |               1 |
| URFall-fall | fall-13 | True    |                        |                    0 |               0 |
| URFall-fall | fall-17 | False   | pelvis_lost_or_no_drop |                    0 |               0 |
| URFall-fall | fall-25 | False   | pelvis_lost_or_no_drop |                    0 |               0 |
| URFall-fall | fall-27 | False   | pelvis_lost_or_no_drop |                    0 |               0 |
| URFall-fall | fall-29 | True    |                        |                    1 |               0 |


## Limits

- 2-D monocular video: no forces, no ground contact, no depth. 'Braking' is image-plane pelvis deceleration in body lengths; the ~g figures assume a 0.5 m trunk and are a yardstick only.
- 15 fps and a 3 Hz low-pass: impacts shorter than ~0.2 s are smeared, so SPARC / jerk cannot see a hard landing; jerk-based smoothness is weakly identified at this frame rate.
- The valid CI set is precision-first: about half of the rejected candidates were real descents lost to tracking gaps and identity swaps (floor tangles, carries), so fast or entangled descents are under-represented.
- 'Floor' (pelvis < 0.6 bl above own feet) does not separate a deep squat from sitting or lying: 7 of the 11 valid descents end in a squat or kneel.
- UR Fall falls are staged by volunteers onto a mattress, filmed frontally with a static camera; drops are larger (standing to lying) and perspective differs. Body-length units do not remove that.
- n = 11 CI descents, 8 falls, 3 lying-down sequences: every comparison is descriptive.