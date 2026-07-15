# Stage 2 joint-compression experiment protocol (draft)

The authoritative draft is [`stage2_protocol.draft.json`](stage2_protocol.draft.json).
This document is a review index, not a second source of protocol values. Any
disagreement must stop execution until the JSON is corrected and recommitted.

## Status and isolation

- Base commit: `b71602a3106434e1165216cc5f85f30957f0ec95`.
- Worktree/branch: `minimind-v-stage2` / `exp/stage2-vlm-joint-compression`.
- Phase 3 is preserved at `archive/phase3-pre-stage2` commit `4f7a1a2`.
- Immutable input receipts were committed separately at `6d5e513`.
- Stage 2 assets live under `/home/lizhaohui/lzq/stage2-assets-v1` and are
  read-only. Their copied manifest and SHA-256 list are under `experiments/`.
- No Phase 3 run artifact may be opened after the historical-exposure receipt
  was imported. There were no manually viewed external source images to add.

## Scientific comparison

All models receive the same caption task and use 4,096 learned coordinates.

| Group | Visual input | Coordinate organization | Formal runs |
| --- | --- | --- | ---: |
| M0 | no | one 4,096-dimensional language vector | roots 43101--43103 |
| M1 | yes | historical fixed projector, two 2,048-dimensional vectors | one |
| M2 | yes | independent vision/projector/language vectors of 582/2327/1187 | roots 43101--43103 |
| M3 | yes | one globally shared 4,096-dimensional vector | roots 43101--43103 |

M2 and M3 target the identical four vision, two projector, and five language
linear layers. M1, M2, and M3 share the same fixed projector base tensors and
non-affine LayerNorm configuration. Deterministic SHA-256 mapping, A0
construction, element ordering, sign assignment, and use-count normalization
are specified byte-for-byte in the JSON draft.

## Data and leakage control

Confirmation data are generated only after the implementation and final
protocol have been committed and tagged. From the immutable source parquet,
the builder ranks candidates using seed 2026, selects 2,000 validation images
first and then 10,000 training images, and rejects any exact historical match
or any pHash within Hamming distance 6 of history or a previously selected
image. Full VLM token sequences, exact assistant spans including EOS, and all
membership/selection receipts are frozen. Any shortage or invariant failure is
a stop condition, not permission to weaken the criteria.

## Development and freezing

The only development decision is learning rate. Each of M0--M3 runs the grid
`{0.005, 0.015, 0.05}` with three predeclared seed/root pairs, for 36 runs.
M0 and M1 select their own mean-bound minimizer. M2 and M3 share a single rate
selected from the equal-weight mean of their six bounds. A rate within `1e-4`
of the minimum is tied, and the smaller tied rate wins. Development uses
delta 0.05 and is not formal evidence.

After recording the selected rates and all pending deterministic hashes, the
implementation is committed; the final protocol is materialized in a separate
commit and tagged `stage2-protocol-v1`. Confirmation runs may not alter code,
data, environment, GPU, hyperparameters, precision, batch size, or protocol.

## Formal execution and evidence

The ten models run in the declared order on one deterministically selected idle
A40: three M0 mappings, M1, three M2 mappings, and three M3 mappings. Each uses
AdamW for three epochs with micro-batch 4, accumulation 4, bf16 autocast, fixed
seed 2026, and the frozen cosine schedule.

Each coordinate vector is quantized to seven levels and stored in the versioned
`MMS2` binary format. Complexity is exactly eight times the entire compressed
adapter file size. A clean process independently decodes each adapter before
full train/validation risk evaluation. Ten compression bounds use per-model
delta 0.005. The raw unclipped bound is primary.

For all seven visual models, secondary diagnostics compare correct images,
deterministically paired mismatched images, and absent images. Bootstrap units,
seeds, repetitions, and percentile rules are fixed in the JSON and cannot be
used for model selection or promoted into post-hoc formal tests.

The final report must include all ten runs, all three mapping roots, the
per-root vision cost `T_k = B(M3,k) - B(M0,k)`, the shared-coordinate gain
`G_k = B(M2,k) - B(M3,k)`, descriptive arithmetic means, risk/complexity
decompositions, diagnostics, exact hashes, and any failure receipts.

## Draft placeholders

Before freezing, the protocol still needs only outcomes that cannot exist yet:
the selected A40/environment receipt, projector and mapping hashes/use counts,
three selected learning rates, the frozen implementation commit/hashes, and
the final target-registry hash. These placeholders are filled mechanically by
preflight and the 36 declared development runs; no methodology question is
open.
