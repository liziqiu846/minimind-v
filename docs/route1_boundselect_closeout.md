# Route 1 BoundSelect v1 closeout

## Outcome

**FAIL.** The frozen raw full compression bound selected a model with a
strictly lower bound than the fixed baseline, but that model had a strictly
higher decoded-quantized validation answer risk.

This closes the requested minimal test. No model was trained, no candidate,
seed, budget, baseline, metric, or tie-break was added after the result.

## Frozen design

- Rule: select the unique candidate minimizing the repository's formal raw,
  unclipped full compression bound.
- Eligible catalog: the complete ten-model Stage 2 v2 formal family under
  protocol `minimind-v-stage2-joint-compression-v2`.
- Fixed baseline: `M1-root-none`, identified by the frozen protocol as the
  historical fixed hashed-projector baseline.
- Held-out metric: decoded-quantized correct-image validation answer risk on
  2,000 samples.
- Selection cost: `ceil(log2(10)) = 4` bits, reported separately without
  changing the existing bound or re-encoding a checkpoint.
- Existing finite-family convention: familywise delta `0.05`, per-model delta
  `0.005`.

The Phase 3 P/S family was audited first and excluded because its artifact
explicitly labels the results development-only and not a formal certificate.
The older compact Stage 2 report was not mixed into this family because its
saved bound hashes do not bind the retained checkpoint identities.

## Leakage control and execution order

1. `candidate_registry.json` froze all ten eligible candidates, provenance,
   actual encoded bits, raw bounds, and the baseline. It contained no
   held-out-risk values and was committed as `bc398db`.
2. The selector read only the frozen registry and chose the unique raw-bound
   minimum. Its receipt was committed separately as `ca08555`.
3. Only after that commit did the evaluator read the validation-risk artifacts
   for the selected model and baseline.

Registry SHA-256:
`2e792ea77330f0610649960dc79e145f3225eb5468ca23f57ff9ce5eed7769e3`.

## Final comparison

| Quantity | BoundSelect | Fixed baseline | Selected minus baseline |
|---|---:|---:|---:|
| Model | `M3-root-43103` | `M1-root-none` | — |
| Actual encoded bits | 6,384 | 10,488 | -4,104 |
| Raw full compression bound | 10.97098526042128 | 12.516978640541838 | -1.5459933801205583 |
| Validation answer risk | 4.995862168073654 | 4.868565459132195 | +0.1272967089414596 |

The selected model satisfies the strict bound improvement but fails the strict
risk improvement. Therefore only two of the three required PASS conditions
hold:

- selection did not read held-out risk: yes;
- selected raw bound is strictly lower than baseline: yes;
- selected validation answer risk is strictly lower than baseline: no.

## Interpretation

For this frozen finite catalog, minimizing the existing raw full compression
bound did not select a model with better held-out task generalization than the
fixed default baseline. This is a failure of the specified BoundSelect
instantiation; it does not by itself reject compression theory or every
possible bound-guided training algorithm.

Under the frozen stopping rule, no tuning, candidate replacement, baseline
replacement, additional ablation, or training follows this result.
