#!/usr/bin/env python3
"""Load, validate, and hash the Stage 2 protocol and immutable inputs."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DRAFT = REPO_ROOT / "experiments/stage2_protocol.draft.json"
DEFAULT_FROZEN = REPO_ROOT / "experiments/stage2_protocol.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def write_json_atomic(path: Path, payload: Any) -> None:
    """Write a generated receipt atomically.

    Source files are edited with patches; experiment outputs use this helper so
    interrupted jobs never leave a valid-looking partial JSON document.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def path_is_within_declared_roots(path: str, roots: list[str]) -> bool:
    candidate = PurePosixPath(path)
    if candidate.is_absolute() or ".." in candidate.parts:
        return False
    normalized = candidate.as_posix()
    return any(
        normalized == PurePosixPath(root).as_posix().rstrip("/")
        or normalized.startswith(PurePosixPath(root).as_posix().rstrip("/") + "/")
        for root in roots
    )


def validate_v2_payload(payload: dict[str, Any]) -> None:
    data = payload["data"]
    draws = data["independent_draws"]
    if (
        draws["sampling"] != "with replacement"
        or draws["train_draws"] != data["train_draws"]
        or draws["validation_draws"] != data["validation_draws"]
        or draws["repeated_catalog_units_allowed"] is not True
        or draws["cross_split_catalog_unit_overlap_allowed"] is not True
        or draws["rejection_or_resampling_for_duplicates_forbidden"] is not True
        or draws["draw_changes_future_eligibility"] is not False
    ):
        raise ValueError("Stage 2 v2 independent-draw contract is inconsistent")
    if (
        data["phash"]["selected_draws_never_enter_forbidden_set"] is not True
        or data["phash"]["within_catalog_or_draw_exclusion"] is not False
        or data["target_distribution"]["real_world_distribution_claim"] is not False
        or data["catalog"]["minimum_eligible_units"]
        < data["train_draws"] + data["validation_draws"]
    ):
        raise ValueError("Stage 2 v2 catalog/distribution contract is inconsistent")
    training = payload["training"]
    micro_batches = data["train_draws"] // training["micro_batch_size"]
    expected_steps = (
        training["epochs"] * micro_batches // training["gradient_accumulation_steps"]
    )
    if (
        data["train_draws"] % training["micro_batch_size"]
        or micro_batches % training["gradient_accumulation_steps"]
        or training["learning_rate_schedule"]["total_steps"] != expected_steps
    ):
        raise ValueError("Stage 2 v2 draw count and optimizer schedule are inconsistent")
    groups = payload["model"]["groups"]
    if any(sum(group["coordinate_dimensions"]) != 4096 for group in groups.values()):
        raise ValueError("Stage 2 v2 model group does not use exactly 4096 coordinates")
    behavior = payload["development"]["v2_reuse"]
    if (
        behavior["allowed"] is not True
        or behavior["behavior_preservation_audit"][
            "model_training_codec_risk_bound_behavior_changed"
        ]
        is not False
        or behavior["selected_learning_rates"]
        != payload["development"]["selected_learning_rates"]
    ):
        raise ValueError("Stage 2 v2 learning-rate reuse gate is inconsistent")
    if (
        payload["history_exclusion"]["stage2_v1_confirmation_images"] != 12000
        or payload["evaluation"]["formal_model_count"] != 10
        or payload["diagnostics"]["pairing_failure"].startswith("stop") is not True
    ):
        raise ValueError("Stage 2 v2 frozen counts or failure policy are inconsistent")
    reused = data.get("reused_confirmation")
    if reused is not None:
        source = reused.get("source_protocol", {})
        if (
            set(source) != {"protocol_id", "protocol_sha256"}
            or source.get("protocol_id") != payload["protocol_id"]
            or not isinstance(source.get("protocol_sha256"), str)
            or len(source["protocol_sha256"]) != 64
            or reused.get("exact_frozen_draws_reused") is not True
            or reused.get("regeneration_forbidden") is not True
        ):
            raise ValueError("Stage 2 v2 reused-confirmation provenance is inconsistent")
    hardware = payload.get("hardware_execution")
    if hardware is not None:
        eligible = hardware.get("eligible_gpu_uuids")
        if (
            hardware.get("policy") != "dynamic_idle_a40_pool"
            or not isinstance(eligible, list)
            or not eligible
            or len(eligible) != len(set(eligible))
            or not all(isinstance(uuid, str) and uuid.startswith("GPU-") for uuid in eligible)
            or hardware.get("per_model_single_physical_gpu") is not True
            or hardware.get("cross_model_parallelism_allowed") is not True
            or hardware.get("rerun_all_formal_models_from_scratch") is not True
            or not isinstance(hardware.get("max_parallel_workers"), int)
            or not 1 <= hardware["max_parallel_workers"] <= len(eligible)
        ):
            raise ValueError("Stage 2 v2 dynamic GPU execution policy is inconsistent")


@dataclass(frozen=True)
class Stage2Protocol:
    path: Path
    sha256: str
    payload: dict[str, Any]

    @classmethod
    def load(
        cls, path: Path | None = None, *, require_frozen: bool = False
    ) -> "Stage2Protocol":
        selected = Path(path or (DEFAULT_FROZEN if require_frozen else DEFAULT_DRAFT))
        selected = selected.resolve()
        payload = json.loads(selected.read_text(encoding="utf-8"))
        schema_version = payload.get("schema_version")
        protocol_ids = {
            1: "minimind-v-stage2-joint-compression-v1",
            2: "minimind-v-stage2-joint-compression-v2",
        }
        if schema_version not in protocol_ids:
            raise ValueError("Stage 2 protocol schema_version must be 1 or 2")
        allowed = {"frozen"} if require_frozen else {"draft", "frozen"}
        if payload.get("status") not in allowed:
            raise ValueError(f"Stage 2 protocol status must be one of {sorted(allowed)}")
        if payload.get("protocol_id") != protocol_ids[schema_version]:
            raise ValueError("unexpected Stage 2 protocol ID")
        if schema_version == 2:
            validate_v2_payload(payload)
        return cls(selected, sha256_file(selected), payload)

    @property
    def is_frozen(self) -> bool:
        return self.payload["status"] == "frozen"

    def reference(self) -> dict[str, str]:
        return {
            "protocol_id": self.payload["protocol_id"],
            "protocol_sha256": self.sha256,
        }

    def confirmation_reference(self) -> dict[str, str]:
        """Return the protocol that originally materialized the frozen draws."""
        reused = self.payload.get("data", {}).get("reused_confirmation")
        if reused is None:
            return self.reference()
        source = reused.get("source_protocol")
        if (
            not isinstance(source, dict)
            or set(source) != {"protocol_id", "protocol_sha256"}
            or source.get("protocol_id") != self.payload["protocol_id"]
            or not isinstance(source.get("protocol_sha256"), str)
            or len(source["protocol_sha256"]) != 64
        ):
            raise ValueError("reused confirmation source protocol is malformed")
        return dict(source)

    def require_frozen(self) -> None:
        if not self.is_frozen:
            raise ValueError("formal confirmation requires a frozen Stage 2 protocol")

    def confirmation_directory(self) -> Path:
        directory = Path(self.payload["data"]["output_directory"])
        return directory if directory.is_absolute() else REPO_ROOT / directory

    def verify_confirmation_data(self, path: Path, role: str) -> dict[str, Any]:
        """Verify post-tag confirmation data through its protocol-bound receipts."""
        self.require_frozen()
        if role not in ("train", "validation"):
            raise ValueError(f"unknown confirmation data role: {role}")
        if self.payload.get("schema_version", 1) == 2:
            return self._verify_v2_confirmation_data(path, role)
        data = self.payload["data"]
        directory = self.confirmation_directory().resolve()
        selected = Path(path).resolve()
        expected_path = directory / f"{role}.parquet"
        if selected != expected_path:
            raise ValueError(
                f"formal {role} data must use the frozen output path: {expected_path}"
            )
        receipts = data["post_tag_receipts"]
        manifest_path = directory / receipts["split_manifest"]
        verification_path = directory / receipts["independent_verification"]
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        verification = json.loads(verification_path.read_text(encoding="utf-8"))
        reference = self.reference()
        if manifest.get("schema_version") != 1 or manifest.get("protocol") != reference:
            raise ValueError("confirmation split manifest does not bind the frozen protocol")
        if (
            verification.get("schema_version") != 1
            or verification.get("status") != "passed"
            or verification.get("protocol") != reference
        ):
            raise ValueError("confirmation verification receipt is not a frozen-protocol pass")
        selection = manifest.get("selection", {})
        if (
            manifest.get("source", {}).get("sha256") != data["source_sha256"]
            or selection.get("seed") != data["selection_seed"]
            or selection.get("validation_first") != data["validation_images"]
            or selection.get("training_second") != data["train_images"]
        ):
            raise ValueError("confirmation manifest selection rules differ from protocol")
        required_manifest_invariants = {
            "exact_unique_and_disjoint",
            "target_eos_present",
            "vlm_length_at_most_450",
            "selected_phash_unique",
        }
        manifest_invariants = manifest.get("invariants", {})
        if not required_manifest_invariants.issubset(manifest_invariants) or not all(
            manifest_invariants[name] for name in required_manifest_invariants
        ):
            raise ValueError("confirmation split manifest has a failed invariant")
        if verification.get("verified_images") != data["train_images"] + data["validation_images"]:
            raise ValueError("confirmation verification image count differs from protocol")
        verification_invariants = verification.get("invariants", {})
        if not verification_invariants or not all(verification_invariants.values()):
            raise ValueError("confirmation independent verification has a failed invariant")
        if verification.get("split_manifest_sha256") != sha256_file(manifest_path):
            raise ValueError("confirmation split manifest hash differs from verification receipt")
        output = manifest.get("outputs", {}).get(role, {})
        expected_rows = data[f"{role}_images"]
        actual_sha256 = sha256_file(selected)
        if output.get("rows") != expected_rows:
            raise ValueError(f"formal {role} row count differs from frozen protocol")
        if output.get("sha256") != actual_sha256:
            raise ValueError(f"formal {role} hash differs from split manifest")
        if verification.get(f"{role}_sha256") != actual_sha256:
            raise ValueError(f"formal {role} hash differs from independent verification")
        return {
            "data_path": str(selected),
            "data_sha256": actual_sha256,
            "split_manifest_path": str(manifest_path),
            "split_manifest_sha256": sha256_file(manifest_path),
            "independent_verification_path": str(verification_path),
            "independent_verification_sha256": sha256_file(verification_path),
        }

    def _verify_v2_confirmation_data(self, path: Path, role: str) -> dict[str, Any]:
        """Verify a v2 catalog draw through both independent replay receipts."""
        data = self.payload["data"]
        directory = self.confirmation_directory().resolve()
        selected = Path(path).resolve()
        expected_path = directory / f"{role}.parquet"
        if selected != expected_path:
            raise ValueError(
                f"formal {role} data must use the frozen output path: {expected_path}"
            )
        receipts = data["post_tag_receipts"]
        paths = {
            "catalog": directory / receipts["catalog"],
            "catalog_manifest": directory / receipts["catalog_manifest"],
            "split_manifest": directory / receipts["split_manifest"],
            "independent_verification": directory / receipts["independent_verification"],
            "replay_verification": directory / receipts["replay_verification"],
        }
        catalog_manifest = json.loads(
            paths["catalog_manifest"].read_text(encoding="utf-8")
        )
        split_manifest = json.loads(
            paths["split_manifest"].read_text(encoding="utf-8")
        )
        verification = json.loads(
            paths["independent_verification"].read_text(encoding="utf-8")
        )
        replay = json.loads(
            paths["replay_verification"].read_text(encoding="utf-8")
        )
        reference = self.confirmation_reference()
        for name, receipt in (
            ("catalog manifest", catalog_manifest),
            ("split manifest", split_manifest),
            ("independent verification", verification),
            ("replay verification", replay),
        ):
            if receipt.get("schema_version") != 2 or receipt.get("protocol") != reference:
                raise ValueError(f"{name} does not bind the frozen v2 protocol")
        if verification.get("status") != "passed" or replay.get("status") != "passed":
            raise ValueError("v2 confirmation verification receipts are not passes")

        catalog_rule = data["catalog"]
        row_selection = catalog_manifest.get("row_selection", {})
        if (
            catalog_manifest.get("source", {}).get("sha256") != data["source_sha256"]
            or catalog_manifest.get("source", {}).get("rows") != data["source_rows"]
            or row_selection.get("seed") != data["selection_seed"]
            or row_selection.get("domain") != catalog_rule["row_rank_domain"]
            or row_selection.get("capacity") != catalog_rule["source_row_capacity"]
            or row_selection.get("independent_of_row_contents") is not True
        ):
            raise ValueError("v2 catalog construction differs from the frozen protocol")
        catalog_invariants = catalog_manifest.get("invariants", {})
        if not catalog_invariants or not all(catalog_invariants.values()):
            raise ValueError("v2 catalog manifest has a failed invariant")

        draws = data["independent_draws"]
        sampling = split_manifest.get("sampling", {})
        if (
            sampling.get("seed") != data["selection_seed"]
            or sampling.get("method") != "independent_with_replacement"
            or sampling.get("validation_domain") != draws["validation_domain"]
            or sampling.get("train_domain") != draws["train_domain"]
            or sampling.get("unbiased_rejection_mapping") is not True
            or sampling.get("duplicates_allowed_without_redraw") is not True
            or sampling.get("cross_split_overlap_allowed_without_redraw") is not True
        ):
            raise ValueError("v2 draw rules differ from the frozen protocol")
        split_invariants = split_manifest.get("invariants", {})
        if not split_invariants or not all(split_invariants.values()):
            raise ValueError("v2 split manifest has a failed invariant")
        for receipt_name, receipt in (
            ("independent verification", verification),
            ("replay verification", replay),
        ):
            receipt_invariants = receipt.get("invariants")
            if receipt_name == "independent verification" and (
                not receipt_invariants or not all(receipt_invariants.values())
            ):
                raise ValueError("v2 independent verification has a failed invariant")

        catalog_sha256 = sha256_file(paths["catalog"])
        catalog_manifest_sha256 = sha256_file(paths["catalog_manifest"])
        split_manifest_sha256 = sha256_file(paths["split_manifest"])
        catalog_rows = catalog_manifest.get("outputs", {}).get("catalog_rows")
        if catalog_rows is None or catalog_rows < catalog_rule["minimum_eligible_units"]:
            raise ValueError("v2 eligible catalog is below the frozen minimum")
        if (
            catalog_manifest.get("outputs", {}).get("catalog_sha256") != catalog_sha256
            or split_manifest.get("catalog", {}).get("sha256") != catalog_sha256
            or verification.get("catalog_sha256") != catalog_sha256
            or replay.get("catalog_sha256") != catalog_sha256
        ):
            raise ValueError("v2 eligible catalog hash is not consistently bound")
        if (
            split_manifest.get("catalog", {}).get("manifest_sha256")
            != catalog_manifest_sha256
            or verification.get("catalog_manifest_sha256")
            != catalog_manifest_sha256
            or replay.get("catalog_manifest_sha256") != catalog_manifest_sha256
        ):
            raise ValueError("v2 catalog manifest hash is not consistently bound")
        if (
            verification.get("split_manifest_sha256") != split_manifest_sha256
            or replay.get("split_manifest_sha256") != split_manifest_sha256
        ):
            raise ValueError("v2 split manifest hash is not consistently bound")
        expected_total = draws["train_draws"] + draws["validation_draws"]
        if (
            verification.get("verified_catalog_units") != catalog_rows
            or verification.get("verified_draws") != expected_total
            or replay.get("catalog_units") != catalog_rows
            or replay.get("train_draws") != draws["train_draws"]
            or replay.get("validation_draws") != draws["validation_draws"]
        ):
            raise ValueError("v2 replay receipt counts differ from the frozen protocol")

        output = split_manifest.get("outputs", {}).get(role, {})
        expected_rows = draws[f"{role}_draws"]
        actual_sha256 = sha256_file(selected)
        if output.get("rows") != expected_rows or output.get("sha256") != actual_sha256:
            raise ValueError(f"formal {role} data differs from the split manifest")
        if verification.get(f"{role}_sha256") != actual_sha256:
            raise ValueError(f"formal {role} data differs from independent verification")
        return {
            "data_path": str(selected),
            "data_sha256": actual_sha256,
            "confirmation_protocol": reference,
            "execution_protocol": self.reference(),
            "catalog_path": str(paths["catalog"]),
            "catalog_sha256": catalog_sha256,
            "catalog_manifest_path": str(paths["catalog_manifest"]),
            "catalog_manifest_sha256": catalog_manifest_sha256,
            "split_manifest_path": str(paths["split_manifest"]),
            "split_manifest_sha256": split_manifest_sha256,
            "independent_verification_path": str(paths["independent_verification"]),
            "independent_verification_sha256": sha256_file(
                paths["independent_verification"]
            ),
            "replay_verification_path": str(paths["replay_verification"]),
            "replay_verification_sha256": sha256_file(paths["replay_verification"]),
        }

    def verify_file(self, path: Path, expected_sha256: str, role: str) -> None:
        actual = sha256_file(path)
        if actual != expected_sha256:
            raise ValueError(
                f"{role} SHA-256 mismatch: expected {expected_sha256}, got {actual}"
            )

    def verify_immutable_inputs(self) -> None:
        assets = self.payload["assets"]
        self.verify_file(
            REPO_ROOT / assets["manifest_path"], assets["manifest_sha256"], "asset manifest"
        )
        self.verify_file(
            REPO_ROOT / assets["sha256_list_path"],
            assets["sha256_list_sha256"],
            "asset hash list",
        )
        history = self.payload["history_exclusion"]
        for stem in ("receipt", "exact_sha256", "phash", "sources", "manifest"):
            self.verify_file(
                REPO_ROOT / history[f"{stem}_path"],
                history[f"{stem}_sha256"],
                f"history {stem}",
            )
        if self.payload.get("schema_version") == 2:
            behavior = self.payload["development"]["v2_reuse"][
                "behavior_preservation_audit"
            ]
            self.verify_file(
                REPO_ROOT / behavior["path"], behavior["sha256"], "v2 behavior audit"
            )
            environment = self.payload["environment"]
            if environment.get("status") != "frozen":
                raise ValueError("Stage 2 v2 environment is not frozen")
            self.verify_file(
                REPO_ROOT / environment["receipt_path"],
                environment["receipt_sha256"],
                "v2 environment receipt",
            )
            self.verify_file(
                REPO_ROOT / environment["pip_freeze_path"],
                environment["pip_freeze_sha256"],
                "v2 pip freeze",
            )
            receipt = json.loads(
                (REPO_ROOT / environment["receipt_path"]).read_text(encoding="utf-8")
            )
            if (
                receipt.get("schema_version") != 2
                or receipt.get("selected_gpu", {}).get("uuid")
                != environment["selected_gpu_uuid"]
                or receipt.get("selected_gpu", {}).get("name")
                != environment["selected_gpu_name"]
                or receipt.get("pip_freeze", {}).get("sha256")
                != environment["pip_freeze_sha256"]
            ):
                raise ValueError("v2 environment receipt differs from frozen protocol")

    def execution_gpu_uuid(self) -> tuple[str, str]:
        """Resolve the one physical GPU assigned to the current process."""
        environment = self.payload["environment"]
        hardware = self.payload.get("hardware_execution")
        if hardware is None:
            return "single_frozen_gpu", environment["selected_gpu_uuid"]
        visible = os.environ.get("CUDA_VISIBLE_DEVICES", "").strip()
        if not visible or "," in visible or not visible.startswith("GPU-"):
            raise ValueError(
                "dynamic formal execution requires exactly one GPU UUID in CUDA_VISIBLE_DEVICES"
            )
        if visible not in hardware["eligible_gpu_uuids"]:
            raise ValueError("execution GPU is outside the frozen dynamic A40 pool")
        return hardware["policy"], visible

    def verify_runtime_integrity(self) -> dict[str, Any]:
        """Bind v2 formal execution to the annotated tag and frozen blobs."""
        self.require_frozen()
        if self.payload.get("schema_version") != 2:
            raise ValueError("runtime-integrity audit is defined for Stage 2 v2 only")

        def git_text(*arguments: str) -> str:
            result = subprocess.run(
                ["git", *arguments],
                cwd=REPO_ROOT,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            return result.stdout.strip()

        git = self.payload["git"]
        tag = git["annotated_tag"]
        if git_text("cat-file", "-t", f"refs/tags/{tag}") != "tag":
            raise ValueError(f"formal protocol tag is not annotated: {tag}")
        tag_commit = git_text("rev-list", "-n", "1", tag)
        head_commit = git_text("rev-parse", "HEAD")
        if head_commit != tag_commit:
            raise ValueError("formal execution HEAD must equal the protocol tag target")
        implementation_commit = git.get("frozen_implementation_commit")
        if not isinstance(implementation_commit, str) or len(implementation_commit) != 40:
            raise ValueError("frozen implementation commit is not materialized")
        ancestor = subprocess.run(
            ["git", "merge-base", "--is-ancestor", implementation_commit, tag_commit],
            cwd=REPO_ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if ancestor.returncode != 0:
            raise ValueError("frozen implementation commit is not an ancestor of protocol tag")

        relative_protocol = self.path.relative_to(REPO_ROOT).as_posix()
        tagged_protocol = subprocess.run(
            ["git", "show", f"{tag_commit}:{relative_protocol}"],
            cwd=REPO_ROOT,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).stdout
        if hashlib.sha256(tagged_protocol).hexdigest() != self.sha256:
            raise ValueError("protocol file differs from the annotated tag target")

        implementation_hashes = self.payload["implementation"].get(
            "implementation_file_sha256", {}
        )
        if not implementation_hashes:
            raise ValueError("frozen implementation file hashes are empty")
        verified_files = []
        for relative, expected in sorted(implementation_hashes.items()):
            current_path = REPO_ROOT / relative
            if sha256_file(current_path) != expected:
                raise ValueError(f"current implementation hash differs: {relative}")
            committed = subprocess.run(
                ["git", "show", f"{implementation_commit}:{relative}"],
                cwd=REPO_ROOT,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            ).stdout
            if hashlib.sha256(committed).hexdigest() != expected:
                raise ValueError(f"frozen implementation blob hash differs: {relative}")
            verified_files.append(relative)

        tracked_status = git_text("status", "--porcelain", "--untracked-files=no")
        if tracked_status:
            raise ValueError("formal execution requires a clean tracked worktree and index")
        untracked = [
            line
            for line in git_text("ls-files", "--others", "--exclude-standard").splitlines()
            if line
        ]
        allowed_roots = self.payload["implementation"].get(
            "allowed_untracked_output_roots", []
        )
        disallowed = [
            path for path in untracked if not path_is_within_declared_roots(path, allowed_roots)
        ]
        if disallowed:
            raise ValueError(f"formal execution has undeclared untracked paths: {disallowed}")
        environment = self.payload["environment"]
        if Path(sys.executable).resolve() != Path(environment["python_executable"]).resolve():
            raise ValueError("formal execution uses a different Python executable")
        pip_lines = subprocess.run(
            [sys.executable, "-m", "pip", "freeze", "--all"],
            cwd=REPO_ROOT,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        ).stdout.splitlines()
        normalized_pip = (
            "\n".join(sorted((line.strip() for line in pip_lines if line.strip()), key=str.lower))
            + "\n"
        ).encode("utf-8")
        if hashlib.sha256(normalized_pip).hexdigest() != environment["pip_freeze_sha256"]:
            raise ValueError("live Python environment differs from frozen pip receipt")
        gpu_rows = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=name,uuid",
                "--format=csv,noheader,nounits",
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        ).stdout.splitlines()
        inventory = [tuple(value.strip() for value in row.split(",", 1)) for row in gpu_rows]
        execution_policy, execution_gpu_uuid = self.execution_gpu_uuid()
        selected_gpu = [
            (name, uuid)
            for name, uuid in inventory
            if uuid == execution_gpu_uuid
        ]
        if len(selected_gpu) != 1 or "A40" not in selected_gpu[0][0]:
            raise ValueError("selected execution A40 is absent from the live GPU inventory")
        process_result = subprocess.run(
            [
                "nvidia-smi",
                "--query-compute-apps=gpu_uuid",
                "--format=csv,noheader,nounits",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        active_gpu_uuids = {
            line.strip()
            for line in process_result.stdout.splitlines()
            if line.strip()
        }
        if execution_gpu_uuid in active_gpu_uuids:
            raise ValueError("selected execution A40 has an active compute process")
        return {
            "status": "passed",
            "protocol": self.reference(),
            "annotated_tag": tag,
            "tag_commit": tag_commit,
            "head_commit": head_commit,
            "frozen_implementation_commit": implementation_commit,
            "verified_implementation_files": verified_files,
            "verified_implementation_file_count": len(verified_files),
            "allowed_untracked_output_roots": allowed_roots,
            "observed_untracked_paths": untracked,
            "python_executable": str(Path(sys.executable).resolve()),
            "live_pip_freeze_sha256": hashlib.sha256(normalized_pip).hexdigest(),
            "execution_gpu_policy": execution_policy,
            "execution_gpu_uuid": execution_gpu_uuid,
            "execution_gpu_name": selected_gpu[0][0],
            "execution_gpu_idle": True,
            "selected_gpu_uuid": execution_gpu_uuid,
            "selected_gpu_name": selected_gpu[0][0],
            "selected_gpu_idle": True,
        }

    def asset_path(self, role: str) -> Path:
        assets = self.payload["assets"]
        relative = assets["required_roles"][role]
        path = Path(assets["root"]) / relative
        manifest = json.loads(
            (REPO_ROOT / assets["manifest_path"]).read_text(encoding="utf-8")
        )
        entries = manifest.get("files", manifest.get("assets", []))
        matches = [
            item for item in entries
            if item.get("path") == relative or item.get("relative_path") == relative
        ]
        if len(matches) == 1:
            expected = matches[0].get("sha256")
            self.verify_file(path, expected, f"asset {role}")
        elif not matches and path.is_dir():
            prefix = relative.rstrip("/") + "/"
            children = [
                item for item in entries
                if (item.get("path") or item.get("relative_path", "")).startswith(prefix)
            ]
            if not children:
                raise ValueError(f"asset manifest does not contain directory {relative}")
            for item in children:
                child_relative = item.get("path") or item["relative_path"]
                self.verify_file(
                    Path(assets["root"]) / child_relative,
                    item["sha256"],
                    f"asset {role}/{Path(child_relative).name}",
                )
        else:
            raise ValueError(f"asset manifest does not uniquely contain {relative}")
        return path


def load_target_registry(path: Path | None = None) -> dict[str, Any]:
    selected = Path(path or REPO_ROOT / "experiments/stage2_target_registry.json")
    payload = json.loads(selected.read_text(encoding="utf-8"))
    if payload.get("schema_version") != 1:
        raise ValueError("Stage 2 target registry schema_version must be 1")
    names: list[str] = []
    for module in ("vision", "projector", "language"):
        entries = payload["modules"][module]["targets"]
        module_names = [entry["canonical_name"] for entry in entries]
        if module_names != sorted(module_names, key=lambda value: value.encode("utf-8")):
            raise ValueError(f"{module} targets are not in canonical UTF-8 order")
        names.extend(module_names)
        rank = payload["modules"][module]["rank"]
        count = sum(
            rank * (entry["in_features"] + entry["out_features"])
            for entry in entries
        )
        if count != payload["modules"][module]["factor_elements"]:
            raise ValueError(f"{module} factor-element count is inconsistent")
    if len(names) != len(set(names)):
        raise ValueError("Stage 2 target names must be unique")
    return payload
