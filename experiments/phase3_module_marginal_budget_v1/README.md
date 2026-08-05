# Phase 3 module budget value curves

This is an independent, private-structure-only (`P`) framework. It accepts an
authoritatively resolved P-4096 `(vision, projector, language)` anchor and a
caller-supplied list of capacity points for each target module. Each curve
changes only its target coordinate dimension. Coordinate dimension is only the
trainable-capacity control; the curve x-axis is the target module's actual
module-separable encoded bit count.

The implementation reuses the established private coordinate store, fixed
projection model builder, frozen-parameter checks, quantizer, training
primitives, and risk arithmetic from the existing Phase 3 implementation. The
shared anchor is stored once in the training-config manifest and referenced by
all three curves. Completed curve records retain module-wise/total encoded
bits, development task risk, semantic bound, and the visual-gain guardrail.
Summaries sort by target module encoded bits and use adjacent finite
differences only. Every evaluation artifact is explicitly marked
`evaluation_role=development_only`.

Primary interfaces:

- `anchor.resolve_p4096_anchor`
- `curve_sweep.build_module_curve`
- `curve_sweep.build_curve_sweep_plan`
- `curve_sweep.build_seed_placeholder_sweep_manifest`
- `preflight.run_curve_preflight`, `preflight.preflight_and_freeze`, and
  `preflight.verify_frozen_manifest`
- `curve_results.summarize_curve_results`,
  `curve_results.summarize_formal_curve_results`, and
  `curve_results.summarize_results_root`
- `summarize_curve_sweep` command-line summary writer
- `results.curve_result_template` and `results.build_curve_result`
- `configs.make_baseline` and `configs.make_single_module_candidate`
- `parameterization.build_candidate_model`
- `codec.encode_coordinates`, `codec.decode_coordinates`, and
  `codec.load_decoded_coordinates`
- `training.private_trainable_parameters` and the reused schedule/freeze helpers
- `results.result_template` and `results.marginal_value`
- `risk.semantic_certificate` and `risk.visual_gain_certificate`

The frozen nine-point construction manifest is
`curve_sweep_manifest_9point.json`, with its raw-file SHA-256 in the adjacent
sidecar. Its seed remains an explicit placeholder; the preflight-only
construction root is not a formal training seed.

## Frozen three-seed run plan

`curve_run_plan_9point_3seed.json` expands the 25 distinct configurations over
the three seeds from the frozen P/S protocol. It contains 72 training runs and
three shared-anchor records that reuse the existing P-4096 checkpoints. The
adjacent SHA-256 sidecar and the source curve-manifest binding are verified
before selection or execution.

Use the unified dispatcher as a module. Omitting `--execute` is a read-only
dry run:

```bash
python -m experiments.phase3_module_marginal_budget_v1.run_curve_sweep \
  --results-root /path/to/curve-results \
  --all
```

Execution additionally requires the frozen Stage 2 artifact root. Every model
is scored on the same frozen Phase 3 v6 development input, preprocessing, and
aggregation protocol:

```bash
python -m experiments.phase3_module_marginal_budget_v1.run_curve_sweep \
  --results-root /path/to/curve-results \
  --artifact-root /path/to/stage2-artifacts \
  --curve vision \
  --execute
```

Selection supports `--run-id RUN_ID`, `--config-id SWEEP_CONFIG_ID --seed
SEED`, `--curve vision|projector|language`, and `--all`; a curve or all-runs
selection may also be filtered with `--seed`. A failed run is retried only when
selected explicitly with `--retry-failed`. A stale `running` state left by an
interrupted process is resumed only with `--resume-running`, using the bound
training recovery artifact or completed training manifest. Complete,
plan-bound results are validated and skipped without overwrite.

After any partial or complete run, write the seed-wise curve summary with:

```bash
python -m experiments.phase3_module_marginal_budget_v1.summarize_curve_sweep \
  --results-root /path/to/curve-results
```

After a complete summary, render the development-risk and
adjacent-marginal-value figures in PNG, PDF, and SVG:

```bash
python -m experiments.phase3_module_marginal_budget_v1.plot_curve_sweep \
  --summary /path/to/curve-results/curve_summary.json
```

The plotting command validates the summary semantics and adjacent-difference
arithmetic before rendering. Its compact risk view shows coordinate-wise
three-seed medians and the shared P-4096 anchor; individual seed markers and
seed min-max whiskers are intentionally omitted for clarity. The
marginal-value view uses the same three-panel line format and plots adjacent
finite differences of the displayed three-seed median curves against each
actual-bit interval midpoint. Neither view applies smoothing or a fitted
derivative.
