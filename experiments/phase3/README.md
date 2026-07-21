# Phase 3: MiniMind-V compression generalization bounds

This directory implements the approved Phase 3 v4 protocol. It evaluates the ten frozen Stage 2 MMS2 adapters from the approved `stage2-v2-rerun-20260721` batch on SugarCrepe++ using caption-token teacher-forced Brier loss, equal-weight unique-image groups, and an IID-superpopulation Hoeffding interpretation. It never trains a model.

Phase 3 v4 retains the v3 rerun artifact authority and the permanent `phase3-v1` assignment. A human review confirmed that 44 of the 1,389 assigned formal image groups are re-encoded versions of project-history images. The overlap receipt therefore freezes those 44 exclusions and a 1,345-group certifying subset; formal execution and CPU bundle verification reject any other membership.

The permanent data split is `phase3-v1`: `sha256("phase3-v1|" + filename)`, with bucket zero assigned to pilot. The frozen assignment counts are 4,757 rows, 1,542 unique images, 153 pilot images, and 1,389 formal images. Protocol revisions do not reshuffle this split. The v4 certificate excludes 44 audited overlaps and computes formal risks and bounds on the remaining 1,345 groups.

The VLM scorer preserves the Stage 2 chat template, 64 image-pad tokens, automatic empty `<think>` wrapper, assistant EOS, and the post-EOS newline. Only caption tokens and the one assistant EOS receive labels; every other token is `-100`. Correct-image and no-pixel conditions use identical IDs and labels. M0 uses the LM-only Stage 2 template primitives and never invokes image replacement.

## Commands

Every command requires an independent `--status-output` path and writes a structured status. Run `python <command> --help` for the full contract.

1. `build_expected_model_registry.py` builds the deterministic registry from the static authority manifest.
2. `verify_stage2_artifacts.py` safely snapshots and verifies all ten MMS2 files.
3. `prepare_phase3_data.py` downloads only the five frozen SugarCrepe++ JSON sources, constructs the permanent split, verifies local COCO images, and performs token preflight.
4. `audit_training_overlap.py` evaluates the seven project-controlled training/model-selection scopes and emits the exact 44/1,345 exclusion partition bound to the human review.
5. `run_phase3_smoke_v2.py` runs M1 on the first eight pilot image groups when resources are ready.
6. `run_phase3_pilot_v2.py` and `run_phase3_formal_v2.py` enforce the frozen protocol. Pilot is non-certifying; formal execution remains impossible until every gate, including the user-supplied approval, passes.
7. `build_phase3_bundle.py` creates a new privacy-sanitized public bundle from a successful run.
8. `verify_phase3_bundle.py` independently recomputes bundle hashes, group aggregation, risks, M0 rules, and NLL summaries on CPU. It checks internal consistency and provenance bindings; it does not re-prove GPU logits.

## Tests

Run:

```bash
python -m unittest discover -s tests -p "test_phase3_*.py"
python -m unittest discover -s tests -p "test*.py"
```

All pure Phase 3 tests are offline, CPU-only, and synthetic. Only the explicit Stage 2 integration test may report `blocked_integration_fixture` when verified M1, strict confirmation validation, assets, or a GPU are unavailable.

## Certification boundary

Smoke and pilot are non-certifying and store null bounds. Formal certification requires the manually frozen two-commit/tag history, complete artifact and data receipts, the bound overlap-exclusion receipt, explicit user approval, and the exact protocol hash. The certificate targets the distribution represented by SugarCrepe++ conditional on no project-history image overlap under stated IID and model-independence assumptions; it is neither a finite-population guarantee for 1,542 fixed images nor a claim about all natural images.
