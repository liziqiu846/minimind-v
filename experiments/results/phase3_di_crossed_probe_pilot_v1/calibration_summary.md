# Phase 3 D_I checkpoint-only crossed diagnostic pilot v1

## Scope and integrity

This is a fixed-checkpoint measurement calibration only. It does not estimate
trajectory D_I, a CMI bound, or a generalization relationship. The pilot used
the six budget-2048 raw checkpoints (P/S × model seed 43101/43102/43103), three
independent probe seeds (74001/74002/74003), and 33 slots per panel. No model
training, MMS2 evaluation, held-out performance correlation, final confirmation
access, or Phase 4 work was performed.

All 99 panel/slot assignments matched across all six checkpoints on probe seed,
train and ghost group identities, image hashes, canonical-conversation hashes,
and selected batch position. The pre-run manifest identity audit and post-run
result identity audit both passed. All six run receipts are complete with 99
rows each; the merged table contains 594 rows.

## Stability results

The probe-to-structure variation ratio is defined as:

- probe variation: the root mean across model seeds of the bootstrap variance
  of K-panel averages of the paired P/S mean;
- structure variation: the root mean squared paired P-minus-S difference across
  seed/bootstrap draws;
- ratio: probe variation divided by structure variation.

For T=11, raw ratios for K=1/2/3 were 0.520/0.406/0.341 and log ratios were
0.528/0.391/0.325. For T=22 they were 1.231/0.900/0.743 raw and
0.961/0.695/0.566 log. For T=33 they were 1.372/0.996/0.815 raw and
1.036/0.742/0.609 log. Panel averaging therefore reduced the estimated probe
variation monotonically, but a single 33-probe panel still had probe variation
at least as large as structure variation.

Increasing T improved the numerical stability of each checkpoint aggregate.
The bootstrap CV range fell from 0.084–0.194 at T=11, to 0.070–0.119 at T=22,
and 0.059–0.106 at T=33. The maximum single-probe contribution share fell from
0.123–0.266, to 0.073–0.145, to 0.057–0.102; the top-three share fell from
0.360–0.483, to 0.211–0.283, to 0.162–0.237.

The paired structure contrast did not become reliably stable. The minimum
bootstrap P/S sign-retention rates for T=11/22/33 were respectively
0.566/0.584/0.497. At T=33, seed 43101 had panel directions P>S, P<S, P>S,
while seeds 43102 and 43103 were P<S in all three panels. Thus changing the
shared panel flipped the P/S ordering for seed 43101.

At T=33, crossed-panel ranking correlations were moderate to high, but absolute
agreement was poor. Pairwise Pearson correlations were 0.775–0.836 raw and
0.880–0.933 log; pairwise Spearman correlations were 0.771–0.943 raw and
0.829–0.943 log. McGraw–Wong ICC(A,1), with six checkpoints as targets and
three panels as raters, was 0.084 raw and 0.160 log, indicating substantial
panel-level shifts despite correlated rankings.

## Decision

`DI_MEASUREMENT_STILL_UNSTABLE`

The pilot establishes that 33 probes substantially reduce single-probe
dominance and aggregate CV, and that averaging panels reduces probe variation.
It does not establish stable P/S discrimination: one model-seed pair changes
direction across panels, the weakest paired sign retention is approximately
chance, and absolute cross-panel agreement remains low. Consequently these
fixed-checkpoint data do not support freezing a unique formal K/T. They also
cannot calibrate additional variation caused by changing parameter states
along an SGD trajectory.
