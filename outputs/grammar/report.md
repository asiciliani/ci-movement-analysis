# State grammar of 11 CI duets (39.8 min)

States per frame (see docstring); detection gaps <= 1 s bridged; episodes >= 0.3 s.

## Per duet

| video            |   minutes |   episodes |   share_apart |   dwell_apart_s |   share_near |   dwell_near_s |   share_contact |   dwell_contact_s |   share_share |   dwell_share_s |   share_floor |   dwell_floor_s |   next_state_entropy_bits |   transitions_per_min |
|:-----------------|----------:|-----------:|--------------:|----------------:|-------------:|---------------:|----------------:|------------------:|--------------:|----------------:|--------------:|----------------:|--------------------------:|----------------------:|
| zQRF2sLK1vY      |      0.9  |         26 |          0.12 |            1.27 |         0.08 |           0.67 |            0.36 |              0.73 |          0.11 |            1.27 |          0.33 |            1.94 |                      1.32 |                 28.88 |
| kxztAr2tQmE_full |      1.08 |         22 |          0.08 |            2.47 |         0.04 |           0.53 |            0.66 |              0.83 |          0.02 |            0.53 |          0.19 |            2.27 |                      0.84 |                 20.45 |
| swmrAJkYrlY_full |      2.5  |         65 |          0.37 |            3    |         0.11 |           0.8  |            0.44 |              1.93 |          0.05 |            1    |          0.03 |            0.93 |                      1.27 |                 26.02 |
| hJQgFDsAms4_full |      7.29 |        118 |          0.02 |            1.07 |         0.06 |           0.87 |            0.53 |              1.33 |          0.05 |            0.8  |          0.34 |            1.27 |                      1.37 |                 16.2  |
| iOEZ3i9rgYM_full |      3.45 |         31 |          0    |          nan    |         0.03 |           1.07 |            0.76 |              2.83 |          0.09 |            1.2  |          0.12 |            1.4  |                      0.85 |                  8.98 |
| dGPRMNAECKM_full |      2.77 |         54 |          0.01 |            1.27 |         0.08 |           1.13 |            0.61 |              2.1  |          0.07 |            0.67 |          0.23 |            1.33 |                      1.35 |                 19.53 |
| Rc9vIJt00vs_full |      4.96 |        136 |          0.06 |            1.13 |         0.09 |           0.63 |            0.54 |              1.6  |          0.11 |            0.8  |          0.19 |            0.93 |                      1.58 |                 27.41 |
| vinlwkaIW4c_full |      3.55 |        100 |          0.08 |            1.73 |         0.11 |           0.67 |            0.54 |              1.9  |          0.08 |            1.07 |          0.18 |            1.33 |                      1.49 |                 28.16 |
| kMkJpfUGZz8_full |      3.13 |         62 |          0.22 |            3.2  |         0.06 |           0.67 |            0.38 |              3.17 |          0.07 |            1    |          0.28 |            1.13 |                      1.41 |                 19.81 |
| uS1JQ-LY8Fs_full |      5.73 |         92 |          0.32 |            2.67 |         0.12 |           0.87 |            0.51 |              4.43 |          0    |          nan    |          0.05 |            1.7  |                      1.03 |                 16.04 |
| YR2QCf5cL6Q_full |      4.42 |        112 |          0.02 |            1.57 |         0.06 |           0.87 |            0.44 |              1.83 |          0.2  |            1.5  |          0.29 |            1.07 |                      1.33 |                 25.32 |


## Pooled transition probabilities (row = current state, 807 transitions)

|         |   apart |   near |   contact |   share |   floor |
|:--------|--------:|-------:|----------:|--------:|--------:|
| apart   |   0     |  0.641 |     0.205 |   0     |   0.154 |
| near    |   0.263 |  0     |     0.615 |   0.013 |   0.109 |
| contact |   0.084 |  0.297 |     0     |   0.289 |   0.33  |
| share   |   0     |  0.023 |     0.592 |   0     |   0.385 |
| floor   |   0.1   |  0.124 |     0.488 |   0.288 |   0     |


Caveats: 'contact' and 'share' are 2-D detectors validated by eye (AUDIT 38-40); releases need SEP_BL separation (hand check, AUDIT 43); A/B identity does not matter here (states are symmetric).