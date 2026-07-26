from __future__ import annotations

from typing import Any, Mapping, Sequence


def aggregate_models(configs: Sequence[Mapping[str, Any]],
                     results: Mapping[str, Mapping[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for config in configs:
        result = results.get(str(config["config_id"]), {})
        rows.append({
            "structure": config["structure"],
            "budget": config["budget"],
            "seed": config["seed"],
            "semantic_bound": result.get("semantic_bound"),
            "visual_gain_lower_bound": result.get("visual_gain_lower_bound"),
            "coded_bits": result.get("coded_bits"),
            "training_status": result.get("training_status", config["training_status"]),
        })
    return rows
