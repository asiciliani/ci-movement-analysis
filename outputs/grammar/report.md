# State grammar of 10 CI duets (32.0 min)

States per frame (see docstring); detection gaps <= 1 s bridged; episodes >= 0.3 s.

## Per duet

| video            |   minutes |   episodes |   share_apart |   dwell_apart_s |   share_near |   dwell_near_s |   share_contact |   dwell_contact_s |   share_share |   dwell_share_s |   share_floor |   dwell_floor_s |   next_state_entropy_bits |   transitions_per_min |
|:-----------------|----------:|-----------:|--------------:|----------------:|-------------:|---------------:|----------------:|------------------:|--------------:|----------------:|--------------:|----------------:|--------------------------:|----------------------:|
| zQRF2sLK1vY      |      0.88 |         28 |          0.09 |            1.33 |         0.18 |           0.67 |            0.42 |              0.77 |          0.04 |            0.43 |          0.28 |            1.43 |                      1.42 |                 31.97 |
| kxztAr2tQmE_full |      0.95 |         38 |          0.06 |            3.4  |         0.24 |           0.8  |            0.5  |              0.53 |          0.03 |            0.53 |          0.17 |            1.13 |                      0.95 |                 39.91 |
| swmrAJkYrlY_full |      3    |         82 |          0.29 |            4.13 |         0.24 |           0.73 |            0.46 |              1.8  |          0.01 |            0.6  |          0.01 |            0.4  |                      0.72 |                 27.32 |
| hJQgFDsAms4_full |      5.72 |        158 |          0.03 |            1.3  |         0.32 |           1.13 |            0.35 |              1.07 |          0.02 |            1.03 |          0.29 |            1.47 |                      1.12 |                 27.6  |
| iOEZ3i9rgYM_full |      3.22 |         62 |          0    |          nan    |         0.19 |           1.07 |            0.66 |              2.3  |          0.02 |            0.37 |          0.13 |            4.33 |                      0.77 |                 19.25 |
| dGPRMNAECKM_full |      2.38 |         84 |          0.02 |            0.4  |         0.25 |           0.67 |            0.47 |              1.47 |          0.03 |            0.33 |          0.23 |            2.47 |                      1.14 |                 35.28 |
| Rc9vIJt00vs_full |      3.87 |        142 |          0.03 |            0.9  |         0.36 |           1.07 |            0.39 |              1.17 |          0.04 |            0.8  |          0.17 |            1.07 |                      1.23 |                 36.7  |
| vinlwkaIW4c_full |      3.15 |        129 |          0.08 |            1.27 |         0.32 |           1    |            0.4  |              1.13 |          0.03 |            0.4  |          0.17 |            1.33 |                      1.25 |                 41    |
| kMkJpfUGZz8_full |      2.92 |         69 |          0.22 |            3.27 |         0.11 |           0.67 |            0.38 |              1.53 |          0.03 |            0.8  |          0.24 |            0.83 |                      1.45 |                 23.62 |
| uS1JQ-LY8Fs_full |      5.89 |        146 |          0.28 |            2.4  |         0.23 |           0.8  |            0.37 |              1.53 |          0    |            0.33 |          0.11 |            3.23 |                      0.84 |                 24.78 |


## Pooled transition probabilities (row = current state, 928 transitions)

|         |   apart |   near |   contact |   share |   floor |
|:--------|--------:|-------:|----------:|--------:|--------:|
| apart   |   0     |  0.603 |     0.176 |   0     |   0.221 |
| near    |   0.097 |  0     |     0.735 |   0.036 |   0.131 |
| contact |   0.058 |  0.781 |     0     |   0.036 |   0.125 |
| share   |   0     |  0.212 |     0.442 |   0     |   0.346 |
| floor   |   0.125 |  0.425 |     0.225 |   0.225 |   0     |


Caveats: 'contact' and 'share' are 2-D detectors validated by eye (AUDIT 38-40); A/B identity does not matter here (states are symmetric).