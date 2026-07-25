import hashlib

import torch

from experiments.phase3_risk_v1.budget_adapter import (
    check_current_mapping_equivalence,
)
from experiments.phase3_risk_v1.budget_codec import (
    check_current_codec_equivalence,
)
from experiments.phase4_m4_v1.mms2_v2 import decode_mms2_any
from experiments.quantize_stage2_adapter import (
    decode_mms2,
    encode_mms2,
)
from experiments.stage2_protocol import load_target_registry
from model.global_subspace_lora import GROUP_DIMENSIONS


FROZEN_SHA256 = {
    "model/global_subspace_lora.py": (
        "4fcb3f0bf8786fe8eb8fce93bac32a4ec8341863c986f42a9f7c2118e2f12908"
    ),
    "experiments/stage2_model.py": (
        "fa69e769a0c482b986ad1058498c156f6eaa26aad633a8807f7904d29593c0f4"
    ),
    "experiments/quantize_stage2_adapter.py": (
        "d42a0f0eecfd3c6977d04a3f446c48369e9505dd65d1c5f577b4e92ccc6cf785"
    ),
}


def test_explicit_frozen_core_files_keep_baseline_bytes():
    for path, expected in FROZEN_SHA256.items():
        assert hashlib.sha256(open(path, "rb").read()).hexdigest() == expected


def test_old_m2_m3_mms2_v1_decode_and_reencode_are_byte_exact():
    for model_group in ("M2", "M3"):
        coordinates = {
            name: torch.linspace(-1.0, 1.0, dimension)
            for name, dimension in GROUP_DIMENSIONS[model_group].items()
        }
        for root in (43101, 43102, 43103):
            archive, _ = encode_mms2(coordinates, model_group, root)
            old_decoded, old_metadata = decode_mms2(archive)
            any_decoded, any_metadata = decode_mms2_any(archive)
            assert any_metadata["legacy_byte_exact_decoder"] is True
            assert any_metadata["model_group"] == model_group
            assert any_metadata["mapping_root"] == root
            assert old_metadata["archive_bytes"] == len(archive)
            for name in old_decoded:
                assert torch.equal(any_decoded[name], old_decoded[name])
            reencoded, _ = encode_mms2(old_decoded, model_group, root)
            assert reencoded == archive


def test_frozen_current_codec_and_mapping_equivalence_still_pass():
    codec = check_current_codec_equivalence()
    mapping = check_current_mapping_equivalence(load_target_registry())
    assert codec["status"] == "passed"
    assert mapping["status"] == "passed"
    assert all(
        row["old_new_byte_equivalence"] for row in codec["checks"]
    )
    assert all(
        row["mapping_tensor_equivalence"] == "exact"
        for row in mapping["checks"]
    )
