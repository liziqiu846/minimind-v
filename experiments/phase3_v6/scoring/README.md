# Phase 3 v6 frozen contrast-hull scoring

This directory is an independent scoring implementation. It does not modify the
Phase 2 models, the Phase 3 v4/v5 implementation, either contrast-hull audit, or
the frozen mismatch assignment.

The formal statistic is the image-group-equal mean difference between the
correct-image semantic preference and the fixed K=5 mismatch-image semantic
preference. Each semantic preference is a stable sigmoid of the difference
between positive- and negative-hull mean teacher-forced log probabilities.

Formal execution order:

1. validate immutable inputs and the ten-model registry;
2. prevalidate all 4,107 original-text candidate stitches and token masks;
3. run unit tests and the two-record real-model smoke run;
4. freeze and hash `protocol.json`;
5. score the ten frozen models with model-local projected-feature caches;
6. enforce the M0 `1e-8` invariant before model comparison;
7. aggregate records within filename and filenames with equal weight;
8. reproduce summaries, compare to frozen Stage 2 metrics, and write a receipt.

`local_hull_sensitivity_analysis` always means
`max(positive_hull_token_coverage, negative_hull_token_coverage) <= 0.75`.
It never replaces the complete 1,343-image main result.

