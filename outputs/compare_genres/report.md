# CI vs salsa with the same video pipeline (12 CI clips, 3 salsa clips)

Medians per genre (each clip one observation). Salsa = CoMPAS3D renders (CC BY-NC 4.0), first 60 s.

|                      |    CI |   salsa |   mann_whitney_p |
|:---------------------|------:|--------:|-----------------:|
| contact_frac         | 0.604 |   0.27  |           0.0703 |
| weight_share_per_min | 3.223 |   0     |           0.0526 |
| frac_floor           | 0.107 |   0     |           0.0331 |
| frac_standing        | 0.71  |   0.979 |           0.0484 |
| hand_hand_share      | 0.129 |   0.162 |           0.2945 |
| torso_share          | 0.4   |   0.45  |           0.1363 |
| roll_share           | 0.4   |   0     |           0.0555 |
| grip_share           | 0     |   0     |           0.6378 |


## Contact regions (pooled share of contact frames)

|                    |    CI |   salsa |
|:-------------------|------:|--------:|
| ('hand', 'hand')   | 0.14  |   0.174 |
| ('arm', 'hand')    | 0.139 |   0.194 |
| ('arm', 'torso')   | 0.128 |   0.146 |
| ('hand', 'torso')  | 0.121 |   0.205 |
| ('torso', 'torso') | 0.085 |   0.068 |
| ('foot', 'foot')   | 0.071 |   0.006 |
| ('arm', 'arm')     | 0.068 |   0.074 |
| ('leg', 'torso')   | 0.044 |   0.011 |
| ('foot', 'leg')    | 0.033 |   0.006 |
| ('head', 'head')   | 0.031 |   0.003 |


Known-answer expectations for salsa: hand-hand dominant, standing ~100 %, weight sharing ~0, GRIP > ROLL.