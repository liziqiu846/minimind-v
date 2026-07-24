import csv
import json

import pytest

from experiments.phase3_risk_v1.summarize_and_plot import (
    join_summary_rows,
    paired_differences,
)
from experiments.phase3_risk_v1.analyze_budget_matrix import _budget_summary
from experiments.phase3_risk_v1.risk_metrics import derive_risk_row
from experiments.phase3_v6.scoring.common import read_json, read_jsonl


def test_old_v6_record_is_readable_and_historical_fields_survive():
    source = read_jsonl(
        "experiments/phase3_v6/scoring/model_record_scores/"
        "M2-root-43101.jsonl"
    )[0]
    result = derive_risk_row(source)
    assert result["q_mismatch_k5"] == source["q_mismatch_k5"]
    assert result["d_k5"] == source["d_k5"]
    assert result["identity_error"] <= 1e-6
    legacy = read_json(
        "experiments/phase3_v6/scoring/model_summaries/"
        "M2-root-43101.json"
    )
    assert legacy["model_id"] == "M2-root-43101"
    assert isinstance(legacy["mu_k5"], float)


def test_frozen_mismatch_manifest_has_exactly_five_distinct_nonself_donors():
    rows = read_jsonl(
        "experiments/phase3_v6/mismatch_audit/mismatch_manifest_k5.jsonl"
    )
    assert rows
    for row in rows:
        donors = [entry["donor_filename"] for entry in row["donor_rounds"]]
        assert [entry["round_id"] for entry in row["donor_rounds"]] == [
            1,
            2,
            3,
            4,
            5,
        ]
        assert len(set(donors)) == 5
        assert row["target_filename"] not in donors


def test_join_and_pair_require_complete_equal_budget_pairs(tmp_path):
    csv_path = tmp_path / "models.csv"
    columns = [
        "model_id",
        "method",
        "budget",
        "experiment_seed",
        "empirical_language_risk",
        "empirical_visual_risk",
        "empirical_total_semantic_risk",
        "empirical_visual_gain",
        "exploratory_language_radius",
        "exploratory_visual_radius",
        "certified",
    ]
    rows = [
        {
            "model_id": f"{method}-current-seed-43101",
            "method": method,
            "budget": "current",
            "experiment_seed": "43101",
            "empirical_language_risk": "0.2",
            "empirical_visual_risk": "0.4",
            "empirical_total_semantic_risk": "0.0",
            "empirical_visual_gain": "0.2",
            "exploratory_language_radius": "0.05",
            "exploratory_visual_radius": "0.05",
            "certified": "False",
        }
        for method in ("M2", "M3")
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    complexity_path = tmp_path / "complexity.json"
    complexity_path.write_text(
        json.dumps(
            {
                "models": [
                    {
                        "model_id": row["model_id"],
                        "coordinate_count_total": 4096,
                        "archive_bits": 100,
                        "external_selection_bits": 5,
                        "external_hyperparameter_bits": 0,
                        "total_description_bits": 105,
                    }
                    for row in rows
                ]
            }
        ),
        encoding="utf-8",
    )
    joined = join_summary_rows(csv_path, complexity_path)
    pairs = paired_differences(joined)
    assert len(pairs) == 1
    assert pairs[0]["delta_description_bits"] == 0
    with pytest.raises(ValueError, match="incomplete"):
        paired_differences(joined[:1])


def test_budget_summary_reports_population_std_and_pair_sign_consistency():
    models = []
    pairs = []
    for budget in ("low", "current", "high"):
        for root_index, root in enumerate((43101, 43102, 43103)):
            for method_index, method in enumerate(("M2", "M3")):
                models.append(
                    {
                        "budget": budget,
                        "method": method,
                        "experiment_seed": root,
                        "empirical_language_risk": 0.4 + 0.01 * method_index,
                        "empirical_visual_risk": 0.5 + 0.01 * method_index,
                        "empirical_total_semantic_risk": (
                            0.4 + 0.03 * method_index
                        ),
                        "empirical_visual_gain": -0.02 * method_index,
                        "archive_bits": 100 + 5 * method_index + root_index,
                        "total_description_bits": (
                            105 + 5 * method_index + root_index
                        ),
                    }
                )
            pairs.append(
                {
                    "budget": budget,
                    "experiment_seed": root,
                    "delta_language_risk": 0.01,
                    "delta_visual_risk": 0.01,
                    "delta_total_semantic_risk": 0.03,
                    "delta_description_bits": 5,
                }
            )
    result = _budget_summary(models, pairs)
    assert len(result) == 6
    assert all(
        row["standard_deviation_definition"] == "population"
        for row in result
    )
    assert all(row["delta_visual_risk_sign_consistent"] for row in result)
    assert all(
        row["delta_visual_risk_signs"] == "positive|positive|positive"
        for row in result
    )
