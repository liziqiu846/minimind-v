"""Phase 3 v5 protocol validation and one-way code-manifest binding."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import subprocess
from typing import Any

from experiments.phase3.canonical_io import (
    canonical_json_bytes,
    load_json_snapshot,
    parse_canonical_json_bytes,
    sha256_bytes,
    snapshot_file,
)
from experiments.phase3.phase3_protocol import (
    ARTIFACT_BATCH_ID,
    CONDITIONAL_TARGET_DISTRIBUTION,
    MODEL_ORDER,
    OVERLAP_PASS_STATUS,
    PROMPT_REVISION,
    REPO_ROOT,
    SPLIT_VERSION,
    STAGE2_PROTOCOL_SHA256,
    STAGE2_REFERENCE_COMMIT,
)


PROTOCOL_VERSION_V5 = "phase3-v5"
PROTOCOL_TAG_V5 = "phase3-protocol-v5"
POST_HOC_STATUS_V5 = "post_hoc_metric_selected_after_v4_formal_results_available"
SOURCE_FILES_V5 = (
    ("replace_attribute", "data/replace_att.json", 788, 226275, "6826413592894754eeca02aeebbcbbc8b95a7456998abcc714e71c033ce6fe87"),
    ("replace_object", "data/replace_obj.json", 1652, 456601, "5c6dc499ec8f511a8aa4ec1b7b5eb0eca90317488abe36ec39573355e2d361ab"),
    ("replace_relation", "data/replace_rel.json", 1406, 392738, "040fb95d3f0619bf515db60879e99709a87a5e9b4f524ec3403b127243480fd4"),
    ("swap_atribute", "data/swap_att.json", 666, 198206, "450d0fd9fcad3e6f44950dc634e7f901ab1c6d9c60a569ade5ae8ffb3d203ad8"),
    ("swap_object", "data/swap_obj.json", 245, 74611, "5f33cae824de431a7ecd3c5de6301f689815f9497aa36d96b154bbaf117b201b"),
)


def build_protocol_payload_v5(code_manifest_sha256: str) -> dict[str, Any]:
    if not re.fullmatch(r"[0-9a-f]{64}", code_manifest_sha256):
        raise ValueError("invalid v5 code-manifest SHA-256")
    return {
        "schema_version": 1,
        "prompt_revision": PROMPT_REVISION,
        "protocol_version": PROTOCOL_VERSION_V5,
        "split_version": SPLIT_VERSION,
        "stage2_reference_commit": STAGE2_REFERENCE_COMMIT,
        "stage2_artifact_batch_id": ARTIFACT_BATCH_ID,
        "stage2_protocol_sha256": STAGE2_PROTOCOL_SHA256,
        "phase3_code_manifest_sha256": code_manifest_sha256,
        "stage2_authority_manifest_sha256": "af98ff7bc219f0954a5f0c9e5496f88f0ea9da5de0528ee2c4cb2480c5846366",
        "expected_model_registry_sha256": "0f989d1a97a2069a2b615bc3338887d49dcb87907908dec2e0ac8fbd7524070c",
        "data_manifest_sha256": "2effb7fbdc763ed1870ba943d30a9cd68be7c6be15ead9892b8c69da62918405",
        "split_manifest_sha256": "6d9ca71c04435f0d9c9aaa932def8d5078822d65996fcc846fdb1a9604f06aff",
        "overlap_audit_input_sha256": "24f62b288d2ae60acd243e4c74fdc623ee84e57837b02f015d6bd433cd84068d",
        "overlap_audit_receipt_sha256": "a9c666c9fa0835fcc19dc28397e55b9a4e814ee9406d98bc8c85027ea9a3ac6d",
        "excluded_formal_images_sha256": "d4d55261f20b36c719c1b84bbd7d2c50dae154fcb14916728461e79c1cb54412",
        "certifying_formal_filenames_sha256": "afb73f300dfbff0c60fd207a3f65c8950448cd2266cc2c8eb0f04b4a41643329",
        "dataset": {
            "repo": "Aman-J/SugarCrepe_pp",
            "revision": "dea2a1b6f9e1069c609f676aa55ec61e9b65fb61",
            "split": "train",
            "source_files": [
                {
                    "config": config,
                    "repository_relative_path": relative,
                    "row_count": rows,
                    "size_bytes": size,
                    "sha256": digest,
                }
                for config, relative, rows, size, digest in SOURCE_FILES_V5
            ],
            "row_count": 4757,
            "unique_image_count": 1542,
        },
        "split": {
            "salt": "phase3-v1",
            "rule": "sha256('phase3-v1|'+filename) first16hex mod10; zero=pilot",
            "pilot_unique_images": 153,
            "formal_unique_images": 1389,
            "excluded_formal_unique_images": 44,
            "certifying_formal_unique_images": 1345,
            "independent_unit": "unique_image_filename_group",
            "split_manifest_summary": {
                "canonical_row_commitment_sha256": "2733e8642d8f23f05efc4bcc135182db16fee19fd5f67117a2cdcfa9a075fd5c",
                "total_rows": 4757,
                "total_unique_images": 1542,
            },
        },
        "models": {
            "ordered_model_ids": list(MODEL_ORDER),
            "decoder_id": "stage2-v2-mms2",
            "decoder_source_sha256": "d42a0f0eecfd3c6977d04a3f446c48369e9505dd65d1c5f577b4e92ccc6cf785",
        },
        "conversation": {
            "vlm": [
                {"role": "user", "content": "<image>\nDescribe the image in one sentence."},
                {"role": "assistant", "content": "<caption>"},
            ],
            "lm_only": [
                {"role": "user", "content": "Describe the image in one sentence."},
                {"role": "assistant", "content": "<caption>"},
            ],
            "automatic_empty_think_preserved": True,
            "valid_labels": "raw_caption_tokens_plus_unique_assistant_eos",
            "masked_labels": ["user", "image_pad", "assistant_marker", "empty_think", "post_eos_newline", "padding"],
            "image_token_count": 64,
            "max_sequence_length": 450,
            "attention_mask": None,
        },
        "image_preprocessing": "Pillow decode -> EXIF transpose -> RGB -> frozen Stage2 SigLIP processor",
        "scoring": {
            "causal_shift": "float32_logits[:, :-1, :] score labels[:, 1:]",
            "brier": "mean_valid(sum(p^2)-2*p_y+1), then caption-level clip to [0,2]",
            "nll_diagnostic": "unsmoothed -log(p_y)/ln(2), bits/token, non-certifying",
            "summary_float": "float64",
        },
        "primary_risks": {
            "robust_positive_brier_risk": {"support": [0.0, 2.0]},
            "visual_semantic_loss": {"support": [0.0, 1.0]},
        },
        "non_primary_diagnostics": [
            "positive_brier_mean", "positive_brier_dispersion", "image_robust_margin",
            "none_robust_margin", "visual_increment", "triplet_success",
            "lm_triplet_success", "visual_increment_success", "unsmoothed_nll_tails",
            "five_category_stratified_results",
        ],
        "m0": {
            "image_fields": None,
            "positive_source": "lm_only_observed_robust_max",
            "visual_increment": 0.0,
            "visual_semantic_loss": 0.5,
            "visual_metric_source": "definition_constant_lm_only",
            "fixed_visual_bound_method": "definition_constant",
            "compression_visual_bound_method": "definition_constant",
        },
        "aggregation": "canonical row -> within(model,filename) float64 mean -> equal-weight unique-image mean",
        "estimand": {
            "sampling_assumption": "iid_superpopulation",
            "target_distribution": CONDITIONAL_TARGET_DISTRIBUTION,
            "not_finite_population_guarantee": True,
            "not_all_natural_images": True,
            "external_base_pretraining_overlap": "unknown",
        },
        "bounds": {
            "global_delta_total": 0.05,
            "fixed_model": {"delta_total": 0.025, "comparison_slots": 20, "delta_each": 0.025 / 20},
            "compression": {"delta_total": 0.025, "comparison_slots": 20, "delta_each": 0.025 / 20},
            "compression_description": "complete_mms2_file_bytes_times_8_plus_4_candidate_id_bits",
            "retain_raw_and_capped_upper_bounds": True,
            "visual_increment_lower_uses_raw_upper": True,
        },
        "statistical_interpretation": {
            "selection_status": POST_HOC_STATUS_V5,
            "simultaneous_95_percent_coverage_claim": False,
            "disclosure": "v5 metrics may have been selected after v4 Formal values were viewed",
        },
        "overlap": {
            "ruleset_id": "phase3-project-image-overlap-exclusion-v2",
            "scope_ids": [
                "phase1_training", "phase1_model_selection", "stage2_adapter_training",
                "stage2_quantization_aware_training", "stage2_hyperparameter_selection",
                "stage2_development_validation", "stage2_other_model_selection",
            ],
            "assigned_formal_unique_images": 1389,
            "excluded_formal_unique_images": 44,
            "certifying_formal_unique_images": 1345,
            "exclusion_rule": "exclude exact matches and human-confirmed same-source probable pairs",
            "formal_pass_status": OVERLAP_PASS_STATUS,
            "external_base_pretraining_overlap": "unknown",
        },
        "execution": {
            "training_allowed": False,
            "model_dtype": "float32",
            "inference_mode": True,
            "model_eval": True,
            "autocast_enabled": False,
            "cuda_matmul_allow_tf32": False,
            "cudnn_allow_tf32": False,
            "cudnn_benchmark": False,
            "cudnn_deterministic": True,
            "global_seed": 3407,
            "item_batch_size_unique_image_groups": 1,
            "formal_shard_size_unique_images": 32,
            "protocol_tag": PROTOCOL_TAG_V5,
        },
        "protocol_lifecycle": "external_filename_tag_and_freeze_receipt; candidate_and_frozen_json_bytes_identical",
        "training_allowed": False,
    }


@dataclass(frozen=True)
class Phase3ProtocolV5:
    path: Path
    payload: dict[str, Any]
    raw_sha256: str

    @classmethod
    def load(cls, path: str | Path) -> "Phase3ProtocolV5":
        target = Path(path)
        raw = snapshot_file(target)
        payload = parse_canonical_json_bytes(raw, name=target.name)
        if not isinstance(payload, dict):
            raise ValueError("v5 protocol must be an object")
        result = cls(target, payload, sha256_bytes(raw))
        result.validate()
        return result

    def validate(self) -> None:
        digest = self.payload.get("phase3_code_manifest_sha256")
        if not isinstance(digest, str):
            raise ValueError("v5 protocol code-manifest binding missing")
        expected = build_protocol_payload_v5(digest)
        if self.payload != expected:
            raise ValueError("v5 protocol differs from the fixed schema or values")

    @property
    def kind(self) -> str:
        return "candidate" if "candidate" in self.path.name else "frozen"

    def require_frozen(self) -> None:
        if self.path.name != "phase3_protocol_frozen_v5.json":
            raise ValueError("formal v5 execution requires the frozen protocol filename")


def enumerate_code_paths_v5(repo_root: str | Path = REPO_ROOT) -> list[Path]:
    root = Path(repo_root)
    paths = set((root / "experiments/phase3").rglob("*.py"))
    for relative in (
        "experiments/phase3/README.md",
        "experiments/phase3/code_audit_v5.md",
        "experiments/phase3/phase3_runtime_paths.template.env",
        "docs/phase3_theory_v5.md",
    ):
        path = root / relative
        if path.is_file():
            paths.add(path)
    paths.update((root / "tests").glob("test_phase3_*.py"))
    fixture_root = root / "tests/fixtures/phase3"
    if fixture_root.is_dir():
        paths.update(path for path in fixture_root.rglob("*") if path.is_file())
    for path in paths:
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"invalid v5 code-manifest member: {path}")
    return sorted(paths, key=lambda path: path.relative_to(root).as_posix().encode("utf-8"))


def build_code_manifest_v5(repo_root: str | Path = REPO_ROOT) -> dict[str, Any]:
    root = Path(repo_root)
    files = []
    for path in enumerate_code_paths_v5(root):
        raw = snapshot_file(path, root=root)
        files.append(
            {"relative_path": path.relative_to(root).as_posix(), "size_bytes": len(raw), "sha256": sha256_bytes(raw)}
        )
    return {
        "schema_version": 1,
        "manifest_type": "phase3_code_manifest_v5",
        "inclusion_rule_id": "phase3-v5-executable-doc-test-files-v1",
        "file_count": len(files),
        "files": files,
        "exclusion_rule": "protocols, manifests, approval files, receipts, dynamic outputs, caches, and non-v5 JSON are excluded",
    }


def verify_code_manifest_v5(path: str | Path, repo_root: str | Path = REPO_ROOT) -> dict[str, Any]:
    payload = load_json_snapshot(path)
    if payload != build_code_manifest_v5(repo_root):
        raise ValueError("Phase 3 v5 code manifest differs from current included bytes")
    return payload


def frozen_repository_binding_v5(protocol: Phase3ProtocolV5) -> dict[str, str]:
    protocol.require_frozen()
    result = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "rev-parse", f"{PROTOCOL_TAG_V5}^{{commit}}"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False,
    )
    if result.returncode != 0 or not re.fullmatch(r"[0-9a-f]{40}\n?", result.stdout):
        raise ValueError("v5 protocol tag is missing or invalid")
    commit = result.stdout.strip()
    tagged = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "show", f"{commit}:experiments/phase3/phase3_protocol_frozen_v5.json"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    if tagged.returncode != 0 or tagged.stdout != snapshot_file(protocol.path):
        raise ValueError("frozen v5 protocol bytes differ from tagged freeze commit")
    ancestor = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "merge-base", "--is-ancestor", commit, "HEAD"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    if ancestor.returncode != 0:
        raise ValueError("current HEAD is not a descendant of the v5 freeze tag")
    return {"protocol_repository_commit": commit, "protocol_tag": PROTOCOL_TAG_V5}
