"""Build and freeze the formal Phase 3 v6 scoring protocol."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from experiments.phase3.caption_template import (
    IMAGE_TOKEN_COUNT,
    MAX_SEQUENCE_LENGTH,
    USER_PROMPT,
)
from experiments.phase3_v6.scoring.common import (
    GLOBAL_SEED,
    REPO_ROOT,
    SCORING_ROOT,
    atomic_write_bytes,
    canonical_json_bytes,
    environment_receipt,
    git_output,
    read_json,
    sha256_bytes,
    sha256_file,
    source_hashes,
    source_tree_sha256,
)
from experiments.phase3_v6.scoring.input_validation import (
    EXPECTED_ASSIGNMENT_CORE_SHA256,
    EXPECTED_MODEL_IDS,
    EXPECTED_VALID_IMAGE_COUNT,
    EXPECTED_VALID_RECORD_COUNT,
    load_and_validate_frozen_inputs,
    verify_stage2_artifacts,
)


PROTOCOL_PATH = SCORING_ROOT / "protocol.json"
PROTOCOL_SHA_PATH = SCORING_ROOT / "protocol.sha256"
RUN_MANIFEST_PATH = SCORING_ROOT / "run_manifest.json"


def build_protocol(
    *,
    device: str,
    artifact_root: str | Path,
    candidate_evidence_path: str | Path,
    candidate_summary_path: str | Path,
    vision_cache_batch_size: int = 8,
    shard_size_images: int = 32,
) -> dict[str, Any]:
    frozen = load_and_validate_frozen_inputs(verify_images=True)
    verified_models = verify_stage2_artifacts(artifact_root)
    sources = source_hashes()
    evidence = Path(candidate_evidence_path)
    evidence_summary = Path(candidate_summary_path)
    if not evidence.is_file() or not evidence_summary.is_file():
        raise FileNotFoundError("candidate preflight evidence is absent")
    stage2_protocol = read_json(REPO_ROOT / "experiments/stage2_protocol_v2.json")
    protocol = {
        "schema_version": 1,
        "protocol_id": "minimind-v-phase3-v6-frozen-contrast-hull-scoring-v1",
        "status": "frozen_before_formal_model_inference",
        "git": {
            "branch": git_output("branch", "--show-current"),
            "code_commit": git_output("rev-parse", "HEAD"),
            "worktree_status_at_freeze": git_output("status", "--short"),
            "scoring_source_sha256": sources,
            "scoring_source_tree_sha256": source_tree_sha256(sources),
        },
        "frozen_inputs": {
            "sha256": frozen["input_sha256"],
            "assignment_core_sha256": frozen["assignment_core_sha256"],
            "expected_assignment_core_sha256": (
                EXPECTED_ASSIGNMENT_CORE_SHA256
            ),
            "candidate_preflight_evidence": str(
                evidence.resolve().relative_to(REPO_ROOT)
            ),
            "candidate_preflight_evidence_sha256": sha256_file(evidence),
            "candidate_preflight_summary": str(
                evidence_summary.resolve().relative_to(REPO_ROOT)
            ),
            "candidate_preflight_summary_sha256": sha256_file(
                evidence_summary
            ),
            "valid_record_count": frozen["valid_record_count"],
            "valid_target_image_count": frozen["valid_image_count"],
            "mismatch_image_union_count": frozen["mismatch_image_count"],
        },
        "record_filter": {
            "scope_flag": "certifying_formal",
            "excluded_second_round_categories": [
                "token_mapping_problem",
                "surface_only_or_degenerate",
                "invalid_sample",
            ],
            "positive_and_negative_model_token_count_at_least": 1,
            "normalized_positive_reconstruction_required": True,
            "normalized_negative_reconstruction_required": True,
            "token_boundary_mapping_required": True,
            "expected_record_count": EXPECTED_VALID_RECORD_COUNT,
            "expected_target_image_count": EXPECTED_VALID_IMAGE_COUNT,
            "equivalent_positive_sources_rule": (
                "use audit-v2 preselected deterministic positive"
            ),
        },
        "text_construction": {
            "alignment_view_role": "locate_and_validate_hull_only",
            "formal_source": "original text and original character offsets",
            "common_prefix_boundary": (
                "end of final common-prefix original lexeme in selected positive"
            ),
            "candidate_positive": "C + positive original boundary-and-hull span",
            "candidate_negative": "C + negative original boundary-and-hull span",
            "negative_uses_selected_positive_common_prefix": True,
            "natural_language_suffix_included": False,
            "template_generated_eos_present_but_unscored": True,
            "surface_cleaning_or_case_conversion": False,
            "all_4107_stitch_and_token_boundaries_prevalidated": True,
        },
        "templates": {
            "user_prompt": USER_PROMPT,
            "visual_user_content": f"<image>\\n{USER_PROMPT}",
            "model_family_template": {
                "M0": "lm_only",
                "M1": "vlm",
                "M2": "vlm",
                "M3": "vlm",
            },
            "image_token_count": IMAGE_TOKEN_COUNT,
            "maximum_sequence_length": MAX_SEQUENCE_LENGTH,
            "attention_mask": None,
        },
        "score": {
            "name": "mean_teacher_forced_hull_log_probability",
            "causal_shift": True,
            "target_mask": "formal scoring-hull model tokens only",
            "prefix_scored": False,
            "image_placeholders_scored": False,
            "padding_scored": False,
            "natural_language_suffix_scored": False,
            "eos_scored": False,
            "log_probability": "log_softmax_then_gather",
            "aggregation_dtype": "float64",
            "q": "stable_sigmoid(mean_lp_positive - mean_lp_negative)",
            "probability_clipping_or_smoothing": False,
            "generation_or_sampling": False,
            "label_smoothing": False,
        },
        "image_contexts": [
            "correct",
            "mismatch_round_1",
            "mismatch_round_2",
            "mismatch_round_3",
            "mismatch_round_4",
            "mismatch_round_5",
        ],
        "mismatch_aggregation": {
            "k1": [1],
            "k3": [1, 2, 3],
            "k5": [1, 2, 3, 4, 5],
            "d_k": "q_correct - arithmetic_mean(q_mismatch_selected_rounds)",
        },
        "image_group_aggregation": {
            "within_filename": "arithmetic mean over all valid records",
            "across_filename": "equal weight per filename",
            "primary_metric": "mu_k5",
            "win_rate_tie_rule": "strict_D_g_k5_greater_than_zero",
            "quantiles": "linear interpolation at (n-1)*p",
        },
        "category_aggregation": {
            "categories": [
                "replace_attribute",
                "replace_object",
                "replace_relation",
                "swap_atribute",
                "swap_object",
            ],
            "rule": "filename_x_category mean then equal filename mean",
        },
        "local_hull_sensitivity_analysis": {
            "label": "local_hull_sensitivity_analysis",
            "selector": (
                "max(positive_hull_token_coverage,"
                "negative_hull_token_coverage) <= 0.75"
            ),
            "may_replace_main_result": False,
        },
        "m0_invariant": {
            "formal_tolerance": 1e-8,
            "secondary_diagnostic_tolerance": 1e-6,
            "manual_zero_assignment": False,
            "six_contexts_actually_scored": True,
            "token_template_mask_identity_checked": True,
            "failure_blocks_formal_model_comparison": True,
        },
        "models": {
            "ordered_model_ids": EXPECTED_MODEL_IDS,
            "artifact_root": str(Path(artifact_root).resolve()),
            "verified_models": verified_models,
            "stage2_protocol_sha256": (
                stage2_protocol["protocol_sha256"]
                if "protocol_sha256" in stage2_protocol
                else "4a15ae6697081098973998f7340702368403fa81f39d6c8ed43172b74a55b5b3"
            ),
            "training_finetuning_or_weight_changes_allowed": False,
        },
        "execution": {
            "global_seed": GLOBAL_SEED,
            "device": device,
            "model_dtype": "float32",
            "model_eval": True,
            "inference_mode": True,
            "dropout": False,
            "autocast": False,
            "cuda_matmul_allow_tf32": False,
            "cudnn_allow_tf32": False,
            "cudnn_deterministic": True,
            "cudnn_benchmark": False,
            "shard_size_target_images": shard_size_images,
            "batch_unit": "all records and six contexts for one target filename",
            "vision_cache": {
                "mode": "model_local_cpu_memory_projected_features",
                "precompute_batch_size": vision_cache_batch_size,
                "expected_unique_images_per_visual_model": 1345,
                "expected_unique_images_per_m0_model": 0,
                "old_cache_reuse": False,
            },
        },
        "stage2_stage3_analysis": {
            "label": "descriptive_only",
            "all_ten_models_pearson_and_spearman": True,
            "seven_non_m0_auxiliary_sensitivity": True,
            "same_root_m2_m3_difference_direction": "M3_minus_M2",
            "p_values_or_strong_generalization_claims": False,
        },
        "bootstrap": {
            "enabled": False,
            "reason": "optional analysis not added to the frozen primary workflow",
        },
        "statistical_scope": (
            "fixed 1343 effective SugarCrepe++ certifying-formal image groups, "
            "fixed contrast hulls, and fixed balanced K=5 mismatch manifest"
        ),
        "claims_not_made": [
            "new unseen test set",
            "all future natural-image population guarantee",
            "new Phase 3 compression generalization bound",
            "random mismatches are equivalent to hard visual negatives",
        ],
        "environment_at_freeze": environment_receipt(device),
    }
    if protocol["git"]["branch"] != "stage3-v5-completion":
        raise ValueError("protocol can only freeze on stage3-v5-completion")
    return protocol


def freeze_protocol(**arguments: Any) -> tuple[dict[str, Any], str]:
    value = build_protocol(**arguments)
    payload = canonical_json_bytes(value, pretty=True)
    digest = sha256_bytes(payload)
    if PROTOCOL_PATH.exists():
        existing = PROTOCOL_PATH.read_bytes()
        if existing != payload:
            raise FileExistsError(
                "a different protocol.json is already frozen; refusing overwrite"
            )
    else:
        atomic_write_bytes(PROTOCOL_PATH, payload)
    sha_payload = f"{digest}  protocol.json\n".encode("ascii")
    if PROTOCOL_SHA_PATH.exists() and PROTOCOL_SHA_PATH.read_bytes() != sha_payload:
        raise FileExistsError("protocol.sha256 differs from the frozen protocol")
    if not PROTOCOL_SHA_PATH.exists():
        atomic_write_bytes(PROTOCOL_SHA_PATH, sha_payload)
    return value, digest


def verify_protocol() -> tuple[dict[str, Any], str]:
    if not PROTOCOL_PATH.is_file() or not PROTOCOL_SHA_PATH.is_file():
        raise FileNotFoundError("formal protocol has not been frozen")
    payload = PROTOCOL_PATH.read_bytes()
    digest = sha256_bytes(payload)
    expected = PROTOCOL_SHA_PATH.read_text(encoding="ascii").split()[0]
    if digest != expected:
        raise ValueError("formal protocol SHA-256 mismatch")
    value = read_json(PROTOCOL_PATH)
    current_sources = source_hashes()
    if current_sources != value["git"]["scoring_source_sha256"]:
        raise ValueError("scoring source changed after protocol freeze")
    if source_tree_sha256(current_sources) != value["git"][
        "scoring_source_tree_sha256"
    ]:
        raise ValueError("scoring source tree hash changed after protocol freeze")
    return value, digest
