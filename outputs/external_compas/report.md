# Lead/lag on CoMPAS3D: 9 pairs, 71 sequences (leader known)

lead_index > 0 means the leader's signal precedes the follower's. Pair = mean over its sequences; tests across pairs (sign test, one-sided Wilcoxon).


## mocap


Per pair (speed):

|   pair | level        |   lead_index |   peak_lag_s |   peak_r |
|-------:|:-------------|-------------:|-------------:|---------:|
|      1 | beginner     |       -0.149 |       -0.096 |    0.213 |
|      2 | intermediate |        0.06  |       -0.704 |    0.27  |
|      3 | beginner     |        0.023 |       -0.779 |    0.236 |
|      4 | intermediate |        0.081 |       -0.008 |    0.542 |
|      5 | professional |       -0.005 |        0.092 |    0.343 |
|      6 | intermediate |        0.123 |        0.808 |    0.337 |
|      7 | professional |        0.004 |        0.014 |    0.33  |
|      8 | beginner     |        0.011 |        0.254 |    0.362 |
|      9 | professional |        0.032 |        0.492 |    0.266 |


Per pair (bounce):

|   pair | level        |   lead_index |   peak_lag_s |   peak_r |
|-------:|:-------------|-------------:|-------------:|---------:|
|      1 | beginner     |        0.176 |        0.117 |    0.246 |
|      2 | intermediate |       -0.22  |        0.454 |   -0.269 |
|      3 | beginner     |       -0.097 |       -0.025 |    0.484 |
|      4 | intermediate |       -0.179 |       -0.033 |    0.095 |
|      5 | professional |       -0.007 |       -0.071 |    0.306 |
|      6 | intermediate |       -0.078 |       -0.079 |    0.252 |
|      7 | professional |        0.013 |        0.133 |    0.171 |
|      8 | beginner     |       -0.059 |       -0.017 |    0.444 |
|      9 | professional |        0.12  |       -0.017 |    0.278 |

| signal   | pairs_leader_first   | sequences_leader_first   |   median_lead_index |   median_peak_lag_s |   sign_test_p |   wilcoxon_p |
|:---------|:---------------------|:-------------------------|--------------------:|--------------------:|--------------:|-------------:|
| speed    | 7/9                  | 46/71                    |              0.0234 |              0.0143 |        0.0898 |       0.1016 |
| bounce   | 3/9                  | 22/71                    |             -0.0595 |             -0.0167 |        0.9102 |       0.8203 |

## 2-D projection + jitter 0.005 bl

| signal   | pairs_leader_first   | sequences_leader_first   |   median_lead_index |   median_peak_lag_s |   sign_test_p |   wilcoxon_p |
|:---------|:---------------------|:-------------------------|--------------------:|--------------------:|--------------:|-------------:|
| speed    | 5/9                  | 44/71                    |              0.0082 |              0.0542 |        0.5    |       0.248  |
| bounce   | 3/9                  | 22/71                    |             -0.0548 |              0.0167 |        0.9102 |       0.8203 |

## 2-D projection + jitter 0.02 bl

| signal   | pairs_leader_first   | sequences_leader_first   |   median_lead_index |   median_peak_lag_s |   sign_test_p |   wilcoxon_p |
|:---------|:---------------------|:-------------------------|--------------------:|--------------------:|--------------:|-------------:|
| speed    | 5/9                  | 46/71                    |              0.007  |              0.1083 |        0.5    |       0.248  |
| bounce   | 3/9                  | 23/71                    |             -0.0261 |              0.0167 |        0.9102 |       0.8203 |