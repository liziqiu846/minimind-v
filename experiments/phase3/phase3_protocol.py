"""Phase 3 protocol loading, validation, and code-manifest enumeration."""

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


REPO_ROOT = Path(__file__).resolve().parents[2]
STAGE2_REFERENCE_COMMIT = "9c575c617dd399dda73996e4e7e6e1f5614ee0d1"
PROTOCOL_VERSION = "phase3-v4"
SPLIT_VERSION = "phase3-v1"
PROTOCOL_TAG = "phase3-protocol-v4"
ARTIFACT_BATCH_ID = "stage2-v2-rerun-20260721"
PROMPT_REVISION = "phase3-prompt-v2.3-overlap-exclusion-approved"
STAGE2_PROTOCOL_SHA256 = "4a15ae6697081098973998f7340702368403fa81f39d6c8ed43172b74a55b5b3"
MODEL_ORDER = (
    "M0-root-43101", "M0-root-43102", "M0-root-43103", "M1-root-none",
    "M2-root-43101", "M2-root-43102", "M2-root-43103",
    "M3-root-43101", "M3-root-43102", "M3-root-43103",
)
CONDITIONAL_TARGET_DISTRIBUTION = (
    "SugarCrepe++ represented target image-text construction distribution conditional on "
    "no project-history image overlap"
)
OVERLAP_PASS_STATUS = "certification_subset_project_disjoint_under_frozen_checks"


@dataclass(frozen=True)
class Phase3Protocol:
    path: Path
    payload: dict[str, Any]
    raw_sha256: str

    @classmethod
    def load(cls, path: str | Path) -> "Phase3Protocol":
        target = Path(path)
        raw = snapshot_file(target)
        payload = parse_canonical_json_bytes(raw, name=target.name)
        if not isinstance(payload, dict):
            raise ValueError("protocol must be a JSON object")
        instance = cls(target, payload, sha256_bytes(raw))
        instance.validate()
        return instance

    def validate(self) -> None:
        if self.payload.get("schema_version") != 1:
            raise ValueError("protocol schema_version mismatch")
        if self.payload.get("prompt_revision") != PROMPT_REVISION:
            raise ValueError("prompt_revision mismatch")
        if self.payload.get("protocol_version") != PROTOCOL_VERSION:
            raise ValueError("protocol_version mismatch")
        if self.payload.get("split_version") != SPLIT_VERSION:
            raise ValueError("split_version mismatch")
        if self.payload.get("stage2_reference_commit") != STAGE2_REFERENCE_COMMIT:
            raise ValueError("stage2 reference commit mismatch")
        if self.payload.get("stage2_artifact_batch_id") != ARTIFACT_BATCH_ID:
            raise ValueError("Stage 2 artifact batch mismatch")
        if self.payload.get("stage2_protocol_sha256") != STAGE2_PROTOCOL_SHA256:
            raise ValueError("Stage 2 protocol SHA mismatch")
        if self.payload.get("split", {}).get("salt") != "phase3-v1":
            raise ValueError("protocol split salt mismatch")
        split = self.payload.get("split", {})
        if set(split) != {
            "salt", "rule", "pilot_unique_images", "formal_unique_images",
            "excluded_formal_unique_images", "certifying_formal_unique_images",
            "independent_unit", "split_manifest_summary",
        }:
            raise ValueError("protocol split schema mismatch")
        if (
            split.get("rule") != "sha256('phase3-v1|'+filename) first16hex mod10; zero=pilot"
            or split.get("pilot_unique_images") != 153
            or split.get("formal_unique_images") != 1389
            or split.get("excluded_formal_unique_images") != 44
            or split.get("certifying_formal_unique_images") != 1345
            or split.get("independent_unit") != "unique_image_filename_group"
        ):
            raise ValueError("protocol split counts/unit mismatch")
        models = self.payload.get("models", {})
        if set(models) != {"ordered_model_ids", "decoder_id", "decoder_source_sha256"}:
            raise ValueError("protocol models schema mismatch")
        if (
            models.get("ordered_model_ids") != list(MODEL_ORDER)
            or models.get("decoder_id") != "stage2-v2-mms2"
            or models.get("decoder_source_sha256")
            != "d42a0f0eecfd3c6977d04a3f446c48369e9505dd65d1c5f577b4e92ccc6cf785"
        ):
            raise ValueError("protocol model order mismatch")
        conversation = self.payload.get("conversation", {})
        if set(conversation) != {
            "vlm", "lm_only", "automatic_empty_think_preserved", "valid_labels",
            "masked_labels", "image_token_count", "max_sequence_length", "attention_mask",
        }:
            raise ValueError("protocol conversation schema mismatch")
        if (
            conversation.get("attention_mask") is not None
            or conversation.get("image_token_count") != 64
            or conversation.get("max_sequence_length") != 450
            or conversation.get("automatic_empty_think_preserved") is not True
            or conversation.get("valid_labels") != "raw_caption_tokens_plus_unique_assistant_eos"
            or conversation.get("masked_labels")
            != ["user", "image_pad", "assistant_marker", "empty_think", "post_eos_newline", "padding"]
            or conversation.get("vlm") != [
                {"role": "user", "content": "<image>\nDescribe the image in one sentence."},
                {"role": "assistant", "content": "<caption>"},
            ]
            or conversation.get("lm_only") != [
                {"role": "user", "content": "Describe the image in one sentence."},
                {"role": "assistant", "content": "<caption>"},
            ]
        ):
            raise ValueError("protocol conversation/label contract mismatch")
        dataset = self.payload.get("dataset", {})
        if set(dataset) != {"repo", "revision", "split", "source_files", "row_count", "unique_image_count"} or any(
            (
                dataset.get("repo") != "Aman-J/SugarCrepe_pp",
                dataset.get("revision") != "dea2a1b6f9e1069c609f676aa55ec61e9b65fb61",
                dataset.get("split") != "train",
                dataset.get("row_count") != 4757,
                dataset.get("unique_image_count") != 1542,
            )
        ):
            raise ValueError("protocol dataset contract mismatch")
        if self.payload.get("main_risks") != {
            "positive_brier_risk": {"support": [0.0, 2.0]},
            "visual_semantic_loss": {"support": [0.0, 1.0]},
            "positive_invariance_loss": {"support": [0.0, 1.0]},
        }:
            raise ValueError("protocol main-risk support mismatch")
        if self.payload.get("m0") != {
            "image_fields": None,
            "positive_source": "lm_only_observed",
            "visual_increment": 0.0,
            "visual_semantic_loss": 0.5,
            "visual_metric_source": "definition_constant_lm_only",
            "visual_bound_method": "definition_constant",
        }:
            raise ValueError("protocol M0 definition mismatch")
        if self.payload.get("training_allowed") is not False:
            raise ValueError("Phase 3 training must remain forbidden")
        execution = self.payload.get("execution", {})
        if set(execution) != {
            "global_seed", "item_batch_size_unique_image_groups", "model_eval",
            "inference_mode", "autocast_enabled", "model_dtype", "cudnn_deterministic",
            "cudnn_benchmark", "cuda_matmul_allow_tf32", "cudnn_allow_tf32",
            "formal_shard_size_unique_images", "formal_nonblocking_exclusive_lock",
            "protocol_tag", "approval_statement",
        }:
            raise ValueError("protocol execution schema mismatch")
        if execution.get("protocol_tag") != PROTOCOL_TAG:
            raise ValueError("protocol annotated tag name mismatch")
        if any(
            (
                execution.get("global_seed") != 3407,
                execution.get("item_batch_size_unique_image_groups") != 1,
                execution.get("model_eval") is not True,
                execution.get("inference_mode") is not True,
                execution.get("autocast_enabled") is not False,
                execution.get("model_dtype") != "float32",
                execution.get("cudnn_deterministic") is not True,
                execution.get("cudnn_benchmark") is not False,
                execution.get("cuda_matmul_allow_tf32") is not False,
                execution.get("cudnn_allow_tf32") is not False,
                execution.get("formal_shard_size_unique_images") != 32,
                execution.get("formal_nonblocking_exclusive_lock") != ".phase3.lock",
                execution.get("approval_statement") != "Primary metrics and formal split are frozen.",
            )
        ):
            raise ValueError("protocol execution/determinism contract mismatch")
        if self.payload.get("image_preprocessing") != "Pillow decode -> EXIF transpose -> RGB -> frozen Stage2 SigLIP processor":
            raise ValueError("protocol image preprocessing mismatch")
        if self.payload.get("aggregation") != "canonical row -> within(model,filename) float64 mean -> equal-weight unique-image mean":
            raise ValueError("protocol aggregation mismatch")
        if self.payload.get("scoring") != {
            "causal_shift": "float32_logits[:, :-1, :] score labels[:, 1:]",
            "brier": "mean_valid(sum(p^2)-2*p_y+1), then caption-level clip to [0,2]",
            "nll_diagnostic": "unsmoothed -log(p_y)/ln(2), bits/token, non-certifying",
            "summary_float": "float64",
        }:
            raise ValueError("protocol scoring mismatch")
        if self.payload.get("estimand") != {
            "sampling_assumption": "iid_superpopulation",
            "target_distribution": CONDITIONAL_TARGET_DISTRIBUTION,
            "not_finite_population_guarantee": True,
            "not_all_natural_images": True,
            "complete_model_formal_independence_requires_user_acceptance": True,
        }:
            raise ValueError("protocol estimand mismatch")
        if self.payload.get("bounds") != {
            "main": {
                "delta_total": 0.05, "comparison_slots": 30,
                "delta_each": 0.05 / 30, "method": "hoeffding_iid_superpopulation",
            },
            "compression": {
                "delta_total": 0.05, "comparison_slots": 30,
                "delta_each": 0.05 / 30, "separate_from_main": True,
            },
        }:
            raise ValueError("protocol bound-family mismatch")
        if self.payload.get("overlap") != {
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
        }:
            raise ValueError("protocol overlap contract mismatch")
        kind = self.payload.get("protocol_kind")
        if kind not in ("candidate", "frozen"):
            raise ValueError("unknown protocol_kind")
        hex64 = re.compile(r"[0-9a-f]{64}")
        for key in (
            "phase3_code_manifest_sha256", "stage2_authority_manifest_sha256",
            "expected_model_registry_sha256",
        ):
            if not isinstance(self.payload.get(key), str) or not hex64.fullmatch(self.payload[key]):
                raise ValueError(f"protocol static hash is invalid: {key}")
        if kind == "candidate":
            expected_top = {
                "schema_version", "prompt_revision", "protocol_version", "split_version",
                "protocol_kind", "candidate_status", "missing_required_fields",
                "phase3_source_commit", "stage2_reference_commit", "stage2_artifact_batch_id",
                "stage2_protocol_sha256", "phase3_code_manifest_sha256",
                "stage2_authority_manifest_sha256", "expected_model_registry_sha256",
                "data_manifest_sha256", "split_manifest_sha256", "overlap_audit_input_sha256",
                "dataset", "split", "models", "conversation", "image_preprocessing",
                "scoring", "main_risks", "m0", "aggregation", "estimand", "bounds",
                "overlap", "execution", "training_allowed",
            }
            if set(self.payload) != expected_top:
                raise ValueError("candidate protocol top-level schema mismatch")
            if self.payload.get("phase3_source_commit") is not None:
                raise ValueError("candidate phase3_source_commit must be null")
            missing = self.payload.get("missing_required_fields")
            if self.payload.get("candidate_status") not in ("incomplete", "ready_for_user_freeze") or not isinstance(missing, list):
                raise ValueError("candidate status/missing fields are invalid")
            expected_status = "incomplete" if missing else "ready_for_user_freeze"
            if self.payload["candidate_status"] != expected_status:
                raise ValueError("candidate status disagrees with missing fields")
            if not missing and (
                not isinstance(dataset.get("source_files"), list)
                or split.get("split_manifest_summary") is None
            ):
                raise ValueError("freeze-ready candidate lacks complete data summaries")
        else:
            expected_top = {
                "schema_version", "prompt_revision", "protocol_version", "split_version",
                "protocol_kind", "freeze_status", "phase3_source_commit", "protocol_tag",
                "stage2_reference_commit", "stage2_artifact_batch_id", "stage2_protocol_sha256",
                "phase3_code_manifest_sha256", "stage2_authority_manifest_sha256",
                "expected_model_registry_sha256", "data_manifest_sha256",
                "split_manifest_sha256", "overlap_audit_input_sha256", "dataset", "split",
                "models", "conversation", "image_preprocessing", "scoring", "main_risks",
                "m0", "aggregation", "estimand", "bounds", "overlap", "execution",
                "training_allowed",
            }
            if set(self.payload) != expected_top:
                raise ValueError("frozen protocol top-level schema mismatch")
            if self.payload.get("freeze_status") != "frozen" or self.payload.get("protocol_tag") != PROTOCOL_TAG:
                raise ValueError("frozen protocol marker/tag mismatch")
            if self.payload.get("missing_required_fields") not in (None, []):
                raise ValueError("frozen protocol cannot retain missing fields")
            for key in ("data_manifest_sha256", "split_manifest_sha256", "overlap_audit_input_sha256"):
                if not isinstance(self.payload.get(key), str) or not hex64.fullmatch(self.payload[key]):
                    raise ValueError(f"frozen protocol hash is invalid: {key}")

    @property
    def kind(self) -> str:
        return str(self.payload.get("protocol_kind"))

    def require_frozen(self) -> None:
        if self.kind != "frozen" or self.payload.get("freeze_status") != "frozen":
            raise ValueError("formal execution requires a frozen protocol")
        source = self.payload.get("phase3_source_commit")
        if not isinstance(source, str) or len(source) != 40:
            raise ValueError("frozen protocol requires phase3_source_commit")


def enumerate_code_paths(repo_root: str | Path = REPO_ROOT) -> list[Path]:
    root = Path(repo_root)
    paths = set((root / "experiments/phase3").rglob("*.py"))
    readme = root / "experiments/phase3/README.md"
    if readme.exists():
        paths.add(readme)
    paths.update((root / "tests").glob("test_phase3_*.py"))
    fixture_root = root / "tests/fixtures/phase3"
    if fixture_root.exists():
        for path in fixture_root.rglob("*"):
            relative_parts = path.relative_to(fixture_root).parts
            excluded = any(part == "__pycache__" or part.startswith(".") for part in relative_parts)
            excluded = excluded or path.name.endswith((".pyc", ".pyo", ".swp", "~"))
            if excluded:
                continue
            if path.is_symlink() or (path.exists() and not path.is_file()):
                raise ValueError(f"invalid fixture path: {path}")
            if path.is_file():
                paths.add(path)
    for path in paths:
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"invalid code-manifest path: {path}")
    return sorted(paths, key=lambda path: path.relative_to(root).as_posix().encode("utf-8"))


def build_code_manifest(repo_root: str | Path = REPO_ROOT) -> dict[str, Any]:
    root = Path(repo_root)
    files = []
    for path in enumerate_code_paths(root):
        payload = snapshot_file(path, root=root)
        files.append(
            {
                "relative_path": path.relative_to(root).as_posix(),
                "size_bytes": len(payload),
                "sha256": sha256_bytes(payload),
            }
        )
    return {
        "schema_version": 1,
        "manifest_type": "phase3_code_manifest_v2",
        "inclusion_rule_id": "phase3-code-files-v2",
        "file_count": len(files),
        "files": files,
        "exclusion_rule": (
            "the code manifest/sidecar, protocol and other JSON, dynamic outputs, Python caches, "
            "and the explicitly excluded fixture temporary names are outside phase3-code-files-v2"
        ),
    }


def verify_code_manifest(path: str | Path, repo_root: str | Path = REPO_ROOT) -> dict[str, Any]:
    payload = load_json_snapshot(path)
    expected = build_code_manifest(repo_root)
    if payload == expected:
        return payload
    # The immutable v4 manifest intentionally continues to describe the v4
    # freeze commit after additive v5 files and the version-dispatch refactor
    # exist in the current tree.  Validate that historical tree rather than
    # weakening or rewriting the frozen v4 artifact.
    raw = snapshot_file(path)
    if (
        Path(path).name != "phase3_code_manifest_v2.json"
        or sha256_bytes(raw) != "6e04c2ba7de3781023bc3c807ef91cc6b5c29955ab32a3b2cef503fae6a84048"
    ):
        raise ValueError("Phase 3 code manifest differs from the current inclusion set or bytes")
    source_commit = "5d9602dd7933f87409d9811fc1f2298b6cc8a790"
    committed_manifest = subprocess.run(
        ["git", "-C", str(repo_root), "show", f"{source_commit}:experiments/phase3/phase3_code_manifest_v2.json"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    if committed_manifest.returncode != 0 or committed_manifest.stdout != raw:
        raise ValueError("frozen v4 code manifest is not the source-commit artifact")
    rows = payload.get("files")
    if not isinstance(rows, list) or len(rows) != payload.get("file_count"):
        raise ValueError("frozen v4 code manifest schema mismatch")
    for row in rows:
        blob = subprocess.run(
            ["git", "-C", str(repo_root), "show", f"{source_commit}:{row['relative_path']}"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
        )
        if (
            blob.returncode != 0
            or len(blob.stdout) != row.get("size_bytes")
            or sha256_bytes(blob.stdout) != row.get("sha256")
        ):
            raise ValueError(f"frozen v4 manifest member mismatch: {row.get('relative_path')}")
    return payload


def frozen_repository_binding(protocol: Phase3Protocol) -> dict[str, str]:
    """Resolve and verify the non-self-referential A/B/annotated-tag binding."""
    protocol.require_frozen()

    def git(*arguments: str) -> str:
        result = subprocess.run(
            ["git", "-C", str(REPO_ROOT), *arguments],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            raise ValueError(f"git binding check failed: {' '.join(arguments)}")
        return result.stdout.strip()

    if git("cat-file", "-t", f"refs/tags/{PROTOCOL_TAG}") != "tag":
        raise ValueError("Phase 3 protocol tag is missing or is not annotated")
    tag_object = git("rev-parse", f"refs/tags/{PROTOCOL_TAG}")
    repository_commit = git("rev-parse", f"refs/tags/{PROTOCOL_TAG}^{{commit}}")
    head = git("rev-parse", "HEAD")
    source = protocol.payload["phase3_source_commit"]
    if head != repository_commit:
        raise ValueError("HEAD does not match Phase 3 annotated-tag target")
    if git("rev-list", "--parents", "-n", "1", source) != f"{source} {STAGE2_REFERENCE_COMMIT}":
        raise ValueError("Phase 3 source commit A has the wrong parent")
    if git("rev-list", "--parents", "-n", "1", repository_commit) != f"{repository_commit} {source}":
        raise ValueError("Phase 3 protocol commit B is not the direct child of A")
    source_diff = git("diff", "--name-status", STAGE2_REFERENCE_COMMIT, source)
    for line in source_diff.splitlines():
        status, relative = line.split("\t", 1)
        if status != "A" or not (
            relative.startswith("experiments/phase3/")
            or relative.startswith("tests/fixtures/phase3/")
            or (relative.startswith("tests/test_phase3_") and relative.endswith(".py"))
        ):
            raise ValueError(f"Phase 3 source commit A has a forbidden diff: {line}")
    protocol_diff = git("diff", "--name-status", source, repository_commit)
    expected_protocol_diff = (
        "A\texperiments/phase3/phase3_protocol_frozen_v4.json\n"
        "A\texperiments/phase3/phase3_protocol_frozen_v4.sha256"
    )
    if protocol_diff != expected_protocol_diff:
        raise ValueError("Phase 3 protocol commit B diff is not the exact two-file whitelist")
    if git("status", "--porcelain", "--untracked-files=no"):
        raise ValueError("Phase 3 execution requires a clean tracked worktree and index")
    return {
        "phase3_source_commit": source,
        "protocol_repository_commit": repository_commit,
        "protocol_tag": PROTOCOL_TAG,
        "protocol_tag_object": tag_object,
    }


def build_candidate_protocol(
    *,
    code_manifest_path: str | Path,
    authority_manifest_path: str | Path,
    expected_registry_path: str | Path,
    data_manifest_path: str | Path | None,
    split_manifest_path: str | Path | None,
    overlap_audit_input_sha256: str | None = None,
) -> dict[str, Any]:
    prepared: dict[str, Any] | None = None
    if data_manifest_path is not None or split_manifest_path is not None:
        if data_manifest_path is None or split_manifest_path is None:
            raise ValueError("data and split manifests must be supplied together")
        data_path = Path(data_manifest_path)
        split_path = Path(split_manifest_path)
        if data_path.name != "data_manifest.json" or split_path.name != "split_manifest.json" or data_path.parent.resolve() != split_path.parent.resolve():
            raise ValueError("data/split manifests must be the canonical pair in one prepared-data directory")
        from experiments.phase3.artifact_validation import validate_prepared_data

        prepared = validate_prepared_data(data_path.parent)
        if prepared["data_manifest"].get("global_image_status") != "ready":
            raise ValueError("a freeze-ready candidate requires all 1542 images ready")
        diagnostics = load_json_snapshot(data_path.parent / "data_diagnostics.json")
        if diagnostics.get("overlength_count") != 0 or diagnostics.get("input_invariant_failure_count") != 0:
            raise ValueError("a freeze-ready candidate requires a clean tokenization preflight")
    paths = {
        "phase3_code_manifest_sha256": Path(code_manifest_path),
        "stage2_authority_manifest_sha256": Path(authority_manifest_path),
        "expected_model_registry_sha256": Path(expected_registry_path),
        "data_manifest_sha256": Path(data_manifest_path) if data_manifest_path is not None else None,
        "split_manifest_sha256": Path(split_manifest_path) if split_manifest_path is not None else None,
    }
    registry = load_json_snapshot(expected_registry_path) if Path(expected_registry_path).is_file() else {"models": []}
    data = prepared["data_manifest"] if prepared is not None else None
    split = prepared["split_manifest"] if prepared is not None else None
    parsed_payloads = {
        "expected_model_registry_sha256": canonical_json_bytes(registry),
        "data_manifest_sha256": canonical_json_bytes(data) if data is not None else None,
        "split_manifest_sha256": canonical_json_bytes(split) if split is not None else None,
    }
    hashes: dict[str, str | None] = {}
    missing = []
    for field, path in paths.items():
        if path is None or not path.is_file():
            hashes[field] = None
            missing.append(field)
        else:
            payload = parsed_payloads.get(field)
            hashes[field] = sha256_bytes(payload if payload is not None else snapshot_file(path))
    if (
        registry.get("schema_version") != 2
        or registry.get("artifact_batch_id") != ARTIFACT_BATCH_ID
        or registry.get("registry_id") != "phase3-v4-expected-model-registry-v2"
    ):
        raise ValueError("Phase 3 v4 requires the approved rerun expected-model registry")
    if data is not None and (
        data.get("protocol_version") != PROTOCOL_VERSION
        or data.get("split_version") != SPLIT_VERSION
    ):
        raise ValueError("data manifest protocol or split version mismatch")
    if split is not None and (
        split.get("protocol_version") != PROTOCOL_VERSION
        or split.get("split_version") != SPLIT_VERSION
    ):
        raise ValueError("split manifest protocol or split version mismatch")
    if data is None:
        missing.append("complete_data_manifest")
    if split is None:
        missing.append("complete_split_manifest")
    if overlap_audit_input_sha256 is None:
        missing.extend(("complete_overlap_input_definition", "overlap_audit_input_sha256"))
    elif not re.fullmatch(r"[0-9a-f]{64}", overlap_audit_input_sha256):
        raise ValueError("overlap_audit_input_sha256 must be lowercase 64-hex")
    missing = sorted(set(missing), key=lambda value: value.encode("utf-8"))
    source_files = data.get("source_files") if data is not None else None
    return {
        "schema_version": 1,
        "prompt_revision": PROMPT_REVISION,
        "protocol_version": PROTOCOL_VERSION,
        "split_version": SPLIT_VERSION,
        "protocol_kind": "candidate",
        "candidate_status": "incomplete" if missing else "ready_for_user_freeze",
        "missing_required_fields": missing,
        "phase3_source_commit": None,
        "stage2_reference_commit": STAGE2_REFERENCE_COMMIT,
        "stage2_artifact_batch_id": ARTIFACT_BATCH_ID,
        "stage2_protocol_sha256": "4a15ae6697081098973998f7340702368403fa81f39d6c8ed43172b74a55b5b3",
        **hashes,
        "overlap_audit_input_sha256": overlap_audit_input_sha256,
        "dataset": {
            "repo": "Aman-J/SugarCrepe_pp",
            "revision": "dea2a1b6f9e1069c609f676aa55ec61e9b65fb61",
            "split": "train",
            "source_files": source_files,
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
            "split_manifest_summary": (
                {
                    "total_rows": split.get("total_rows"),
                    "total_unique_images": split.get("total_unique_images"),
                    "canonical_row_commitment_sha256": split.get("canonical_row_commitment_sha256"),
                }
                if split is not None else None
            ),
        },
        "models": {
            "ordered_model_ids": [row["model_id"] for row in registry.get("models", [])],
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
        "main_risks": {
            "positive_brier_risk": {"support": [0.0, 2.0]},
            "visual_semantic_loss": {"support": [0.0, 1.0]},
            "positive_invariance_loss": {"support": [0.0, 1.0]},
        },
        "m0": {
            "image_fields": None,
            "positive_source": "lm_only_observed",
            "visual_increment": 0.0,
            "visual_semantic_loss": 0.5,
            "visual_metric_source": "definition_constant_lm_only",
            "visual_bound_method": "definition_constant",
        },
        "aggregation": "canonical row -> within(model,filename) float64 mean -> equal-weight unique-image mean",
        "estimand": {
            "sampling_assumption": "iid_superpopulation",
            "target_distribution": CONDITIONAL_TARGET_DISTRIBUTION,
            "not_finite_population_guarantee": True,
            "not_all_natural_images": True,
            "complete_model_formal_independence_requires_user_acceptance": True,
        },
        "bounds": {
            "main": {"delta_total": 0.05, "comparison_slots": 30, "delta_each": 0.05 / 30, "method": "hoeffding_iid_superpopulation"},
            "compression": {"delta_total": 0.05, "comparison_slots": 30, "delta_each": 0.05 / 30, "separate_from_main": True},
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
            "global_seed": 3407,
            "item_batch_size_unique_image_groups": 1,
            "model_eval": True,
            "inference_mode": True,
            "autocast_enabled": False,
            "model_dtype": "float32",
            "cudnn_deterministic": True,
            "cudnn_benchmark": False,
            "cuda_matmul_allow_tf32": False,
            "cudnn_allow_tf32": False,
            "formal_shard_size_unique_images": 32,
            "formal_nonblocking_exclusive_lock": ".phase3.lock",
            "protocol_tag": PROTOCOL_TAG,
            "approval_statement": "Primary metrics and formal split are frozen.",
        },
        "training_allowed": False,
    }


def build_frozen_protocol(candidate: dict[str, Any], phase3_source_commit: str) -> dict[str, Any]:
    """Materialize the non-self-referential frozen protocol for commit B."""
    if not re.fullmatch(r"[0-9a-f]{40}", phase3_source_commit):
        raise ValueError("phase3_source_commit must be a lowercase 40-hex commit ID")
    if (
        candidate.get("protocol_kind") != "candidate"
        or candidate.get("candidate_status") != "ready_for_user_freeze"
        or candidate.get("missing_required_fields") != []
        or candidate.get("phase3_source_commit") is not None
    ):
        raise ValueError("only a complete ready candidate can be frozen")
    frozen = dict(candidate)
    frozen.pop("candidate_status", None)
    frozen.pop("missing_required_fields", None)
    frozen.update(
        {
            "protocol_kind": "frozen",
            "freeze_status": "frozen",
            "phase3_source_commit": phase3_source_commit,
            "protocol_tag": PROTOCOL_TAG,
        }
    )
    return frozen
