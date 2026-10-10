# State grammar of 10 CI duets (32.0 min)

States per frame (see docstring); detection gaps <= 1 s bridged; episodes >= 0.3 s.

## Per duet

| video            |   minutes |   episodes |   share_apart |   dwell_apart_s |   share_near |   dwell_near_s |   share_contact |   dwell_contact_s |   share_share |   dwell_share_s |   share_floor |   dwell_floor_s |   next_state_entropy_bits |   transitions_per_min |
|:-----------------|----------:|-----------:|--------------:|----------------:|-------------:|---------------:|----------------:|------------------:|--------------:|----------------:|--------------:|----------------:|--------------------------:|----------------------:|
| zQRF2sLK1vY      |      0.88 |         26 |          0.09 |            1.33 |         0.1  |           0.75 |            0.5  |              0.75 |          0.04 |            0.43 |          0.28 |            1.43 |                      1.46 |                 29.68 |
| kxztAr2tQmE_full |      0.95 |         25 |          0.06 |            3.4  |         0.12 |           0.8  |            0.62 |              2.2  |          0.03 |            0.53 |          0.17 |            1.13 |                      1.3  |                 26.25 |
| swmrAJkYrlY_full |      3    |         56 |          0.29 |            4.13 |         0.14 |           0.8  |            0.56 |              2.33 |          0.01 |            0.33 |          0.01 |            0.4  |                      0.98 |                 18.66 |
| hJQgFDsAms4_full |      5.72 |         94 |          0.03 |            1.3  |         0.08 |           1.2  |            0.59 |              2.33 |          0.02 |            1.03 |          0.29 |            1.47 |                      1.15 |                 16.42 |
| iOEZ3i9rgYM_full |      3.22 |         25 |          0    |          nan    |         0.05 |           1.2  |            0.8  |              9.33 |          0.02 |            0.37 |          0.13 |            4.33 |                      0.97 |                  7.76 |
| dGPRMNAECKM_full |      2.38 |         54 |          0.02 |            0.4  |         0.11 |           0.8  |            0.61 |              1.87 |          0.03 |            0.33 |          0.23 |            2.3  |                      1.29 |                 22.68 |
| Rc9vIJt00vs_full |      3.87 |         93 |          0.03 |            0.9  |         0.13 |           0.8  |            0.62 |              4.07 |          0.05 |            0.8  |          0.17 |            1.13 |                      1.59 |                 24.04 |
| vinlwkaIW4c_full |      3.15 |         94 |          0.08 |            1.27 |         0.17 |           0.8  |            0.56 |              1.23 |          0.03 |            0.37 |          0.17 |            1.33 |                      1.45 |                 29.87 |
| kMkJpfUGZz8_full |      2.92 |         54 |          0.22 |            3.27 |         0.06 |           0.7  |            0.43 |              2.97 |          0.04 |            0.8  |          0.24 |            0.83 |                      1.42 |                 18.49 |
| uS1JQ-LY8Fs_full |      5.89 |         98 |          0.28 |            2.4  |         0.15 |           0.93 |            0.45 |              3.5  |          0    |            0.33 |          0.11 |            3.23 |                      1.01 |                 16.64 |


## Pooled transition probabilities (row = current state, 609 transitions)

|         |   apart |   near |   contact |   share |   floor |
|:--------|--------:|-------:|----------:|--------:|--------:|
| apart   |   0     |  0.603 |     0.176 |   0     |   0.221 |
| near    |   0.223 |  0     |     0.662 |   0.032 |   0.083 |
| contact |   0.091 |  0.435 |     0     |   0.11  |   0.364 |
| share   |   0     |  0.091 |     0.6   |   0     |   0.309 |
| floor   |   0.125 |  0.175 |     0.475 |   0.225 |   0     |


Caveats: 'contact' and 'share' are 2-D detectors validated by eye (AUDIT 38-40); releases need SEP_BL separation (hand check, AUDIT 43); A/B identity does not matter here (states are symmetric).