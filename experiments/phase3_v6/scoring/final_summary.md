# Phase 3 v6 frozen contrast-hull scoring

Scope: fixed 1,343 effective SugarCrepe++ certifying-formal image groups, fixed contrast hulls, and the fixed balanced K=5 mismatch manifest.

Protocol SHA-256: `3cbf89287ef5c75657bf0df6ed1170f0ab1c916ac5aacc0c009fb80c3bbf9195`

## Main image-equal results

| Model | Method | mu K1 | mu K3 | mu K5 | Win rate K5 |
|---|---:|---:|---:|---:|---:|
| M0-root-43101 | M0 | 0 | 7.28098283131e-20 | 2.00464010224e-19 | 0.157855547282 |
| M0-root-43102 | M0 | 0 | 6.72579022566e-19 | 1.09714155161e-19 | 0.163067758749 |
| M0-root-43103 | M0 | 0 | -1.00417757844e-18 | 1.42439441388e-19 | 0.173492181683 |
| M1-root-none | M1 | 0.000948974070591 | 0.000834021604645 | 0.000610095041113 | 0.516753536858 |
| M2-root-43101 | M2 | 0.000757696565463 | 0.000718575971778 | 0.000811513360918 | 0.538346984363 |
| M2-root-43102 | M2 | -9.26397869977e-05 | 0.000716070868422 | 0.000627192138965 | 0.501116902457 |
| M2-root-43103 | M2 | 0.000199568257279 | 0.000220286939289 | -2.01850776282e-05 | 0.495160089352 |
| M3-root-43101 | M3 | -0.000684202222072 | -0.00140784948255 | -0.00172319892059 | 0.506329113924 |
| M3-root-43102 | M3 | -0.000349950358868 | -0.000573843587654 | -0.000436766076267 | 0.486224869695 |
| M3-root-43103 | M3 | 0.000362994995042 | -0.000358786302283 | -0.000281843251265 | 0.492926284438 |

## M0 invariant

| Model | max record | max image | abs mu K5 | pass 1e-8 |
|---|---:|---:|---:|---:|
| M0-root-43101 | 1.11022302463e-16 | 1.11022302463e-16 | 2.00464010224e-19 | True |
| M0-root-43102 | 1.11022302463e-16 | 1.11022302463e-16 | 1.09714155161e-19 | True |
| M0-root-43103 | 1.11022302463e-16 | 1.11022302463e-16 | 1.42439441388e-19 | True |

## Interpretation

These are fixed-benchmark descriptive results. They are not a new unseen test set, a population guarantee for future natural images, a new Phase 3 compression bound, or evidence that random mismatches are equivalent to hard visual negatives.

Stage 2 correlations, the seven-non-M0 sensitivity analysis, and the three same-root M2/M3 differences are descriptive only.

