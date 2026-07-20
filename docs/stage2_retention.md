# Stage 2 compact-retention policy

## Purpose

Stage 2 is complete and its core result bundle is published. This checkout is
therefore maintained as a compact code-and-results repository rather than as a
live training workspace. Large files that can be regenerated from frozen code,
protocols, seeds, and immutable source assets are not retained here.

## Retained

- all tracked implementation, tests, frozen protocols, annotated-tag history,
  environment receipts, and history-exclusion receipts;
- `docs/stage2_v1_closeout.md` and `docs/stage2_v2_closeout.md`;
- the four authoritative v1 audit receipts under
  `experiments/audits/stage2_v1/`;
- the compact v2 result bundle under
  `experiments/runs/stage2_v2_fast/final/`;
- the first-finalization race audit receipt, without its five superseded
  duplicate reports.

## Removed after successful publication

- `dataset/stage2_confirm_seed2026/` (about 95 MiB);
- `dataset/stage2_confirm_v2_seed2028/` (about 387 MiB);
- v1 development, smoke, preflight, and formal-run intermediates under
  `experiments/runs/stage2/` (about 75 MiB, including the ignored local copy of
  the final report; the tracked v1 closeout and four audits remain);
- the superseded interrupted single-GPU v2 run under
  `experiments/runs/stage2_v2/` (about 8.4 MiB);
- the complete dynamic-run working directory under
  `experiments/runs/stage2_v2_fast/formal/` (about 37 MiB);
- Python and test caches;
- five duplicate report files from the audited first-finalization race.

The removed material included parquet copies, membership/exposure JSONL,
training checkpoints, coordinate tensors, encoded/decoded adapters, per-draw
risk vectors, stage logs, dry-run plans, and obsolete failure/recovery outputs.

## Regeneration boundary

The frozen source dataset remains outside this repository at
`/home/lizhaohui/lzq/stage2-assets-v1/dataset/pretrain_i2t.parquet`, with
SHA-256
`65761f37d1947d54a1d85457ff70938275e4ef58ba5cedcd02463a3a247c93fd`.
The code and protocol tags contain the deterministic catalog/draw rules and
all seeds needed to regenerate confirmation data and rerun the experiment.

The retained `stage2_artifact_manifest.json` and `completion_audit.json` record
the fully populated state before cleanup. They are historical evidence: a
compact checkout is expected to fail a full 268-artifact replay because the raw
artifacts were intentionally removed. This does not alter the hashes or
conclusions in the published final report.

## Git landmarks

- frozen dynamic execution protocol: `stage2-protocol-v2-fast-multigpu`;
- published full result bundle: `stage2-v2-fast-results`;
- compact-retention cleanup: the commit that adds this document.

Checking out an earlier Git tag restores tracked code and compact report files,
but never restores the untracked large datasets or run intermediates. Those
must be regenerated from the immutable source assets.
