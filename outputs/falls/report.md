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
| Rc9vIJt00vs_full | A        |     90.2  | real_low     |                |      0.79 |          0.4  |               1.86 |              2.37 |          0.67 |              0.2  |               0.59 |              0.49 |   -1.61 |              0.06 |  -7.31 |             0.23 |                   1.08 |                0.87 |              0.75 |                169.81 |            0.73 |
| Rc9vIJt00vs_full | A        |    273.27 |              |                |      0.87 |          0.47 |               1.68 |              1.94 |          0    |              0.01 |               0.24 |              0.12 |   -1.67 |              0.09 |  -6.72 |             0.34 |                   0.28 |                0.2  |              0.71 |                 13.43 |            1    |
| Rc9vIJt00vs_full | B        |    285.73 |              |                |      1.03 |          0.93 |               1.71 |              1.66 |          0.64 |              0.36 |               0.31 |              0.31 |   -2.08 |              0.13 |  -8.95 |             0.24 |                 nan    |              nan    |              0.8  |                 96.32 |            0.83 |
| YR2QCf5cL6Q_full | A        |    280.2  |              |                |      0.88 |          0.87 |               1.82 |              2.07 |          0.85 |              0.32 |               0.6  |              0.57 |   -2.87 |              0.13 |  -8.7  |             0.15 |                   0.41 |                0.4  |              0.53 |                 92.97 |            0.97 |
| hJQgFDsAms4_full | B        |    102.4  |              |                |      0.73 |          0.27 |               2.3  |              3.17 |          0.25 |              0.47 |               0.55 |              0.4  |   -2.29 |              0.12 |  -6.87 |             0.2  |                   1.7  |                0.97 |              2.43 |                253.29 |            0.9  |
| hJQgFDsAms4_full | B        |    224    |              |                |      0.68 |          1.27 |               0.71 |              1.04 |          0.95 |              0.16 |               0.21 |              0.36 |   -2.35 |              0.23 | -10.04 |             0.23 |                   0.35 |                0.27 |              0.5  |                 11.16 |            1    |
| hJQgFDsAms4_full | B        |    468.73 |              |                |      1.04 |          2.47 |               1.67 |              1.6  |          0.35 |              0.48 |               0.73 |              0.48 |   -3.5  |              0.14 | -11.87 |             0.08 |                   0.43 |                0.47 |              0.48 |                 28.01 |            0.53 |
| iOEZ3i9rgYM_full | A        |    174    |              |                |      0.93 |          2.13 |               1.15 |              1.24 |          0.5  |              0.28 |               0.28 |              0.29 |   -3.6  |              0.24 | -11.18 |             0.18 |                   0.54 |                0.53 |              0.55 |                 15.02 |            1    |
| kMkJpfUGZz8_full | B        |     29.13 |              |                |      0.71 |          0.27 |               2.93 |              4.14 |          0    |              0.59 |               0.53 |              0.22 |   -1.78 |              0.06 |  -6.6  |             0.09 |                   1.26 |                0.97 |              1.25 |                 91.48 |            0.9  |
| kxztAr2tQmE_full | A        |     22.2  |              |                |      0.96 |          3.33 |               1.76 |              1.83 |          0.98 |              0.57 |               0.4  |              0.69 |   -4.57 |              0.12 | -11.78 |             0.08 |                   1.32 |                0.87 |              0.75 |                189.19 |            1    |
| kxztAr2tQmE_full | B        |     35.2  |              |                |      0.84 |          0.53 |               1.57 |              1.86 |          0.5  |              0.25 |               0.24 |              0.11 |   -1.41 |              0.1  |  -6.46 |             0.34 |                   0.26 |                0.4  |              1.08 |                 18.64 |            1    |
| uS1JQ-LY8Fs_full | A        |    326.93 |              |                |      1.68 |          2.47 |               1.7  |              1.01 |          0.59 |              0.29 |               0.37 |              0.19 |   -2.42 |              0.16 | -10.83 |             0.13 |                   0.5  |                0.5  |              0.48 |                 29.59 |            1    |
| vinlwkaIW4c_full | A        |     25.53 |              |                |      1.21 |          2.13 |               1.94 |              1.6  |          0.97 |              0.7  |               1.15 |              0.67 |   -3.47 |              0.12 | -11.74 |             0.03 |                   0.28 |                0.23 |              0.74 |                 58.47 |            1    |
| vinlwkaIW4c_full | A        |    190.4  |              |                |      0.85 |          1.07 |               1.46 |              1.71 |          0.62 |              0.36 |               0.26 |              0.2  |   -2    |              0.1  |  -8.64 |             0.22 |                   0.5  |                0.5  |              0.49 |                 41.42 |            1    |
| vinlwkaIW4c_full | B        |     33.47 |              |                |      1.14 |          1.6  |               1.83 |              1.61 |          0.96 |              0.73 |               0.64 |              0.44 |   -2.78 |              0.15 | -11.12 |             0.07 |                   1.28 |                0.77 |              0.54 |                 85.2  |            0.97 |
| vinlwkaIW4c_full | B        |     73.33 | real_floor   | False          |      1.01 |          0.27 |               3.38 |              3.35 |          0.5  |              0.25 |               0.91 |              0.19 |   -1.57 |              0.02 |  -6.75 |             0.13 |                   1.46 |                0.9  |              1.8  |                 47.1  |            1    |
| vinlwkaIW4c_full | B        |     84.4  |              |                |      1.07 |          0.67 |               2.81 |              2.63 |          0    |              0.25 |               0.54 |              0.09 |   -1.77 |              0.03 |  -7.81 |             0.15 |                   0.86 |                0.73 |              0.54 |                114.35 |            1    |
| vinlwkaIW4c_full | B        |    146.6  |              |                |      1.08 |          0.47 |               2.57 |              2.38 |          0.57 |              0.51 |               0.63 |              0.41 |   -1.57 |              0.05 |  -7.31 |             0.13 |                   0.3  |                0.23 |              0.54 |                 31.29 |            1    |
| vinlwkaIW4c_full | B        |    187.8  |              |                |      1.09 |          1.8  |               1.94 |              1.78 |          0.11 |              0.25 |               0.64 |              0.09 |   -2.61 |              0.09 | -10.21 |             0.12 |                   0.5  |                0.5  |              1.99 |                 61.92 |            1    |
| vinlwkaIW4c_full | B        |    199.53 |              |                |      0.93 |          0.47 |               2.08 |              2.25 |          0.57 |              0.27 |               0.47 |              0.36 |   -2.07 |              0.1  |  -7.28 |             0.21 |                   0.95 |                0.87 |              1.32 |                 68.3  |            1    |
| zQRF2sLK1vY      | A        |     30.1  |              |                |      0.65 |          0.37 |               2.16 |              3.32 |          0.09 |              0.18 |               0.38 |              0.23 |   -1.89 |              0.05 |  -7.23 |             0.24 |                   1.15 |                0.97 |              1.03 |                 72.68 |            1    |
| zQRF2sLK1vY      | A        |     54.42 |              |                |      0.88 |          0.37 |               2.52 |              2.86 |          0.64 |              0.37 |               0.7  |              0.09 |   -1.71 |              0.09 |  -7.47 |             0.14 |                   1.14 |                1    |              1.28 |                 75.71 |            1    |
| zQRF2sLK1vY      | B        |     29.16 |              |                |      1.09 |          2.57 |               2.75 |              2.52 |          0.03 |              0.12 |               1.27 |              0.24 |   -2.62 |              0.11 | -11.99 |             0.1  |                   1.35 |                0.92 |              0.6  |                260.86 |            1    |


## Medians by source

|                      |    CI |   URFall-adl |   URFall-fall |
|:---------------------|------:|-------------:|--------------:|
| drop_bl              |  0.93 |         0.65 |          2.25 |
| dur_10_90_s          |  0.87 |         0.33 |          0.87 |
| peak_down_v_bl_s     |  1.86 |         1.78 |          3.21 |
| peak_v_per_drop      |  1.94 |         2.75 |          1.7  |
| t_peak_frac          |  0.57 |         0    |          0.76 |
| peak_down_acc_g      |  0.29 |        -0.19 |          0.59 |
| peak_brake_acc_g     |  0.54 |         0.44 |          0.69 |
| end_speed_ratio      |  0.29 |         0.18 |          0.36 |
| sparc                | -2.08 |        -1.65 |         -1.67 |
| sparc_jitter_sd      |  0.1  |         0.03 |          0.02 |
| ldlj                 | -8.64 |        -7.27 |         -8.21 |
| ldlj_jitter_sd       |  0.15 |         0.15 |          0.04 |
| after_speed_med_bl_s |  0.7  |         0.53 |          0.41 |
| after_moving_frac    |  0.63 |         0.5  |          0.38 |
| after_max_level      |  0.74 |         1.18 |          0.38 |
| after_trunk_rot_deg  | 68.3  |        42.84 |        176.03 |
| after_tracked        |  1    |         0.83 |          0.78 |


## CI: floor vs low, contact vs solo (medians; n tiny)

|                      |       |   real_floor |   real_low |
|:---------------------|------:|-------------:|-----------:|
| drop_bl              |  0.93 |         1.01 |       0.79 |
| dur_10_90_s          |  0.93 |         0.27 |       0.4  |
| peak_down_v_bl_s     |  1.83 |         3.38 |       1.86 |
| peak_v_per_drop      |  1.86 |         3.35 |       2.37 |
| t_peak_frac          |  0.57 |         0.5  |       0.67 |
| peak_down_acc_g      |  0.32 |         0.25 |       0.2  |
| peak_brake_acc_g     |  0.53 |         0.91 |       0.59 |
| end_speed_ratio      |  0.29 |         0.19 |       0.49 |
| sparc                | -2.29 |        -1.57 |      -1.61 |
| sparc_jitter_sd      |  0.11 |         0.02 |       0.06 |
| ldlj                 | -8.7  |        -6.75 |      -7.31 |
| ldlj_jitter_sd       |  0.15 |         0.13 |       0.23 |
| after_speed_med_bl_s |  0.52 |         1.46 |       1.08 |
| after_moving_frac    |  0.52 |         0.9  |       0.87 |
| after_max_level      |  0.71 |         1.8  |       0.75 |
| after_trunk_rot_deg  | 68.3  |        47.1  |     169.81 |
| after_tracked        |  1    |         1    |       0.73 |



|                      |   False |
|:---------------------|--------:|
| drop_bl              |    1.01 |
| dur_10_90_s          |    0.27 |
| peak_down_v_bl_s     |    3.38 |
| peak_v_per_drop      |    3.35 |
| t_peak_frac          |    0.5  |
| peak_down_acc_g      |    0.25 |
| peak_brake_acc_g     |    0.91 |
| end_speed_ratio      |    0.19 |
| sparc                |   -1.57 |
| sparc_jitter_sd      |    0.02 |
| ldlj                 |   -6.75 |
| ldlj_jitter_sd       |    0.13 |
| after_speed_med_bl_s |    1.46 |
| after_moving_frac    |    0.9  |
| after_max_level      |    1.8  |
| after_trunk_rot_deg  |   47.1  |
| after_tracked        |    1    |


## CI vs UR Fall (Mann-Whitney, uncorrected)

| metric           | vs          |   ci_median |   other_median |   n_ci |   n_other |   p_mannwhitney |
|:-----------------|:------------|------------:|---------------:|-------:|----------:|----------------:|
| dur_10_90_s      | URFall-fall |       0.867 |          0.867 |     23 |         8 |           0.982 |
| dur_10_90_s      | URFall-adl  |       0.867 |          0.333 |     23 |         3 |           0.296 |
| peak_down_v_bl_s | URFall-fall |       1.865 |          3.215 |     23 |         8 |           0.002 |
| peak_down_v_bl_s | URFall-adl  |       1.865 |          1.784 |     23 |         3 |           1     |
| peak_brake_acc_g | URFall-fall |       0.545 |          0.693 |     23 |         6 |           0.511 |
| peak_v_per_drop  | URFall-fall |       1.937 |          1.702 |     23 |         8 |           0.158 |
| peak_v_per_drop  | URFall-adl  |       1.937 |          2.753 |     23 |         3 |           0.541 |
| end_speed_ratio  | URFall-fall |       0.293 |          0.355 |     23 |         8 |           0.464 |
| end_speed_ratio  | URFall-adl  |       0.293 |          0.175 |     23 |         3 |           0.312 |
| sparc            | URFall-fall |      -2.08  |         -1.671 |     23 |         8 |           0.172 |
| sparc            | URFall-adl  |      -2.08  |         -1.649 |     23 |         3 |           0.594 |
| ldlj             | URFall-fall |      -8.64  |         -8.209 |     23 |         8 |           0.947 |
| ldlj             | URFall-adl  |      -8.64  |         -7.27  |     23 |         3 |           0.395 |
| peak_down_acc_g  | URFall-fall |       0.291 |          0.586 |     23 |         8 |           0.005 |
| peak_down_acc_g  | URFall-adl  |       0.291 |         -0.193 |     23 |         3 |           0.395 |
| drop_bl          | URFall-fall |       0.932 |          2.247 |     23 |         8 |           0     |
| drop_bl          | URFall-adl  |       0.932 |          0.648 |     23 |         3 |           0.395 |
| t_peak_frac      | URFall-fall |       0.571 |          0.76  |     23 |         8 |           0.136 |
| t_peak_frac      | URFall-adl  |       0.571 |          0     |     23 |         3 |           0.333 |
| after_max_level  | URFall-fall |       0.737 |          0.375 |     23 |         8 |           0.003 |
| after_max_level  | URFall-adl  |       0.737 |          1.18  |     23 |         3 |           0.594 |


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