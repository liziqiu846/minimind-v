"""Verified, in-memory loading of the ten frozen Stage 2 MMS2 adapters."""

from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path
from typing import Any

from experiments.phase3.canonical_io import sha256_bytes, snapshot_file


DECODER_ID = "stage2-v2-mms2"
ARTIFACT_BATCH_ID = "stage2-v2-rerun-20260721"
RERUN_SOURCE_COMMIT = "07eff239d965f644e3207925ddac446a803ee45e"
STAGE2_REFERENCE_COMMIT = "9c575c617dd399dda73996e4e7e6e1f5614ee0d1"
STAGE2_PROTOCOL_SHA256 = "4a15ae6697081098973998f7340702368403fa81f39d6c8ed43172b74a55b5b3"
REPO_ROOT = Path(__file__).resolve().parents[2]
STAGE2_FROZEN_PATHS = (
    "experiments/stage2_protocol_v2.json",
    "experiments/stage2_protocol.py",
    "experiments/evaluate_stage2_risk.py",
    "experiments/stage2_model.py",
    "experiments/quantize_stage2_adapter.py",
    "experiments/stage2_target_registry.json",
    "dataset/stage2_dataset.py",
    "model/global_subspace_lora.py",
    "model/model_minimind.py",
    "model/model_vlm.py",
    "model/subspace_projector.py",
)
MODELS: tuple[dict[str, Any], ...] = (
    {"model_id":"M0-root-43101","method":"M0","mapping_root":43101,"artifact_relative_path":"experiments/runs/stage2_v2_fast/formal/01_M0_root-43101_seed-2026_lr-0p050/encode/adapter.mms2","artifact_size_bytes":820,"artifact_sha256":"7ac08152d6487b582a6cae16c6d932ef507823b67302a77e7260ccf87dd12220","description_bits":6560},
    {"model_id":"M0-root-43102","method":"M0","mapping_root":43102,"artifact_relative_path":"experiments/runs/stage2_v2_fast/formal/02_M0_root-43102_seed-2026_lr-0p050/encode/adapter.mms2","artifact_size_bytes":828,"artifact_sha256":"a77491ab4729bd2e99e9062b77611f59550931c2ed508725c56523ffb3ce66cf","description_bits":6624},
    {"model_id":"M0-root-43103","method":"M0","mapping_root":43103,"artifact_relative_path":"experiments/runs/stage2_v2_fast/formal/03_M0_root-43103_seed-2026_lr-0p050/encode/adapter.mms2","artifact_size_bytes":973,"artifact_sha256":"c0349a686885bc36d130e83b4a4d696e3b59aeb43e936ccc7631a0483a22ab96","description_bits":7784},
    {"model_id":"M1-root-none","method":"M1","mapping_root":None,"artifact_relative_path":"experiments/runs/stage2_v2_fast/formal/04_M1_root-none_seed-2026_lr-0p015/encode/adapter.mms2","artifact_size_bytes":1311,"artifact_sha256":"e30206f2063217e36f992a4c622f99a15db38f7d071aea67e0c79b8df9dd7674","description_bits":10488},
    {"model_id":"M2-root-43101","method":"M2","mapping_root":43101,"artifact_relative_path":"experiments/runs/stage2_v2_fast/formal/05_M2_root-43101_seed-2026_lr-0p050/encode/adapter.mms2","artifact_size_bytes":1150,"artifact_sha256":"29234c2a2709fee8256779a6cacd8ace75de34a73791f4f07031b6383688e8ad","description_bits":9200},
    {"model_id":"M2-root-43102","method":"M2","mapping_root":43102,"artifact_relative_path":"experiments/runs/stage2_v2_fast/formal/06_M2_root-43102_seed-2026_lr-0p050/encode/adapter.mms2","artifact_size_bytes":1296,"artifact_sha256":"6c99254997772d99155969dd6c6d5867bb8f2b16f619fb330cdfa6747252cd00","description_bits":10368},
    {"model_id":"M2-root-43103","method":"M2","mapping_root":43103,"artifact_relative_path":"experiments/runs/stage2_v2_fast/formal/07_M2_root-43103_seed-2026_lr-0p050/encode/adapter.mms2","artifact_size_bytes":1302,"artifact_sha256":"5f39f9f70341051683fb0f17d58373cbe60f50749767fda74b48b4ddb95db2bf","description_bits":10416},
    {"model_id":"M3-root-43101","method":"M3","mapping_root":43101,"artifact_relative_path":"experiments/runs/stage2_v2_fast/formal/08_M3_root-43101_seed-2026_lr-0p050/encode/adapter.mms2","artifact_size_bytes":804,"artifact_sha256":"732d9af5c6ddb7d21f78bc3a942473a71393a7d3452be3b095b4b166bdd6b405","description_bits":6432},
    {"model_id":"M3-root-43102","method":"M3","mapping_root":43102,"artifact_relative_path":"experiments/runs/stage2_v2_fast/formal/09_M3_root-43102_seed-2026_lr-0p050/encode/adapter.mms2","artifact_size_bytes":978,"artifact_sha256":"78ba0766be1adf79aa11579dee02d394ddcfc990559a97f87d11a50fb86f4977","description_bits":7824},
    {"model_id":"M3-root-43103","method":"M3","mapping_root":43103,"artifact_relative_path":"experiments/runs/stage2_v2_fast/formal/10_M3_root-43103_seed-2026_lr-0p050/encode/adapter.mms2","artifact_size_bytes":798,"artifact_sha256":"8950c943a030ea9571b0fb191a0ac9cb20aeec9ea1e87b6a11cd80c89a1d7b83","description_bits":6384},
)


def expected_model(model_id: str) -> dict[str, Any]:
    matches = [model for model in MODELS if model["model_id"] == model_id]
    if len(matches) != 1:
        raise ValueError(f"unknown or duplicate model_id: {model_id}")
    return dict(matches[0])


def verify_stage2_source_integrity(stage2_protocol_path: str):
    """Verify the complete frozen Stage 2 source and base-asset chain."""
    from experiments.stage2_protocol import Stage2Protocol

    protocol_path = Path(stage2_protocol_path).absolute()
    expected_protocol_path = (REPO_ROOT / "experiments/stage2_protocol_v2.json").absolute()
    if protocol_path != expected_protocol_path:
        raise ValueError("Phase 3 requires the repository Stage 2 v2 protocol path")
    protocol_raw = snapshot_file(protocol_path, root=REPO_ROOT)
    if sha256_bytes(protocol_raw) != STAGE2_PROTOCOL_SHA256:
        raise ValueError("Stage 2 v2 protocol raw SHA-256 mismatch")

    def git(*arguments: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["git", "-C", str(REPO_ROOT), *arguments],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )

    ancestor = git("merge-base", "--is-ancestor", STAGE2_REFERENCE_COMMIT, "HEAD")
    if ancestor.returncode != 0:
        raise ValueError("current repository HEAD is not a descendant of Stage 2 reference commit")
    for relative in STAGE2_FROZEN_PATHS:
        frozen = subprocess.run(
            ["git", "-C", str(REPO_ROOT), "show", f"{STAGE2_REFERENCE_COMMIT}:{relative}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if frozen.returncode != 0:
            raise ValueError(f"frozen Stage 2 source path is absent from reference commit: {relative}")
        current = snapshot_file(REPO_ROOT / relative, root=REPO_ROOT)
        if current != frozen.stdout:
            raise ValueError(f"frozen Stage 2 source path changed: {relative}")

    protocol = Stage2Protocol.load(protocol_path, require_frozen=True)
    implementation = protocol.payload.get("implementation", {}).get("implementation_file_sha256", {})
    if not isinstance(implementation, dict) or not implementation:
        raise ValueError("Stage 2 implementation SHA table is missing")
    for relative, expected_sha in sorted(implementation.items()):
        current = snapshot_file(REPO_ROOT / relative, root=REPO_ROOT)
        if sha256_bytes(current) != expected_sha:
            raise ValueError(f"Stage 2 implementation SHA mismatch: {relative}")
    protocol.verify_immutable_inputs()
    for role in ("tokenizer", "initial_llm", "vision_encoder"):
        protocol.asset_path(role)
    return protocol


def verify_payload(payload: bytes, expected: dict[str, Any]):
    from experiments.quantize_stage2_adapter import decode_mms2

    if len(payload) != expected["artifact_size_bytes"]:
        raise ValueError("size_mismatch")
    if hashlib.sha256(payload).hexdigest() != expected["artifact_sha256"]:
        raise ValueError("hash_mismatch")
    coordinates, metadata = decode_mms2(payload)
    if metadata["model_group"] != expected["method"] or metadata["mapping_root"] != expected["mapping_root"]:
        raise ValueError("decoded_identity_mismatch")
    if metadata["archive_bytes"] != len(payload):
        raise ValueError("decoded_identity_mismatch")
    return coordinates, metadata


def snapshot_and_verify(root: str | Path, expected: dict[str, Any]):
    artifact_root = Path(root).absolute()
    path = artifact_root / expected["artifact_relative_path"]
    payload = snapshot_file(path, root=artifact_root)
    coordinates, metadata = verify_payload(payload, expected)
    return payload, coordinates, metadata


def load_verified_model(
    model_id: str,
    *,
    artifact_root: str | Path,
    stage2_protocol_path: str | Path,
    device="cpu",
    dtype=None,
):
    import torch
    from experiments.stage2_model import build_stage2_model
    from model.global_subspace_lora import load_coordinate_state

    expected = expected_model(model_id)
    protocol = verify_stage2_source_integrity(str(Path(stage2_protocol_path).absolute()))
    _, coordinates, metadata = snapshot_and_verify(artifact_root, expected)
    model = build_stage2_model(
        expected["method"],
        protocol,
        expected["mapping_root"],
        device=device,
        dtype=dtype or torch.float32,
    )
    load_coordinate_state(model, coordinates)
    model.eval()
    return model, metadata, protocol
