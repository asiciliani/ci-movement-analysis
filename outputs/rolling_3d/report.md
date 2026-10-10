# Rolling vs gripping in 3-D: CoMPAS3D salsa markers (21 sequences, 1178 annotated figures, 443 contact bouts)

Grip = hand-hand markers < 0.1 m; surface contact = pairs with trunk/forearm/head < 0.1 m (0.16 m with trunk markers); location on a per-dancer MDS body chart; travel = net displacement between the first and last 0.5 s of the window (edges trimmed 0.3 s), max over the two bodies. Excluded as noisy captures (rigid-group distance SD > 1 cm): Pair1_song1_take2, Pair1_song2_take1, Pair1_song2_take2, Pair1_song3_take2, Pair1_song4_take1, Pair2_song1_take1, Pair2_song1_take2, Pair2_song2_take1, Pair2_song2_take2, Pair2_song3_take1, Pair2_song3_take2, Pair2_song4_take2, Pair3_song3_take2, Pair4_song4_take2, Pair6_song1_take1, Pair6_song2_take1, Pair6_song2_take2, Pair6_song3_take1, Pair6_song3_take2, Pair6_song4_take1, Pair7_song3_take2, Pair7_song4_take1, Pair7_song4_take2, Pair8_song1_take1, Pair9_song4_take1.

## By annotated figure class

| cls                    |   figures |   grip |   surface |   hand_trunk |   travel_m |   travel_measured |
|:-----------------------|----------:|-------:|----------:|-------------:|-----------:|------------------:|
| open hold              |       285 |  0.92  |     0.409 |        0.316 |      0.364 |             0.389 |
| turn, hands held       |       220 |  0.64  |     0.206 |        0.09  |      0.426 |             0.186 |
| closed hold            |       174 |  0.469 |     0.854 |        0.784 |      0.331 |             0.885 |
| hand travels over body |        46 |  0.574 |     0.419 |        0.305 |      0.227 |             0.239 |
| other                  |       453 |  0.578 |     0.197 |        0.106 |      0.223 |             0.258 |


## Known-answer checks

| check                                          | measure         |   mann_whitney_p_one_sided |
|:-----------------------------------------------|:----------------|---------------------------:|
| closed hold > open hold                        | hand_trunk_frac |                     0      |
| hand travels > turn, hands held                | travel_m        |                     0.8952 |
| hand travels > open hold                       | travel_m        |                     0.9609 |
| turn, hands held > open hold (should NOT hold) | travel_m        |                     0.2103 |


## Contact bouts (>= 1 s)

|       |   dur_s |   travel_leader_m |   travel_follower_m |   grip_frac |
|:------|--------:|------------------:|--------------------:|------------:|
| count | 443     |           431     |             431     |     443     |
| mean  |   3.638 |             0.218 |               0.204 |       0.394 |
| std   |   7.546 |             0.169 |               0.148 |       0.351 |
| min   |   1.6   |             0     |               0     |       0     |
| 25%   |   1.9   |             0.085 |               0.081 |       0.082 |
| 50%   |   2.4   |             0.17  |               0.178 |       0.286 |
| 75%   |   3.367 |             0.308 |               0.287 |       0.682 |
| max   | 150.6   |             1.015 |               0.961 |       1     |


Main region pairs:

| main_regions    |   share |
|:----------------|--------:|
| hand-trunk      |   0.587 |
| trunk-hand      |   0.21  |
| hand-forearm    |   0.047 |
| trunk-forearm   |   0.041 |
| forearm-forearm |   0.036 |
| forearm-trunk   |   0.034 |
| forearm-hand    |   0.023 |
| trunk-trunk     |   0.02  |


## 2-D labels vs 3-D in the same bouts (rendered video vs mocap)

| label_2d   |   bouts |   grip_3d |   surface_3d |   travel_3d_median_m |
|:-----------|--------:|----------:|-------------:|---------------------:|
| HOLD       |       1 |     0     |        1     |                0.595 |
| MIXED      |       7 |     0.467 |        0.544 |                0.402 |
| ROLL       |      13 |     0.556 |        0.5   |                0.415 |