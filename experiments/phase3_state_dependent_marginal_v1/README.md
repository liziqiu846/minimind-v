# Phase 3 state-dependent local marginal value

This independent experiment answers only whether the local Vision, Projector,
and Language marginal-value ordering changes across three fixed private
coordinate-budget states. It has three seeds, nine reused base checkpoints,
and exactly 27 newly trained one-module-up candidates.

The frozen design is:

- original `(582, 2327, 1187)` → Vision 766, Projector 3063, Language 1562
- language-rich `(582, 2327, 3561)` → Vision 766, Projector 3063, Language 4686
- projector-rich `(582, 6981, 1187)` → Vision 766, Projector 9187, Language 1562

Only the named module changes within a candidate. Training, private fixed
projection, frozen-parameter checks, module-separable MMB1 encoding, frozen
Phase 3 v6 development scoring, and risk arithmetic are reused from
`phase3_module_marginal_budget_v1`.

Freeze after the twelve configuration preflight and nine checkpoint-reuse
checks:

```bash
python -m experiments.phase3_state_dependent_marginal_v1.preflight --freeze
```

Read-only dry run:

```bash
python -m experiments.phase3_state_dependent_marginal_v1.run_experiment --all
```

Formal execution requires the frozen Stage 2 artifact root and a single
visible A40 at logical `cuda:0`. `--shard-count`/`--shard-index` support
disjoint multi-GPU workers without changing the manifest.

After all 36 model runs, the summary command verifies every checkpoint,
training freeze receipt, codec round trip, development result, and child
artifact before writing the 27 state × module × seed comparisons and the
three state-wise rankings.

The formal report uses the signed trained target-module bit difference exactly
as specified; a nonzero negative compression delta remains in the comparison,
while a zero delta would make eta undefined:

```bash
python -m experiments.phase3_state_dependent_marginal_v1.reporting.summarize_signed
```
