from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from . import BUDGETS, CANDIDATE_COUNT, PROTOCOL_ID, SEEDS, STRUCTURES
from .authority import read_m2_authority
from .common import REPO_ROOT, canonical_bytes, load_json, sha256_file
from .configs import generate_matrix, matrix_sha256, validate_matrix
from .certificates import (
    FORMAL_DELTA_SEMANTIC,
    FORMAL_DELTA_TOTAL,
    FORMAL_DELTA_VISUAL,
)

PROTOCOL_PATH = Path(__file__).with_name("protocol.json")


def build_protocol() -> dict[str, Any]:
    base = load_json(REPO_ROOT / "experiments/stage2_protocol_v2.json")
    training = base["training"]
    return {
        "schema_version": 1,
        "status": "frozen",
        "protocol_id": PROTOCOL_ID,
        "scientific_question": "private_module_coordinates_vs_one_shared_coordinate_vector",
        "structures": list(STRUCTURES),
        "budgets": list(BUDGETS),
        "seeds": list(SEEDS),
        "s0": SEEDS[0],
        "candidate_count": CANDIDATE_COUNT,
        "candidate_matrix_sha256": matrix_sha256(),
        "candidate_selection": {
            "unit": "bit",
            "bits": __import__("math").log2(CANDIDATE_COUNT),
            "natural_log_conversion": "bits * ln(2)",
            "seed_integer_bits": 0,
            "checkpoint_reencoding_bits": 0,
        },
        "m2_allocation_authority": read_m2_authority(),
        "shared_semantics": "delta_theta_m = P_m w; one w, module-specific frozen P_m",
        "fairness": {
            "base_checkpoint": {
                "path": base["assets"]["required_roles"]["initial_llm"],
                "sha256": "5b8c49f6c9d965092e651cafeeaeb8705558632b3fd4ac8ab319cbc5a3cbc4a0",
            },
            "training_data": {
                "relative_path": "dataset/stage2_confirm_v2_seed2028/train.parquet",
                "sha256": base["data"]["reused_confirmation"]["train_sha256"],
                "same_order": True,
                "train_seed": training["formal_seed"],
                "epoch_permutation": training["epoch_permutation"],
            },
            "target_registry": {
                "relative_path": "experiments/stage2_target_registry.json",
                "sha256": base["implementation"]["target_registry_sha256"],
            },
            "optimizer": training["optimizer"],
            "epochs": training["epochs"],
            "micro_batch_size": training["micro_batch_size"],
            "gradient_accumulation_steps": training["gradient_accumulation_steps"],
            "total_steps": training["learning_rate_schedule"]["total_steps"],
            "learning_rate_schedule": training["learning_rate_schedule"],
            "learning_rate": base["development"]["selected_learning_rates"]["M2_M3"],
            "quantization": {
                "format": base["compression"]["format"],
                "levels": base["compression"]["levels"],
                "codec": base["compression"]["codec"],
                "complexity_bits": base["compression"]["complexity_bits"],
            },
            "projection_domain": "stage2-map-v1",
        },
        "evaluation": {
            "joint_confidence": {
                "delta_total": FORMAL_DELTA_TOTAL,
                "delta_semantic": FORMAL_DELTA_SEMANTIC,
                "delta_visual": FORMAL_DELTA_VISUAL,
                "allocation_rule": "delta_semantic + delta_visual = delta_total",
                "simultaneous_confidence": 1.0 - FORMAL_DELTA_TOTAL,
            },
            "semantic_risk": "existing_prediction_smoothed_conditional_nll",
            "semantic_smoothing": {
                "alpha": base["evaluation"]["alpha"],
                "vocab_size": base["evaluation"]["vocab_size"],
                "loss_unit": base["evaluation"]["loss_units"],
                "loss_range": (
                    "Delta_alpha=log2(1+(1-alpha)*vocab_size/alpha)"
                ),
                "bound": (
                    "R_hat+Delta_alpha*sqrt(((C_bits*ln(2)+2*ln(C_bits))"
                    "+ln(1/delta_semantic))/(2*m))"
                ),
            },
            "visual_score": "phase3_v6_bounded_visual_semantic_contrast_q",
            "visual_candidate_selection": {
                "candidate_count": CANDIDATE_COUNT,
                "selection_bits": __import__("math").log2(CANDIDATE_COUNT),
                "selection_nats": "selection_bits*ln(2)=ln(18)",
                "bound_radius": (
                    "sqrt(2*(ln(18)+ln(1/delta))/pair_count)"
                ),
            },
            "pairing_seed": 3407,
            "pairing": (
                "shuffle_unique_groups_then_adjacent_disjoint_pairs_and_use_both_directions"
            ),
            "pair_estimand": "0.5*((q(I_i,T_i)-q(I_j,T_i))+(q(I_j,T_j)-q(I_i,T_j)))",
            "odd_sample_policy": "drop_frozen_permutation_last_and_record_audit_hashes",
            "development_image_count": 1343,
            "development_use_only": True,
            "formal_requires_fresh_confirmation_manifest": True,
        },
        "execution_limit": {
            "formal_training_allowed": True,
            "formal_training_entry": (
                "experiments.phase3_private_vs_shared_v1.train_one"
            ),
            "formal_matrix_entry": (
                "experiments.phase3_private_vs_shared_v1.run_matrix"
            ),
            "smoke_max_batches": 2,
        },
        "artifact_compatibility": {
            "required_field": "protocol_sha256",
            "required_value": "raw SHA-256 of this protocol.json",
            "required_matrix_field": "candidate_matrix_sha256",
            "missing_or_mismatched_policy": "reject",
            "cross_protocol_mixing": "forbidden",
        },
        "candidate_matrix_rule": "deterministic_cartesian_product(structure,budget,seed)",
    }


def validate_frozen_protocol() -> str:
    payload = load_json(PROTOCOL_PATH)
    expected = build_protocol()
    if payload != expected:
        raise ValueError("protocol.json differs from its deterministic builder")
    sidecar = PROTOCOL_PATH.with_suffix(".sha256").read_text(
        encoding="ascii"
    ).split()
    if len(sidecar) != 2 or sidecar[1] != "protocol.json":
        raise ValueError("protocol.sha256 has an invalid format")
    if sidecar[0] != sha256_file(PROTOCOL_PATH):
        raise ValueError("protocol.json raw-file SHA-256 differs from frozen sidecar")
    validate_matrix(generate_matrix())
    return hashlib.sha256(canonical_bytes(payload)).hexdigest()


def validate_artifact_protocol(artifact: dict[str, Any]) -> None:
    """Reject missing, stale, or foreign protocol bindings."""
    current = sha256_file(PROTOCOL_PATH)
    observed = artifact.get("protocol_sha256")
    if observed != current:
        raise ValueError(
            "artifact protocol SHA-256 does not match the current frozen protocol"
        )
