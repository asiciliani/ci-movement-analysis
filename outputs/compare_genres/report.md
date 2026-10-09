# CI vs salsa with the same video pipeline (12 CI clips, 3 salsa clips)

Medians per genre (each clip one observation). Salsa = CoMPAS3D renders (CC BY-NC 4.0), first 60 s.

|                      |    CI |   salsa |   mann_whitney_p |
|:---------------------|------:|--------:|-----------------:|
| contact_frac         | 0.637 |   0.744 |           0.233  |
| weight_share_per_min | 3.223 |   0     |           0.0526 |
| frac_floor           | 0.107 |   0     |           0.0331 |
| frac_standing        | 0.71  |   0.979 |           0.0484 |
| hand_hand_share      | 0.128 |   0.158 |           0.633  |
| torso_share          | 0.403 |   0.441 |           0.1802 |
| roll_share           | 0.429 |   0.6   |           0.0501 |
| hold_share           | 0     |   0     |           0.4898 |


## Contact regions (pooled share of contact frames)

|                    |    CI |   salsa |
|:-------------------|------:|--------:|
| ('arm', 'hand')    | 0.144 |   0.184 |
| ('hand', 'hand')   | 0.138 |   0.158 |
| ('arm', 'torso')   | 0.133 |   0.147 |
| ('hand', 'torso')  | 0.124 |   0.219 |
| ('torso', 'torso') | 0.082 |   0.054 |
| ('arm', 'arm')     | 0.068 |   0.082 |
| ('foot', 'foot')   | 0.067 |   0.006 |
| ('leg', 'torso')   | 0.042 |   0.01  |
| ('foot', 'leg')    | 0.031 |   0.01  |
| ('head', 'head')   | 0.029 |   0.003 |


Known-answer expectations for salsa: hand-hand dominant, standing ~100 %, weight sharing ~0, HOLD > ROLL.