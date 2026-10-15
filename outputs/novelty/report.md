# Idea C: predictability and novelty of the improvisation

Vocabulary refitted exactly as describe_duets.py: max |usage difference| vs outputs/describe/vocabulary_usage.csv = nan.

H0/H1/H2 = entropy of the next symbol given 0/1/2 previous symbols (bits, Miller-Madow), collapsed sequences. `_shuffle` / `_markov1` = surrogate means (same length and frequencies / same first-order transitions). `nov3` = share of 3-grams in the second half never seen before.


## words_CI

| set      | unit             |   n_symbols |   n_distinct |    H0 |    H1 |   H1_shuffle |   H1_shuffle_p_low |    H2 |   H2_markov1 |   H2_markov1_p_low |   nov2 |   nov2_markov1 |   nov3 |   nov3_shuffle |   nov3_markov1 |   nov3_markov1_p_low |   nov3_markov1_p_high |
|:---------|:-----------------|------------:|-------------:|------:|------:|-------------:|-------------------:|------:|-------------:|-------------------:|-------:|---------------:|-------:|---------------:|---------------:|---------------------:|----------------------:|
| words_CI | Rc9vIJt00vs_full |         142 |           10 | 3.105 | 2.08  |        2.656 |              0.003 | 1.2   |        1.174 |              0.568 |  0.302 |          0.245 |  0.762 |          0.939 |          0.769 |                0.545 |                 0.661 |
| words_CI | dGPRMNAECKM_full |         133 |            9 | 3.062 | 2.288 |        2.656 |              0.003 | 1.129 |        1.201 |              0.233 |  0.333 |          0.229 |  0.625 |          0.916 |          0.707 |                0.266 |                 0.86  |
| words_CI | hJQgFDsAms4_full |         265 |           10 | 3.173 | 2.322 |        2.898 |              0.003 | 1.473 |        1.546 |              0.213 |  0.145 |          0.136 |  0.775 |          0.905 |          0.707 |                0.85  |                 0.233 |
| words_CI | iOEZ3i9rgYM_full |         220 |            9 | 2.812 | 1.988 |        2.471 |              0.003 | 1.524 |        1.542 |              0.429 |  0.096 |          0.093 |  0.556 |          0.706 |          0.47  |                0.894 |                 0.163 |
| words_CI | kMkJpfUGZz8_full |         166 |           10 | 3.127 | 2.096 |        2.753 |              0.003 | 1.375 |        1.384 |              0.482 |  0.231 |          0.154 |  0.614 |          0.874 |          0.566 |                0.781 |                 0.299 |
| words_CI | kxztAr2tQmE_full |          68 |            9 | 2.903 | 1.738 |        2.215 |              0.003 | 1.028 |        1.002 |              0.551 |  0.36  |          0.281 |  1     |          0.922 |          0.766 |                1     |                 0.027 |
| words_CI | swmrAJkYrlY_full |         192 |           10 | 2.801 | 1.928 |        2.402 |              0.003 | 1.152 |        1.342 |              0.04  |  0.175 |          0.119 |  0.5   |          0.81  |          0.59  |                0.216 |                 0.86  |
| words_CI | uS1JQ-LY8Fs_full |         291 |            9 | 2.497 | 1.791 |        2.105 |              0.003 | 1.39  |        1.524 |              0.063 |  0.069 |          0.051 |  0.276 |          0.369 |          0.245 |                0.738 |                 0.332 |
| words_CI | vinlwkaIW4c_full |         208 |           10 | 3.115 | 2.376 |        2.775 |              0.003 | 1.381 |        1.509 |              0.083 |  0.143 |          0.14  |  0.596 |          0.851 |          0.652 |                0.236 |                 0.811 |
| words_CI | zQRF2sLK1vY      |          79 |           10 | 3.253 | 2.395 |        2.544 |              0.11  | 0.886 |        0.983 |              0.206 |  0.452 |          0.318 |  1     |          0.954 |          0.807 |                1     |                 0.023 |

## states_CI

| set       | unit             |   n_symbols |   n_distinct |    H0 |    H1 |   H1_shuffle |   H1_shuffle_p_low |    H2 |   H2_markov1 |   H2_markov1_p_low |   nov2 |   nov2_markov1 |   nov3 |   nov3_shuffle |   nov3_markov1 |   nov3_markov1_p_low |   nov3_markov1_p_high |
|:----------|:-----------------|------------:|-------------:|------:|------:|-------------:|-------------------:|------:|-------------:|-------------------:|-------:|---------------:|-------:|---------------:|---------------:|---------------------:|----------------------:|
| states_CI | zQRF2sLK1vY      |          26 |            5 | 2.418 | 1.592 |        1.836 |              0.073 | 0.756 |        0.778 |              0.452 |  0.273 |          0.269 |  0.444 |          0.896 |          0.623 |                0.262 |                 0.89  |
| states_CI | kxztAr2tQmE_full |          22 |            5 | 2.155 | 0.935 |        1.402 |              0.003 | 0.716 |        0.633 |              0.681 |  0.333 |          0.154 |  0.714 |          0.768 |          0.418 |                0.967 |                 0.133 |
| states_CI | swmrAJkYrlY_full |          65 |            5 | 2.119 | 1.337 |        1.694 |              0.003 | 0.876 |        1.088 |              0.027 |  0.069 |          0.042 |  0.25  |          0.491 |          0.26  |                0.535 |                 0.625 |
| states_CI | hJQgFDsAms4_full |          86 |            5 | 2.02  | 1.466 |        1.554 |              0.169 | 0.91  |        1.172 |              0.017 |  0.034 |          0.087 |  0.214 |          0.564 |          0.478 |                0.043 |                 0.987 |
| states_CI | iOEZ3i9rgYM_full |          25 |            4 | 1.678 | 0.907 |        1.137 |              0.309 | 0.415 |        0.518 |              0.322 |  0.1   |          0.161 |  0.5   |          0.681 |          0.427 |                0.728 |                 0.495 |
| states_CI | dGPRMNAECKM_full |          49 |            4 | 1.958 | 1.38  |        1.483 |              0.15  | 1.127 |        1.112 |              0.538 |  0.048 |          0.06  |  0.312 |          0.499 |          0.4   |                0.336 |                 0.841 |
| states_CI | Rc9vIJt00vs_full |         128 |            5 | 2.239 | 1.656 |        1.859 |              0.003 | 1.469 |        1.454 |              0.568 |  0.057 |          0.037 |  0.375 |          0.41  |          0.295 |                0.894 |                 0.179 |
| states_CI | vinlwkaIW4c_full |          99 |            5 | 2.196 | 1.574 |        1.786 |              0.003 | 1.227 |        1.343 |              0.159 |  0.021 |          0.031 |  0.205 |          0.331 |          0.213 |                0.522 |                 0.654 |
| states_CI | kMkJpfUGZz8_full |          61 |            5 | 2.347 | 1.537 |        1.979 |              0.003 | 1.005 |        1.159 |              0.146 |  0.037 |          0.078 |  0.348 |          0.676 |          0.382 |                0.458 |                 0.701 |
| states_CI | uS1JQ-LY8Fs_full |          93 |            4 | 1.803 | 1.053 |        1.597 |              0.003 | 0.903 |        0.921 |              0.435 |  0.045 |          0.031 |  0.075 |          0.229 |          0.096 |                0.465 |                 0.674 |
| states_CI | YR2QCf5cL6Q_full |          87 |            5 | 2.049 | 1.466 |        1.586 |              0.04  | 1.196 |        1.222 |              0.405 |  0.088 |          0.059 |  0.409 |          0.462 |          0.352 |                0.771 |                 0.392 |

## words_salsa_CIvocab

| set                 | unit                    |   n_symbols |   n_distinct |    H0 |    H1 |   H1_shuffle |   H1_shuffle_p_low |    H2 |   H2_markov1 |   H2_markov1_p_low |   nov2 |   nov2_markov1 |   nov3 |   nov3_shuffle |   nov3_markov1 |   nov3_markov1_p_low |   nov3_markov1_p_high |
|:--------------------|:------------------------|------------:|-------------:|------:|------:|-------------:|-------------------:|------:|-------------:|-------------------:|-------:|---------------:|-------:|---------------:|---------------:|---------------------:|----------------------:|
| words_salsa_CIvocab | salsa_Pair1_song1_take1 |          51 |            4 | 1.987 | 1.408 |        1.518 |              0.066 | 1.105 |        1.042 |              0.615 |  0.143 |          0.094 |  0.588 |          0.508 |          0.379 |                0.967 |                 0.076 |
| words_salsa_CIvocab | salsa_Pair2_song2_take1 |          84 |            5 | 2.095 | 1.605 |        1.643 |              0.302 | 1.046 |        1.116 |              0.326 |  0.125 |          0.117 |  0.478 |          0.506 |          0.406 |                0.764 |                 0.359 |
| words_salsa_CIvocab | salsa_Pair5_song2_take1 |          80 |            5 | 1.877 | 1.232 |        1.547 |              0.04  | 1.044 |        0.943 |              0.694 |  0.138 |          0.14  |  0.438 |          0.565 |          0.402 |                0.701 |                 0.472 |

## words_salsa_ownvocab

| set                  | unit                    |   n_symbols |   n_distinct |    H0 |    H1 |   H1_shuffle |   H1_shuffle_p_low |    H2 |   H2_markov1 |   H2_markov1_p_low |   nov2 |   nov2_markov1 |   nov3 |   nov3_shuffle |   nov3_markov1 |   nov3_markov1_p_low |   nov3_markov1_p_high |
|:---------------------|:------------------------|------------:|-------------:|------:|------:|-------------:|-------------------:|------:|-------------:|-------------------:|-------:|---------------:|-------:|---------------:|---------------:|---------------------:|----------------------:|
| words_salsa_ownvocab | salsa_Pair1_song1_take1 |          37 |            9 | 2.791 | 1.574 |        1.747 |              0.163 | 0.223 |        0.697 |              0.007 |  0.643 |          0.324 |  0.625 |          0.923 |          0.717 |                0.412 |                 0.844 |
| words_salsa_ownvocab | salsa_Pair2_song2_take1 |         102 |           10 | 3.303 | 2.2   |        2.754 |              0.003 | 1.039 |        1.159 |              0.133 |  0.39  |          0.256 |  0.828 |          0.951 |          0.717 |                0.934 |                 0.15  |
| words_salsa_ownvocab | salsa_Pair5_song2_take1 |          86 |           10 | 3.03  | 2.152 |        2.382 |              0.02  | 1.164 |        1.113 |              0.648 |  0.419 |          0.282 |  0.842 |          0.915 |          0.759 |                0.877 |                 0.316 |

## states_salsa

| set          | unit                    |   n_symbols |   n_distinct |   H0 |   H1 |   H1_shuffle |   H1_shuffle_p_low |   H2 |   H2_markov1 |   H2_markov1_p_low |   nov2 |   nov2_markov1 |   nov3 |   nov3_shuffle |   nov3_markov1 |   nov3_markov1_p_low |   nov3_markov1_p_high |
|:-------------|:------------------------|------------:|-------------:|-----:|-----:|-------------:|-------------------:|-----:|-------------:|-------------------:|-------:|---------------:|-------:|---------------:|---------------:|---------------------:|----------------------:|
| states_salsa | salsa_Pair2_song2_take1 |           7 |            2 |  nan |  nan |          nan |                nan |  nan |          nan |                nan |      0 |              0 |    0.5 |          0.572 |            0.5 |                    1 |                     1 |


## Summary (median over units; counts of units with surrogate p < 0.05)

| set                  |   units |   n_symbols |      H0 |      H1 |   gain_H1_vs_shuffle |   H1_sig_lower_than_shuffle |   gain_H2_vs_markov1 |   H2_sig_lower_than_markov1 |   nov3 |   nov3_minus_markov1 |   nov3_sig_low |   nov3_sig_high |
|:---------------------|--------:|------------:|--------:|--------:|---------------------:|----------------------------:|---------------------:|----------------------------:|-------:|---------------------:|---------------:|----------------:|
| states_CI            |      11 |          65 |   2.119 |   1.466 |                0.23  |                           7 |                0.026 |                           2 |  0.348 |               -0.01  |              1 |               0 |
| states_salsa         |       1 |           7 | nan     | nan     |              nan     |                           0 |              nan     |                           0 |  0.5   |                0     |              0 |               0 |
| words_CI             |      10 |         179 |   3.083 |   2.088 |                0.476 |                           9 |                0.072 |                           1 |  0.619 |                0.039 |              0 |               2 |
| words_CI_seg         |      14 |          86 |   2.874 |   1.901 |                0.429 |                          14 |               -0     |                           0 |  0.793 |                0.063 |              0 |               2 |
| words_salsa_CIvocab  |       3 |          80 |   1.987 |   1.408 |                0.11  |                           1 |               -0.063 |                           0 |  0.478 |                0.072 |              0 |               0 |
| words_salsa_ownvocab |       3 |          86 |   3.03  |   2.152 |                0.23  |                           2 |                0.12  |                           1 |  0.828 |                0.083 |              0 |               0 |


## CI vs salsa at equal length (80 collapsed word symbols per segment; CI segments from the same duet are not independent)

| measure            | contrast                                       |   ci_median |   salsa_median |   n_ci |   n_salsa |   mannwhitney_p |
|:-------------------|:-----------------------------------------------|------------:|---------------:|-------:|----------:|----------------:|
| H0                 | CI 60-s-equivalent segments vs salsa CI-vocab  |      2.8744 |         1.9872 |     14 |         3 |          0.0029 |
| H0                 | CI 60-s-equivalent segments vs salsa own-vocab |      2.8744 |         3.0299 |     14 |         3 |          0.4324 |
| H1                 | CI 60-s-equivalent segments vs salsa CI-vocab  |      1.9008 |         1.4085 |     14 |         3 |          0.0118 |
| H1                 | CI 60-s-equivalent segments vs salsa own-vocab |      1.9008 |         2.1521 |     14 |         3 |          0.3618 |
| gain_H1_vs_shuffle | CI 60-s-equivalent segments vs salsa CI-vocab  |      0.4287 |         0.1097 |     14 |         3 |          0.0471 |
| gain_H1_vs_shuffle | CI 60-s-equivalent segments vs salsa own-vocab |      0.4287 |         0.2301 |     14 |         3 |          0.6765 |
| gain_H2_vs_markov1 | CI 60-s-equivalent segments vs salsa CI-vocab  |     -0.0004 |        -0.0633 |     14 |         3 |          0.3    |
| gain_H2_vs_markov1 | CI 60-s-equivalent segments vs salsa own-vocab |     -0.0004 |         0.1201 |     14 |         3 |          0.4324 |
| nov3               | CI 60-s-equivalent segments vs salsa CI-vocab  |      0.7929 |         0.4783 |     14 |         3 |          0.0912 |
| nov3               | CI 60-s-equivalent segments vs salsa own-vocab |      0.7929 |         0.8276 |     14 |         3 |          1      |
| nov3_minus_markov1 | CI 60-s-equivalent segments vs salsa CI-vocab  |      0.0628 |         0.072  |     14 |         3 |          0.5912 |
| nov3_minus_markov1 | CI 60-s-equivalent segments vs salsa own-vocab |      0.0628 |         0.0833 |     14 |         3 |          0.7676 |


## Smooth-signal control (CI words, runs >= 8 windows)

Gain = H1(shuffle) - H1. `gain_phase_mean` = the same gain for multivariate phase-randomised features re-quantised with the same k-means (100 surrogates); `gain_phase_p_high` = share of surrogates with a gain at least as large as observed.

| video            |   n_symbols |    H1 |   H1_shuffle |   gain_obs |   gain_phase_mean |   gain_phase_p_high |   H1_phase_mean |
|:-----------------|------------:|------:|-------------:|-----------:|------------------:|--------------------:|----------------:|
| Rc9vIJt00vs_full |          92 | 1.909 |        2.547 |      0.638 |             0.609 |               0.416 |           1.971 |
| dGPRMNAECKM_full |         113 | 2.189 |        2.564 |      0.375 |             0.494 |               0.842 |           2.115 |
| hJQgFDsAms4_full |         202 | 2.368 |        2.846 |      0.478 |             0.583 |               0.891 |           2.268 |
| iOEZ3i9rgYM_full |         196 | 1.982 |        2.434 |      0.452 |             0.437 |               0.436 |           2.097 |
| kMkJpfUGZz8_full |         138 | 2.084 |        2.648 |      0.564 |             0.462 |               0.188 |           2.177 |
| kxztAr2tQmE_full |          61 | 1.806 |        2.093 |      0.287 |             0.174 |               0.228 |           1.88  |
| swmrAJkYrlY_full |         157 | 1.81  |        2.263 |      0.453 |             0.271 |               0.03  |           2.022 |
| uS1JQ-LY8Fs_full |         270 | 1.779 |        2.079 |      0.3   |             0.403 |               0.96  |           1.713 |
| vinlwkaIW4c_full |         166 | 2.29  |        2.71  |      0.42  |             0.228 |               0.02  |           2.497 |
| zQRF2sLK1vY      |          74 | 2.46  |        2.487 |      0.028 |             0.084 |               0.624 |           2.336 |


Salsa word usage with the CI vocabulary (alphabet collapse check):

| video                   |     1 |     4 |     5 |     7 |     8 |
|:------------------------|------:|------:|------:|------:|------:|
| salsa_Pair1_song1_take1 | 0.162 | 0.176 | 0.191 | 0.471 | 0     |
| salsa_Pair2_song2_take1 | 0.164 | 0.241 | 0.067 | 0.472 | 0.056 |
| salsa_Pair5_song2_take1 | 0.065 | 0.33  | 0.032 | 0.551 | 0.022 |


## Held-out (leave-one-duet-out) cross-entropy, bits per symbol, CI

| video            |   bits_order0 |   n |   bits_order1 |   bits_order2 | set       |
|:-----------------|--------------:|----:|--------------:|--------------:|:----------|
| Rc9vIJt00vs_full |         3.124 |  73 |         2.379 |         2.63  | words_CI  |
| dGPRMNAECKM_full |         3.257 |  81 |         2.836 |         3.043 | words_CI  |
| hJQgFDsAms4_full |         3.261 | 145 |         2.868 |         2.97  | words_CI  |
| iOEZ3i9rgYM_full |         2.998 | 150 |         2.35  |         2.433 | words_CI  |
| kMkJpfUGZz8_full |         3.18  | 113 |         2.665 |         2.91  | words_CI  |
| kxztAr2tQmE_full |         2.945 |  44 |         2.581 |         2.92  | words_CI  |
| swmrAJkYrlY_full |         3.143 | 110 |         2.646 |         2.612 | words_CI  |
| uS1JQ-LY8Fs_full |         2.969 | 214 |         2.188 |         2.281 | words_CI  |
| vinlwkaIW4c_full |         3.232 | 134 |         2.759 |         2.745 | words_CI  |
| zQRF2sLK1vY      |         3.339 |  57 |         3.034 |         3.31  | words_CI  |
| zQRF2sLK1vY      |         2.407 |  22 |         1.717 |         1.902 | states_CI |
| kxztAr2tQmE_full |         2.077 |  18 |         1.423 |         1.168 | states_CI |
| swmrAJkYrlY_full |         2.273 |  55 |         1.688 |         1.767 | states_CI |
| hJQgFDsAms4_full |         2.176 |  56 |         1.635 |         1.345 | states_CI |
| iOEZ3i9rgYM_full |         2.121 |  17 |         1.381 |         1.099 | states_CI |
| dGPRMNAECKM_full |         2.071 |  39 |         1.48  |         1.584 | states_CI |
| Rc9vIJt00vs_full |         2.236 | 102 |         1.729 |         1.701 | states_CI |
| vinlwkaIW4c_full |         2.192 |  93 |         1.58  |         1.616 | states_CI |
| kMkJpfUGZz8_full |         2.327 |  53 |         1.611 |         1.847 | states_CI |
| uS1JQ-LY8Fs_full |         2.571 |  85 |         1.55  |         1.456 | states_CI |
| YR2QCf5cL6Q_full |         2.163 |  63 |         1.495 |         1.493 | states_CI |


Median held-out gain order0 -> order1: words 0.485 bits, states 0.654 bits; order1 -> order2: words -0.154, states 0.002.