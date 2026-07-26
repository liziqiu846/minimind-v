"""Read and verify the existing M2 allocation authority."""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

from .common import REPO_ROOT, load_json, sha256_file

PROTOCOL_PATH = REPO_ROOT / "experiments/stage2_protocol_v2.json"
CODE_PATH = REPO_ROOT / "model/global_subspace_lora.py"


def _code_group_dimensions(path: Path) -> dict[str, dict[str, int]]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in tree.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            target = node.targets[0] if isinstance(node, ast.Assign) else node.target
            if isinstance(target, ast.Name) and target.id == "GROUP_DIMENSIONS":
                return ast.literal_eval(node.value)
    raise ValueError("GROUP_DIMENSIONS is absent from Stage 2 authority code")


def read_m2_authority() -> dict[str, Any]:
    protocol = load_json(PROTOCOL_PATH)
    targets = protocol["model"]["targets"]
    weights = {
        name: int(targets[name]["factor_elements"])
        for name in ("vision", "projector", "language")
    }
    declared = protocol["model"]["groups"]["M2"]
    code_dimensions = _code_group_dimensions(CODE_PATH)["M2"]
    if len(declared["coordinate_groups"]) != len(declared["coordinate_dimensions"]):
        raise ValueError("Stage 2 M2 group names/dimensions have different lengths")
    protocol_dimensions = dict(zip(
        declared["coordinate_groups"], declared["coordinate_dimensions"]
    ))
    if code_dimensions != protocol_dimensions:
        raise ValueError("Stage 2 M2 code/protocol dimensions disagree")
    if sum(weights.values()) <= 0 or any(value <= 0 for value in weights.values()):
        raise ValueError("Stage 2 M2 factor-element weights are invalid")
    return {
        "factor_elements": weights,
        "current_dimensions": protocol_dimensions,
        "protocol_relative_path": str(PROTOCOL_PATH.relative_to(REPO_ROOT)),
        "protocol_sha256": sha256_file(PROTOCOL_PATH),
        "code_relative_path": str(CODE_PATH.relative_to(REPO_ROOT)),
        "code_sha256": sha256_file(CODE_PATH),
        "verification": "factor_elements_from_protocol_and_M2_dimensions_match_code",
    }
