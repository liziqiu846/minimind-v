from __future__ import annotations

import copy
import hashlib
import json
import random

import numpy as np
import torch

from experiments.phase3_image_group_dependence_sgd_v1.configs import generate_matrix
from experiments.phase3_image_group_dependence_sgd_v1.codec import (
    decode_coordinates,
    encode_and_verify,
)
from experiments.phase3_image_group_dependence_sgd_v1.diagnosis import (
    capture_rng,
    diagnose_replacement,
    fixed_index,
    rng_equal,
)


class ToyModel(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.linear = torch.nn.Linear(3, 2)
        self.dropout = torch.nn.Dropout(0.25)

    def forward(self, input_ids, labels, pixel_values=None):
        logits = self.linear(self.dropout(input_ids.float()))
        loss = torch.nn.functional.cross_entropy(logits, labels)
        return type("Output", (), {"loss": loss})


def _seed(value: int) -> None:
    random.seed(value)
    np.random.seed(value)
    torch.manual_seed(value)


def _checkpoint_bytes(model, optimizer, step, lr):
    digest = hashlib.sha256()
    for name, value in sorted(model.state_dict().items()):
        digest.update(name.encode("utf-8") + b"\0")
        digest.update(value.detach().cpu().contiguous().numpy().tobytes())
    optimizer_receipt = {
        "state": optimizer.state_dict()["state"],
        "param_groups": optimizer.state_dict()["param_groups"],
        "step": step,
        "lr": lr,
    }
    digest.update(
        json.dumps(optimizer_receipt, sort_keys=True, separators=(",", ":")).encode()
    )
    return digest.digest()


def _trajectory(diagnosis_enabled: bool):
    _seed(43101)
    model = ToyModel()
    optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
    batches = [
        (torch.randn(4, 3), torch.tensor([0, 1, 0, 1]), None)
        for _ in range(5)
    ]
    ghost = (torch.tensor([9.0, -2.0, 1.0]), torch.tensor(1), None)
    step_receipts = []
    for step, batch in enumerate(batches):
        lr = 0.1 - 0.01 * step
        optimizer.param_groups[0]["lr"] = lr
        if diagnosis_enabled:
            diagnose_replacement(
                model,
                list(model.parameters()),
                batch,
                ghost,
                selected_position=fixed_index(43101, step, "batch-position", 4),
                accumulation=1,
            )
        optimizer.zero_grad(set_to_none=True)
        model(input_ids=batch[0], labels=batch[1]).loss.backward()
        optimizer.step()
        step_receipts.append(
            {
                "parameters": [p.detach().clone() for p in model.parameters()],
                "optimizer": copy.deepcopy(optimizer.state_dict()),
                "lr": optimizer.param_groups[0]["lr"],
                "rng": capture_rng(),
            }
        )
    return (
        step_receipts,
        _checkpoint_bytes(model, optimizer, len(batches), lr),
        capture_rng(),
    )


def test_matrix_is_exact_preregistered_12():
    matrix = generate_matrix()
    assert len(matrix) == 12
    assert {row["budget"] for row in matrix} == {2048, 8192}
    assert 4096 not in {row["budget"] for row in matrix}


def test_variable_budget_mms2_round_trip_has_bare_group_names():
    for row in generate_matrix():
        coordinates = {
            name: torch.zeros(dimension)
            for name, dimension in row["coordinate_dimensions"].items()
        }
        archive, receipt = encode_and_verify(
            coordinates, row["structure"], row["seed"]
        )
        decoded, metadata = decode_coordinates(archive)
        assert set(decoded) == set(row["coordinate_dimensions"])
        assert metadata["archive_bits"] == receipt["archive_bits"]


def test_diagnosis_on_off_trajectory_is_bit_identical():
    off, off_checkpoint, off_rng = _trajectory(False)
    on, on_checkpoint, on_rng = _trajectory(True)
    assert len(off) == len(on)
    for left, right in zip(off, on):
        assert left["lr"] == right["lr"]
        assert left["optimizer"] == right["optimizer"]
        assert all(
            torch.equal(a, b)
            for a, b in zip(left["parameters"], right["parameters"])
        )
        assert rng_equal(left["rng"], right["rng"])
    assert off_checkpoint == on_checkpoint
    assert rng_equal(off_rng, on_rng)
