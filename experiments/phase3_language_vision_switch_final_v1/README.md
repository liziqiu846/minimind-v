# Final Language ↔ Vision state-switch validation

This is the terminal go/no-go experiment for one claim: increasing Language
should be preferred to increasing Vision at the Original state, while the order
should reverse at the Language-rich state.

The design contains only:

- Original `(582, 2327, 1187)`
- Language-rich `(582, 2327, 3561)`
- Vision and Language actions
- seeds `43101`, `43102`, and `43103`

Projector remains fixed at 2327.  The new rounded action coordinates are:

- Original: Vision 1700 or Language 2700
- Language-rich: Vision 1700 or Language 5976

Existing actual-bit curves are used only to calibrate these four coordinates.
They predict target-module increases of roughly 2.1–2.8 kbit.  The intended
Language-rich Language coordinate 6500 was lowered to the nearest smaller
dimension with complete fixed-projection coverage for every frozen seed.  No
prior candidate result is reused.  The six complete base results are reused
without training or model inference; exactly 12 candidates are newly trained
and evaluated.

The primary metric is the raw, unclipped full compression bound improvement
`delta_B = B_base - B_candidate`.  Eta is not computed.  The experiment passes
only if the predeclared actual-bit adequacy gate passes and at least two of
three seeds plus the three-seed median show Language > Vision at Original and
Vision > Language at Language-rich.  Failure terminates this route without
expansion.

Freeze after preflight:

```bash
python -m experiments.phase3_language_vision_switch_final_v1.preflight --freeze
```

Read-only dry run:

```bash
python -m experiments.phase3_language_vision_switch_final_v1.run_experiment --all
```

Execute only after the frozen manifest and dry run have been audited.
