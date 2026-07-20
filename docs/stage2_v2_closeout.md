# Stage 2 v2 completion and interpretation addendum

## Status

The hardware-amended Stage 2 v2 experiment is complete. All ten predeclared
formal models were rerun from scratch, all seven predeclared visual diagnostic
models were summarized, and the post-execution completion audit passed all 131
checks. No formal failure receipt exists and no mapping root was selected after
seeing the results.

The execution is bound to annotated tag
`stage2-protocol-v2-fast-multigpu` at commit
`07eff239d965f644e3207925ddac446a803ee45e`. It is explicitly not presented as
an execution of the superseded single-GPU tag. Each model remained on one
physical A40, while independent models were dispatched across these two A40s:

- `GPU-8e1547c5-b212-b319-786a-c17a3d644e0b`
- `GPU-dc9b3899-d5cf-ff29-8870-c369ef8196a6`

This hardware amendment did not change the model families, 4096-coordinate
budgets, data draws, selected learning rates, seeds, optimizer, precision,
codec, smoothing, risk aggregation, bound, mapping roots, or diagnostic rules.
The frozen behavior-preservation audit therefore continued to exclude a rerun
of the 36 development experiments.

## Sampling and certificate scope

The exact confirmation data materialized under source protocol SHA-256
`89f5e8ee3083f9a66b86b8cef83b73d5a66a02b2915b4e55862dd911801a21d0`
were reused without regeneration. Independent verification and replay passed:

- fixed eligible catalog: 39,561 exact-image units;
- training: 10,000 independent with-replacement draws;
- validation: 2,000 independent with-replacement draws;
- total independently reconstructed draws: 12,000;
- training SHA-256:
  `3c3d90c525f43200d35ebd5b4ac1719c8336d278aecbf7e929997c8401b1d5ce`;
- validation SHA-256:
  `72456b3a6f43800a2302fbc376f905335c9bb52b5b8bdad5ddee07ec99f942e8`.

The resulting strict certificate language applies only to the finite uniform
empirical distribution over this frozen eligible catalog. It is not a
real-world-distribution or out-of-distribution certificate.

## Formal results

All values below are the predeclared raw, unclipped compression upper bounds in
bits. The smoothed random-prediction baseline is 12.643856 bits.

| Model | Root | Train risk | Validation risk | Adapter bits | Raw bound | Margin below random |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| M0 | 43101 | 5.067062 | 5.054879 | 6,408 | 11.040984 | 1.602873 |
| M0 | 43102 | 5.064794 | 5.054002 | 6,720 | 11.181755 | 1.462101 |
| M0 | 43103 | 5.014444 | 5.000706 | 8,040 | 11.702784 | 0.941072 |
| M1 | — | 4.874315 | 4.861855 | 10,600 | 12.550426 | 0.093430 |
| M2 | 43101 | 4.931502 | 4.919503 | 8,792 | 11.924497 | 0.719359 |
| M2 | 43102 | 4.916816 | 4.902748 | 9,856 | 12.319463 | 0.324393 |
| M2 | 43103 | 4.878552 | 4.864660 | 10,568 | 12.543102 | 0.100754 |
| M3 | 43101 | 4.974591 | 4.961433 | 6,144 | 10.824745 | 1.819111 |
| M3 | 43102 | 5.004928 | 4.990440 | 7,528 | 11.477638 | 1.166219 |
| M3 | 43103 | 4.998919 | 4.984781 | 6,112 | 10.833892 | 1.809964 |

All ten raw bounds are below the random-prediction baseline for the declared
finite-catalog distribution. M1 and M2 at root 43103 have the smallest positive
margins and should not be described as strong certificates merely because they
are technically nonvacuous by this baseline.

The three predeclared paired differences were:

| Root | Vision cost `T = B(M3)-B(M0)` | Shared gain `G = B(M2)-B(M3)` |
| ---: | ---: | ---: |
| 43101 | -0.216239 | 1.099752 |
| 43102 | 0.295882 | 0.841826 |
| 43103 | -0.868892 | 1.709210 |
| Descriptive mean | -0.263083 | 1.216929 |

The shared-coordinate M3 bound is tighter than the independently allocated M2
bound at every predeclared mapping root. The M3-versus-M0 vision-cost contrast
has mixed signs across roots. The arithmetic means are descriptive summaries;
they are not the result of selecting a preferred root.

## Secondary visual diagnostics

The seven diagnostic models retained their predeclared secondary/descriptive
status and were not used for model or mapping-root selection.

- Paired-shuffled minus correct-image risk was positive for all seven models.
  The observed means ranged from 0.003041 to 0.021029 bits, and every frozen
  percentile interval was above zero.
- No-image minus correct-image risk was positive for all seven models. The
  observed means ranged from 0.514132 to 0.662000 bits, again with every frozen
  percentile interval above zero.

These diagnostics establish image dependence for these frozen hypotheses on
the frozen validation draws. They do not establish universal visual reasoning,
semantic grounding, or real-world generalization.

## v1/v2 interpretation

Stage 2 v1 remains immutable at the three closeout hashes recorded in
`docs/stage2_v1_closeout.md`. Its empirical and compression observations are
retained, but its adaptive sampling construction did not establish the
independence premise required for strict certificate language.

The v1/v2 differences are descriptive because the two versions use different
confirmation samples. They are not paired-sample effects. In particular, the
changed adapter byte lengths arise from separately trained coordinates on the
different confirmation draws and do not indicate a codec-rule change.

## Final evidence

The authoritative result files are under
`experiments/runs/stage2_v2_fast/final/`:

- final report JSON:
  `f872bd5925fa10302393f253acf6efef2f468e7ab0e456bcb0a912ee8df5cb84`;
- final report Markdown:
  `a093ea7b9debc162f314cc5788df102c5f5c7d8f908dfeb496892e0169e6e381`;
- 268-file artifact manifest:
  `3d360a2cbc844c1962d6a34928ec1af74e23b75a3605b032c9ce27f20636264f`;
- formal summary:
  `f477ac434b97a56e5acba24a686609cd70dc5ab5b5d375506f12de9ce1a52e4a`;
- seven-model diagnostics:
  `6357034dd1812213b5bb2f82f97def3fee555e2bf552e172a7e883eb9828eaa0`;
- runtime-integrity receipt:
  `661537ca9528194e8d970a5c378ef8a0f7136936d6c1e85402268a57378faf64`;
- v1/v2 comparison JSON:
  `171e97d820be23978d071077b70a39cf5a0257dd157bdc8c2020ed7bff1ea711`;
- 131-check completion audit:
  `1ff3fc7d1bb6611311135dc1bc5a6bb71d40adcf4408e2199d91cdf81a7feb5b`.

The first finalizer invocation captured `supervisor.log` before the
orchestrating `tee` appended the finalizer output and completion line. After the
orchestrator exited, the same frozen finalizer was rerun with the same
protocol-bound inputs and the now-stable log. The completion audit recomputed
every byte count and SHA-256 in the replacement 268-file manifest with zero
mismatches. The compact post-experiment checkout retains the audit receipt for
this incident but removes the five superseded duplicate reports.

## Post-experiment retention

After completion and publication, reproducible intermediate datasets, model
checkpoints, per-draw risk vectors, and full run directories were removed from
the working checkout to keep the repository small. The source asset remains
available under the separately managed immutable asset root, and its SHA-256
still matches the protocol. Protocols, implementation code, final summaries,
diagnostics, reports, comparison, audit receipts, and conclusion addenda remain
tracked. The 268-file manifest and 131-check receipt are immutable records of
the complete pre-cleanup state; the compact checkout is not claimed to retain
all 268 raw artifacts locally. See `docs/stage2_retention.md`.
