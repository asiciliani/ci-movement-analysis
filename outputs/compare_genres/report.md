# CI vs salsa with the same video pipeline (11 CI clips, 3 salsa clips)

Medians per genre (each clip one observation). Salsa = CoMPAS3D renders (CC BY-NC 4.0), first 60 s.

|                      |    CI |   salsa |   mann_whitney_p |
|:---------------------|------:|--------:|-----------------:|
| contact_frac         | 0.609 |   0.801 |           0.1264 |
| weight_share_per_min | 3.751 |   0     |           0.0286 |
| frac_floor           | 0.206 |   0     |           0.0123 |
| frac_standing        | 0.584 |   0.966 |           0.0055 |
| hand_hand_share      | 0.113 |   0.115 |           0.7692 |
| torso_share          | 0.455 |   0.49  |           0.456  |
| roll_share           | 0.564 |   0.8   |           0.0125 |
| hold_share           | 0     |   0     |           1      |


## Contact regions (pooled share of contact frames)

|                    |    CI |   salsa |
|:-------------------|------:|--------:|
| ('arm', 'torso')   | 0.122 |   0.16  |
| ('hand', 'torso')  | 0.115 |   0.211 |
| ('hand', 'hand')   | 0.115 |   0.135 |
| ('torso', 'torso') | 0.109 |   0.066 |
| ('arm', 'hand')    | 0.1   |   0.143 |
| ('leg', 'torso')   | 0.057 |   0.011 |
| ('foot', 'foot')   | 0.055 |   0.01  |
| ('arm', 'arm')     | 0.054 |   0.079 |
| ('foot', 'leg')    | 0.044 |   0.013 |
| ('leg', 'leg')     | 0.032 |   0.01  |


Known-answer expectations for salsa: hand-hand dominant, standing ~100 %, weight sharing ~0, HOLD > ROLL.