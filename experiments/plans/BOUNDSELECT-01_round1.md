# BOUNDSELECT-01 Round 1 — frozen-bound model selection

## Scientific question

Can the repository's formal raw, unclipped full compression bound select a
frozen MiniMind-V hypothesis with lower independently evaluated validation
answer risk than the repository's fixed historical baseline?

This plan implements the user-frozen Route 1 question. It does not change the
Mission Question, introduce Route 2, or claim that a compression bound is a
complete VLM mechanism.

## Hypothesis

If the existing raw full compression bound is useful as a model-selection
criterion in the frozen candidate family, then the unique candidate minimizing
that bound will have strictly lower decoded-quantized validation answer risk
than the fixed baseline.

If it does not, this BoundSelect instantiation fails in this candidate family.
No candidate-set change, baseline change, new training, seed, budget, sweep, or
rescue is allowed.

## VLM specificity

The eligible family contains frozen language-only and vision-language
hypotheses with historical projector, private vision/projector/language, and
globally shared coordinate structures. The experiment tests whether their
training-risk-plus-description-length certificate ordering transfers to
unseen validation answer risk.

## Frozen candidate-family audit

The preferred Phase 3 P/S 18-model development artifact was audited first. It
is excluded because its own frozen output declares
`development_only_exploratory_not_a_formal_certificate`; it therefore does not
meet the user's requirement for an existing formal raw full compression bound.

The eligible family is the complete, preregistered Stage 2 v2 formal family:

- protocol: `minimind-v-stage2-joint-compression-v2`;
- protocol SHA-256:
  `4a15ae6697081098973998f7340702368403fa81f39d6c8ed43172b74a55b5b3`;
- exact retained checkpoint identities are frozen by the Phase 3 v6 protocol
  SHA-256
  `3cbf89287ef5c75657bf0df6ed1170f0ab1c916ac5aacc0c009fb80c3bbf9195`;
- family size: 10;
- identical frozen training/validation, smoothing, codec, and bound protocol;
- all ten formal checkpoints, actual encoded-bit artifacts, raw bounds, and
  decoded-quantized validation-risk artifacts must exist and pass provenance
  checks.

The unique default baseline is `M1-root-none`, because the frozen protocol
defines M1 as the `historical fixed hashed projector baseline`. This decision
is frozen before validation-risk values are read.

The older compact Stage 2 final report describes a different completed
execution whose large checkpoints were removed under the retention policy. Its
saved bound hashes do not bind the currently retained Phase 3 v6 checkpoints,
so its numerical rows are not mixed with this family.

## Falsifiable prediction

Let

`selected = argmin_h raw_compression_upper_bound_bits(h)`.

The prediction is:

1. `selected` is unique;
2. its raw bound is strictly below the M1 baseline raw bound; and
3. its decoded-quantized correct-image validation answer risk is strictly below
   the M1 baseline risk.

## Minimal experiment

1. Generate and commit a risk-value-free candidate registry containing only
   eligibility metadata, provenance, actual bits, raw bounds, and the fixed
   baseline flag.
2. Run a selector whose accepted candidate schema contains no validation-risk
   value.
3. Freeze the selector receipt.
4. Read validation risk only for the selected candidate and fixed baseline.
5. Produce one final comparison and stop.

No model inference or training is performed.

## Selection cost

For `K=10`, separately report `ceil(log2(K)) = 4` bits. Do not re-encode a
checkpoint and do not alter the existing raw bounds. Also report the existing
familywise union-bound convention (`delta_total=0.05`,
`delta_per_model=0.005`) already used by the frozen Stage 2 bounds.

## Decision criteria

### Support / PASS

PASS if and only if:

1. the selector input and receipt contain no held-out/validation risk value;
2. the unique selected raw bound is strictly below the baseline raw bound; and
3. the selected validation answer risk is strictly below the baseline risk.

### Reject / FAIL

FAIL if any PASS condition fails, including if the selected candidate is the
baseline, either strict inequality fails, or an exact bound tie has no frozen
tie-break.

### Unable to determine

Missing, partial, inconsistent, non-formal, hash-invalid, or leaked artifacts
make the candidate ineligible. If this prevents a unique complete family or
baseline, report FAIL for the requested closeout; do not replace the family or
baseline.

## Possible confounds and scope

- The formal certificate covers the frozen finite catalog, not an unrestricted
  real-world distribution.
- Model/root identities are members of one finite family; roots are not
  selected post hoc before BoundSelect.
- The raw bound uses decoded-quantized full training risk. Validation answer
  risk is a separate 2,000-draw artifact and is not an input to selection.
- A failure rejects this BoundSelect instantiation, not compression theory or
  all generalization-bound-guided algorithms.

## Resources

- GPU: 0
- new training/model inference: 0
- new seeds/budgets/checkpoints: 0
- computation: local JSON/provenance audit and deterministic arithmetic only
