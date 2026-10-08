# Phase-2 design simulation

## Naive circular-shift test on blocks with NO coupling

|   nuisance_k |   naive_circular_test_false_positive_rate |
|-------------:|------------------------------------------:|
|          0   |                                 0.0333333 |
|          0.3 |                                 0.133333  |
|          0.6 |                                 0.916667  |


## N-S contrast (Wilcoxon across dyads, one-sided, alpha 0.05)

Rows with coupling_c = 0 are the false-positive rate under dyad-varying nuisance; the others are power.

|   coupling_c |     6 |    10 |    15 |
|-------------:|------:|------:|------:|
|         0    | 0.06  | 0.02  | 0.025 |
|         0.2  | 0.07  | 0.105 | 0.125 |
|         0.35 | 0.27  | 0.375 | 0.645 |
|         0.5  | 0.765 | 0.975 | 0.99  |


For scale (60 extra simulated dyads): c = 0.5 corresponds to a mean N-S difference in peak |r| of
≈ 0.14 (SD across dyads ≈ 0.11); c = 0.2-0.35 to ≈ 0.02-0.03. The between-dyad SD is an assumption
of this model and is the number the pilot must measure.