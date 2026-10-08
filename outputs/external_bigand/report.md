# Coupling method on Bigand et al. (2024) mocap: 35 dyads, 1120 trials

Statistic: peak |r| within ±2 s at 25 Hz. Contrasts are per-dyad means, Wilcoxon (one-sided) across dyads.


## 3-D mocap (ground truth)

| signal   | contrast                                                 |   n_dyads |   mean_diff |   sd_diff |   dyads_positive |   wilcoxon_p |
|:---------|:---------------------------------------------------------|----------:|------------:|----------:|-----------------:|-------------:|
| speed    | PARTNER: vision vs curtain, different music              |        35 |      0.0344 |    0.0452 |               27 |       0      |
| speed    | partner with shared music: vision vs curtain, same music |        35 |      0.0169 |    0.0426 |               25 |       0.0035 |
| speed    | MUSIC: same vs different music, curtain                  |        35 |      0.0415 |    0.047  |               31 |       0      |
| bounce   | PARTNER: vision vs curtain, different music              |        35 |      0.0297 |    0.0428 |               28 |       0      |
| bounce   | partner with shared music: vision vs curtain, same music |        35 |      0.0586 |    0.0746 |               30 |       0      |
| bounce   | MUSIC: same vs different music, curtain                  |        35 |      0.26   |    0.1635 |               35 |       0      |


Mean peak |r| per condition:

|        |   speed_peak_abs_r |   bounce_peak_abs_r |
|:-------|-------------------:|--------------------:|
| (0, 0) |              0.472 |               0.14  |
| (0, 1) |              0.513 |               0.4   |
| (1, 0) |              0.506 |               0.169 |
| (1, 1) |              0.53  |               0.457 |


**Naive per-trial circular-shift test, fraction of trials 'significant' (p < 0.05).** Curtain + different music has no channel between the dancers, so it is the false-positive rate; curtain + same music shares only the music.

|        |   speed_naive_p |   bounce_naive_p |
|:-------|----------------:|-----------------:|
| (0, 0) |           0.634 |            0.219 |
| (0, 1) |           0.811 |            0.532 |
| (1, 0) |           0.762 |            0.345 |
| (1, 1) |           0.825 |            0.711 |

## 2-D virtual camera at 25 fps + keypoint jitter 0.005 body lengths

| signal   | contrast                                                 |   n_dyads |   mean_diff |   sd_diff |   dyads_positive |   wilcoxon_p |
|:---------|:---------------------------------------------------------|----------:|------------:|----------:|-----------------:|-------------:|
| speed    | PARTNER: vision vs curtain, different music              |        35 |      0.0394 |    0.045  |               27 |       0      |
| speed    | partner with shared music: vision vs curtain, same music |        35 |      0.0233 |    0.0439 |               26 |       0.001  |
| speed    | MUSIC: same vs different music, curtain                  |        35 |      0.0428 |    0.0469 |               32 |       0      |
| bounce   | PARTNER: vision vs curtain, different music              |        35 |      0.0269 |    0.0406 |               29 |       0      |
| bounce   | partner with shared music: vision vs curtain, same music |        35 |      0.0538 |    0.0772 |               26 |       0.0001 |
| bounce   | MUSIC: same vs different music, curtain                  |        35 |      0.2296 |    0.1562 |               35 |       0      |


Mean peak |r| per condition:

|        |   speed_peak_abs_r |   bounce_peak_abs_r |
|:-------|-------------------:|--------------------:|
| (0, 0) |              0.394 |               0.131 |
| (0, 1) |              0.437 |               0.36  |
| (1, 0) |              0.433 |               0.158 |
| (1, 1) |              0.459 |               0.413 |

## 2-D virtual camera at 25 fps + keypoint jitter 0.02 body lengths

| signal   | contrast                                                 |   n_dyads |   mean_diff |   sd_diff |   dyads_positive |   wilcoxon_p |
|:---------|:---------------------------------------------------------|----------:|------------:|----------:|-----------------:|-------------:|
| speed    | PARTNER: vision vs curtain, different music              |        35 |      0.0303 |    0.0341 |               27 |       0      |
| speed    | partner with shared music: vision vs curtain, same music |        35 |      0.0242 |    0.0343 |               27 |       0.0001 |
| speed    | MUSIC: same vs different music, curtain                  |        35 |      0.0299 |    0.0412 |               28 |       0      |
| bounce   | PARTNER: vision vs curtain, different music              |        35 |      0.0153 |    0.0252 |               25 |       0.0002 |
| bounce   | partner with shared music: vision vs curtain, same music |        35 |      0.042  |    0.0545 |               27 |       0      |
| bounce   | MUSIC: same vs different music, curtain                  |        35 |      0.1144 |    0.1037 |               33 |       0      |


Mean peak |r| per condition:

|        |   speed_peak_abs_r |   bounce_peak_abs_r |
|:-------|-------------------:|--------------------:|
| (0, 0) |              0.262 |               0.118 |
| (0, 1) |              0.292 |               0.232 |
| (1, 0) |              0.292 |               0.133 |
| (1, 1) |              0.316 |               0.274 |