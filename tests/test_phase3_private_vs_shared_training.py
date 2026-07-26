import json
import subprocess
import sys

import pytest

from experiments.phase3_private_vs_shared_v1 import run_matrix
from experiments.phase3_private_vs_shared_v1.artifacts import (
    bindings, validate_bindings, write_json_exclusive,
)
from experiments.phase3_private_vs_shared_v1.codec import encode_coordinates
from experiments.phase3_private_vs_shared_v1.common import load_json
from experiments.phase3_private_vs_shared_v1.configs import (
    generate_matrix, matrix_sha256,
)
from experiments.phase3_private_vs_shared_v1.parameterization import CoordinateStore
from experiments.phase3_private_vs_shared_v1.protocol_tools import (
    PROTOCOL_PATH, validate_frozen_protocol,
)


def test_protocol_freezes_formal_entries_and_matrix_hash():
    protocol = load_json(PROTOCOL_PATH)
    assert protocol["execution_limit"]["formal_training_allowed"] is True
    assert protocol["candidate_matrix_sha256"] == matrix_sha256()
    assert validate_frozen_protocol()


def test_new_training_code_has_no_legacy_experiment_dependency():
    root = PROTOCOL_PATH.parent
    source = "\n".join(
        path.read_text(encoding="utf-8") for path in root.glob("*.py")
    )
    assert "phase3_risk_v1" not in source
    assert "M4" not in source


def test_codec_encodes_shared_once_and_private_separately():
    private = CoordinateStore(
        "P", {"vision": 2, "projector": 3, "language": 4}
    )
    shared = CoordinateStore("S", {"shared": 9})
    _, p_receipt = encode_coordinates(
        dict(private.coordinates), "P", 43101
    )
    _, s_receipt = encode_coordinates(
        dict(shared.coordinates), "S", 43101
    )
    assert [row["name"] for row in p_receipt["coordinate_groups"]] == [
        "vision", "projector", "language"
    ]
    assert [row["name"] for row in s_receipt["coordinate_groups"]] == ["shared"]


def test_old_protocol_or_matrix_artifact_is_rejected():
    current = bindings()
    validate_bindings(current)
    with pytest.raises(ValueError, match="bindings"):
        validate_bindings({**current, "protocol_sha256": "old"})
    with pytest.raises(ValueError, match="bindings"):
        validate_bindings({**current, "candidate_matrix_sha256": "old"})


def test_run_manifest_is_exclusive(tmp_path):
    path = tmp_path / "run.json"
    write_json_exclusive(path, {"frozen": True})
    with pytest.raises(FileExistsError):
        write_json_exclusive(path, {"frozen": False})


def test_single_candidate_two_batch_smoke(tmp_path):
    command = [
        sys.executable, "-m",
        "experiments.phase3_private_vs_shared_v1.train_one",
        "--config-id", generate_matrix()[0]["config_id"],
        "--output-root", str(tmp_path),
        "--smoke-batches", "2",
    ]
    result = subprocess.run(command, check=True, text=True, capture_output=True)
    receipt = json.loads(result.stdout)
    assert receipt["status"] == "passed"
    assert receipt["batches"] == 2
    assert receipt["formal_training"] is False


def test_dispatch_skips_complete_and_requires_resume_for_failed(
    tmp_path, monkeypatch
):
    configs = generate_matrix()[:2]
    monkeypatch.setattr(run_matrix, "generate_matrix", lambda: configs)
    output = tmp_path / "outputs"
    commands = [[sys.executable, "-c", "pass"] for _ in configs]
    manifest = {
        **bindings(),
        "status": "frozen_before_dispatch",
        "selected_device_indices": ["0"],
        "output_root": str(output),
        "commands": commands,
    }
    manifest_path = tmp_path / "run.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    for config, status in zip(configs, ("complete", "failed")):
        directory = output / config["config_id"]
        directory.mkdir(parents=True)
        (directory / "status.json").write_text(json.dumps({
            **bindings(), "status": status,
        }), encoding="utf-8")
    first = run_matrix.dispatch(manifest_path, resume=False)
    assert first["dispatched"] == []
    assert len(first["skipped"]) == 2
    second = run_matrix.dispatch(manifest_path, resume=True)
    assert second["dispatched"] == [configs[1]["config_id"]]
    assert second["skipped"] == [configs[0]["config_id"]]


def test_dispatch_records_failure_even_before_trainer_receipt(tmp_path):
    current = bindings()
    result = run_matrix._run(
        [sys.executable, "-c", "raise SystemExit(7)"],
        "0", tmp_path / "failure.log", "candidate-x", tmp_path, current,
    )
    assert result["returncode"] == 7
    status = json.loads(
        (tmp_path / "candidate-x/status.json").read_text(encoding="utf-8")
    )
    assert status["status"] == "failed"
    assert status["error_type"] == "SubprocessFailureBeforeTrainerReceipt"
    validate_bindings(status)
