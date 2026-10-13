# Rolling vs gripping on SMPL-X meshes: CoMPAS3D salsa (71 sequences, 3023 contact tracks >= 1 s)

Contact = vertices within 3 cm of the partner's skin, 10 fps; sites tracked on each dancer's rest-pose body; GRIP < 5 cm net travel on both bodies, SLIDE/ROLL >= 15 cm on either.

## Known-answer checks

| check                                                             | result      |
|:------------------------------------------------------------------|:------------|
| hand-hand tracks are GRIP                                         | 70% of 2244 |
| hand-hand tracks during turn figures are GRIP                     | 74% of 493  |
| hand travels > turn, hands held (figures with a SLIDE/ROLL track) | p = 1.0000  |
| hand travels > open hold                                          | p = 1.0000  |


## Tracks by label

| label      |   tracks |
|:-----------|---------:|
| GRIP       |     2076 |
| MIXED      |      923 |
| SLIDE/ROLL |       24 |


Hand-hand tracks:

| label      |   tracks |
|:-----------|---------:|
| GRIP       |     1568 |
| MIXED      |      668 |
| SLIDE/ROLL |        8 |


Body tracks (any non hand-hand), main regions:

|                                   |   tracks |
|:----------------------------------|---------:|
| ('hand', 'trunk', 'GRIP')         |      261 |
| ('hand', 'trunk', 'MIXED')        |      145 |
| ('trunk', 'hand', 'GRIP')         |       85 |
| ('upper_arm', 'hand', 'GRIP')     |       60 |
| ('trunk', 'hand', 'MIXED')        |       38 |
| ('upper_arm', 'hand', 'MIXED')    |       32 |
| ('hand', 'forearm', 'GRIP')       |       26 |
| ('forearm', 'upper_arm', 'GRIP')  |       15 |
| ('forearm', 'forearm', 'GRIP')    |       12 |
| ('hand', 'upper_arm', 'GRIP')     |       11 |
| ('trunk', 'forearm', 'GRIP')      |        9 |
| ('forearm', 'upper_arm', 'MIXED') |        8 |


## By annotated figure class

| cls                    |   figures |   contact |   with_slide |
|:-----------------------|----------:|----------:|-------------:|
| open hold              |       451 |     1     |        0.007 |
| turn, hands held       |       372 |     0.96  |        0.008 |
| closed hold            |       234 |     1     |        0.004 |
| hand travels over body |       100 |     0.888 |        0     |
| other                  |       858 |     1     |        0.01  |