import hashlib
import json
from pathlib import Path

import pytest

from experiments.phase3_module_marginal_budget_v1 import MODULES
from experiments.phase3_module_marginal_budget_v1.formal_plan import (
    DEFAULT_RUN_PLAN,
    authoritative_seeds,
    build_formal_run_plan,
    verify_formal_run_plan,
)
from experiments.phase3_module_marginal_budget_v1.curve_results import (
    summarize_formal_curve_results,
)
from experiments.phase3_module_marginal_budget_v1.preflight import (
    DEFAULT_MANIFEST,
)
from experiments.phase3_module_marginal_budget_v1.plot_curve_sweep import (
    render_curve_figures,
)
from experiments.phase3_module_marginal_budget_v1.run_curve_sweep import (
    dispatch,
    select_runs,
)
from experiments.phase3_private_vs_shared_v1.common import sha256_file


@pytest.fixture(scope="module")
def formal_plan():
    return verify_formal_run_plan(DEFAULT_RUN_PLAN)


def _fake_result(run, *, plan_path, training_status="trained"):
    return {
        "curve_run_plan_sha256": sha256_file(plan_path),
        "run_id": run["run_id"],
        "config_id": run["config_id"],
        "sweep_config_id": run["sweep_config_id"],
        "curve_name": run["curve_name"],
        "target_module": run["target_module"],
        "coordinate_dimensions": dict(run["coordinate_dimensions"]),
        "seed": run["seed"],
        "checkpoint_path": "/not-used-in-dispatch-unit-test/checkpoint.pt",
        "vision_encoded_bits": 10,
        "projector_encoded_bits": 20,
        "language_encoded_bits": 30,
        "module_wise_encoded_bits": {
            "vision": 10,
            "projector": 20,
            "language": 30,
        },
        "target_module_encoded_bits": (
            None
            if run["target_module"] is None
            else {
                "vision": 10,
                "projector": 20,
                "language": 30,
            }[run["target_module"]]
        ),
        "total_encoded_bits": 60,
        "development_task_risk": 0.5,
        "semantic_risk_bound": 0.6,
        "visual_gain_guardrail": 0.1,
        "evaluation_role": "development_only",
        "module_codec_paths": {
            "vision": "/not-used/vision.mmb1",
            "projector": "/not-used/projector.mmb1",
            "language": "/not-used/language.mmb1",
        },
        "codec_receipt_path": "/not-used/receipt.json",
        "training_status": training_status,
        "run_status": "complete",
        "status": "complete",
    }


def test_formal_seeds_and_anchor_artifacts_are_ps_authoritative(formal_plan):
    authority = authoritative_seeds()
    assert authority["seeds"] == [43101, 43102, 43103]
    assert formal_plan["formal_seeds"] == authority["seeds"]
    assert formal_plan["expanded_run_count"] == 75
    assert formal_plan["actual_training_run_count"] == 72
    assert formal_plan["reused_anchor_run_count"] == 3
    anchors = [run for run in formal_plan["runs"] if run["anchor_reuse"]]
    assert len(anchors) == 3
    assert {run["seed"] for run in anchors} == set(authority["seeds"])
    assert all(
        run["training_required"] is False
        and Path(run["anchor_source"]["checkpoint_path"]).is_file()
        and sha256_file(Path(run["anchor_source"]["checkpoint_path"]))
        == run["anchor_source"]["checkpoint_sha256"]
        for run in anchors
    )


def test_expanded_run_identities_and_non_target_dimensions(formal_plan):
    runs = formal_plan["runs"]
    assert len({run["run_id"] for run in runs}) == 75
    assert len({(run["sweep_config_id"], run["seed"]) for run in runs}) == 75
    anchor = formal_plan["anchor_config"]["coordinate_dimensions"]
    for run in runs:
        if run["target_module"] is None:
            assert run["coordinate_dimensions"] == anchor
            continue
        assert all(
            run["coordinate_dimensions"][module] == anchor[module]
            for module in MODULES
            if module != run["target_module"]
        )


def test_single_curve_and_all_selection_counts(formal_plan):
    one = select_runs(
        formal_plan,
        config_id="P-4096-vision-coords-194",
        seed=43102,
    )
    assert len(one) == 1
    assert one[0]["seed"] == 43102
    vision = select_runs(formal_plan, curve="vision")
    assert len(vision) == 27
    assert sum(run["training_required"] for run in vision) == 24
    all_runs = select_runs(formal_plan, all_runs=True)
    assert len(all_runs) == 75
    with pytest.raises(ValueError, match="explicit seed"):
        select_runs(formal_plan, config_id="P-4096-vision-coords-194")


def test_dry_run_does_not_create_results(formal_plan, tmp_path):
    selected = select_runs(formal_plan, all_runs=True)
    output = tmp_path / "curve-results"
    receipt = dispatch(
        DEFAULT_RUN_PLAN,
        output,
        selected_runs=selected,
        execute=False,
        retry_failed=False,
    )
    assert receipt["selected_run_count"] == 75
    assert receipt["selected_training_run_count"] == 72
    assert receipt["selected_anchor_reuse_count"] == 3
    assert not output.exists()


def test_source_manifest_hash_change_is_rejected(tmp_path):
    payload = json.loads(DEFAULT_MANIFEST.read_text(encoding="utf-8"))
    copied = tmp_path / DEFAULT_MANIFEST.name
    copied.write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    digest = hashlib.sha256(copied.read_bytes()).hexdigest()
    copied.with_suffix(".sha256").write_text(
        f"{digest}  {copied.name}\n", encoding="ascii"
    )
    with pytest.raises(ValueError, match="frozen SHA-256"):
        build_formal_run_plan(curve_manifest_path=copied)


def test_run_plan_hash_change_is_rejected_before_dispatch(tmp_path):
    copied = tmp_path / DEFAULT_RUN_PLAN.name
    copied.write_bytes(DEFAULT_RUN_PLAN.read_bytes() + b" ")
    copied.with_suffix(".sha256").write_text(
        f"{sha256_file(DEFAULT_RUN_PLAN)}  {copied.name}\n",
        encoding="ascii",
    )
    with pytest.raises(ValueError, match="SHA-256 sidecar"):
        dispatch(
            copied,
            tmp_path / "results",
            selected_runs=[],
            execute=False,
            retry_failed=False,
        )
    assert not (tmp_path / "results").exists()


def test_completed_result_is_never_overwritten(formal_plan, tmp_path):
    run = select_runs(
        formal_plan,
        config_id="P-4096-projector-coords-776",
        seed=43101,
    )[0]
    calls = []

    def worker(selected, **kwargs):
        calls.append(selected["run_id"])
        return _fake_result(selected, plan_path=kwargs["plan_path"])

    first = dispatch(
        DEFAULT_RUN_PLAN,
        tmp_path,
        selected_runs=[run],
        execute=True,
        retry_failed=False,
        worker=worker,
    )
    result_path = tmp_path / run["run_id"] / "run_result.json"
    before = result_path.read_bytes()
    second = dispatch(
        DEFAULT_RUN_PLAN,
        tmp_path,
        selected_runs=[run],
        execute=True,
        retry_failed=False,
        worker=lambda *_args, **_kwargs: pytest.fail(
            "completed worker was called again"
        ),
    )
    assert first["completed"] == [run["run_id"]]
    assert second["skipped"] == [run["run_id"]]
    assert calls == [run["run_id"]]
    assert result_path.read_bytes() == before


def test_failed_run_requires_explicit_retry(formal_plan, tmp_path):
    run = select_runs(
        formal_plan,
        config_id="P-4096-language-coords-396",
        seed=43103,
    )[0]

    def fail(*_args, **_kwargs):
        raise RuntimeError("synthetic dispatch failure")

    first = dispatch(
        DEFAULT_RUN_PLAN,
        tmp_path,
        selected_runs=[run],
        execute=True,
        retry_failed=False,
        worker=fail,
    )
    second = dispatch(
        DEFAULT_RUN_PLAN,
        tmp_path,
        selected_runs=[run],
        execute=True,
        retry_failed=False,
        worker=fail,
    )
    third = dispatch(
        DEFAULT_RUN_PLAN,
        tmp_path,
        selected_runs=[run],
        execute=True,
        retry_failed=True,
        worker=lambda selected, **kwargs: _fake_result(
            selected, plan_path=kwargs["plan_path"]
        ),
    )
    assert first["failed"] == [run["run_id"]]
    assert second["skipped"] == [run["run_id"]]
    assert third["completed"] == third["retried"] == [run["run_id"]]


def test_stale_running_run_requires_explicit_resume(formal_plan, tmp_path):
    run = select_runs(
        formal_plan,
        config_id="P-4096-vision-coords-255",
        seed=43101,
    )[0]

    def interrupt(*_args, **_kwargs):
        raise KeyboardInterrupt

    with pytest.raises(KeyboardInterrupt):
        dispatch(
            DEFAULT_RUN_PLAN,
            tmp_path,
            selected_runs=[run],
            execute=True,
            retry_failed=False,
            worker=interrupt,
        )
    skipped = dispatch(
        DEFAULT_RUN_PLAN,
        tmp_path,
        selected_runs=[run],
        execute=True,
        retry_failed=False,
        worker=lambda *_args, **_kwargs: pytest.fail(
            "stale running worker resumed implicitly"
        ),
    )
    resumed = dispatch(
        DEFAULT_RUN_PLAN,
        tmp_path,
        selected_runs=[run],
        execute=True,
        retry_failed=False,
        resume_running=True,
        worker=lambda selected, **kwargs: _fake_result(
            selected, plan_path=kwargs["plan_path"]
        ),
    )
    assert skipped["skipped_running"] == [run["run_id"]]
    assert resumed["completed"] == resumed["resumed"] == [run["run_id"]]


def test_formal_summary_expands_one_anchor_into_all_three_curves(formal_plan):
    results = []
    for run in formal_plan["runs"]:
        if run["seed"] != 43101:
            continue
        result = _fake_result(
            run,
            plan_path=DEFAULT_RUN_PLAN,
            training_status=(
                "reused_authoritative_p4096" if run["anchor_reuse"] else "trained"
            ),
        )
        bits = {
            module: run["coordinate_dimensions"][module] * 8
            for module in MODULES
        }
        result.update(
            {
                "vision_encoded_bits": bits["vision"],
                "projector_encoded_bits": bits["projector"],
                "language_encoded_bits": bits["language"],
                "module_wise_encoded_bits": bits,
                "target_module_encoded_bits": (
                    None
                    if run["target_module"] is None
                    else bits[run["target_module"]]
                ),
                "total_encoded_bits": sum(bits.values()),
                "development_task_risk": 0.5,
            }
        )
        results.append(result)
    summary = summarize_formal_curve_results(formal_plan, results)
    assert summary["completed_model_count"] == 25
    assert summary["complete"] is False
    curves = summary["by_seed"]["43101"]["curves"]
    assert all(curves[module]["point_count"] == 9 for module in MODULES)
    assert all(
        sum(point["is_anchor"] for point in curves[module]["points"]) == 1
        for module in MODULES
    )
    assert all(
        len(curves[module]["adjacent_differences"]) == 8 for module in MODULES
    )


def test_complete_formal_summary_renders_curve_figures(formal_plan, tmp_path):
    pytest.importorskip("matplotlib")
    results = []
    for run in formal_plan["runs"]:
        result = _fake_result(
            run,
            plan_path=DEFAULT_RUN_PLAN,
            training_status=(
                "reused_authoritative_p4096" if run["anchor_reuse"] else "trained"
            ),
        )
        bits = {
            module: run["coordinate_dimensions"][module] * 8 + run["seed"] % 17
            for module in MODULES
        }
        result.update(
            {
                "vision_encoded_bits": bits["vision"],
                "projector_encoded_bits": bits["projector"],
                "language_encoded_bits": bits["language"],
                "module_wise_encoded_bits": bits,
                "target_module_encoded_bits": (
                    None
                    if run["target_module"] is None
                    else bits[run["target_module"]]
                ),
                "total_encoded_bits": sum(bits.values()),
                "development_task_risk": (
                    0.5
                    + 1e-7 * sum(run["coordinate_dimensions"].values())
                    + 1e-6 * (run["seed"] - 43100)
                ),
            }
        )
        results.append(result)
    summary = summarize_formal_curve_results(formal_plan, results)
    summary_path = tmp_path / "curve_summary.json"
    summary_path.write_text(json.dumps(summary), encoding="utf-8")

    manifest = render_curve_figures(
        summary_path,
        tmp_path / "figures",
        formats=("png",),
        dpi=300,
    )

    assert manifest["status"] == "complete"
    assert manifest["evaluation_role"] == "development_only"
    assert (
        manifest["figures"]["development_risk_curves"]["summary"]
        == "coordinate-wise 3-seed median only"
    )
    assert (
        manifest["figures"]["development_risk_curves"]["individual_points"]
        == "omitted"
    )
    assert (
        manifest["figures"]["marginal_value_curves"]["rendering"]
        == "three-panel median-curve finite-difference lines"
    )
    assert manifest["figures"]["marginal_value_curves"]["invalid_edge_count"] == 0
    assert all(
        Path(figure["files"]["png"]["path"]).is_file()
        and figure["files"]["png"]["bytes"] > 0
        for figure in manifest["figures"].values()
    )
    assert (tmp_path / "figures" / "figure_manifest.json").is_file()


def test_anchor_runtime_never_calls_training(formal_plan, tmp_path, monkeypatch):
    from experiments.phase3_module_marginal_budget_v1 import formal_runtime

    run = next(run for run in formal_plan["runs"] if run["anchor_reuse"])
    binding = {
        "curve_run_plan_sha256": sha256_file(DEFAULT_RUN_PLAN),
        "curve_manifest_sha256": formal_plan["curve_manifest_sha256"],
        "phase3_ps_protocol_sha256": "test",
        "run_id": run["run_id"],
        "evaluation_role": "development_only",
        "git_commit": "test",
        "git_branch": "test",
    }
    monkeypatch.setattr(
        formal_runtime, "_formal_binding", lambda *_args, **_kwargs: binding
    )
    monkeypatch.setattr(
        formal_runtime,
        "train_candidate",
        lambda *_args, **_kwargs: pytest.fail("anchor attempted training"),
    )
    monkeypatch.setattr(
        formal_runtime,
        "_module_codec",
        lambda *_args, **_kwargs: (
            {
                "vision_encoded_bits": 10,
                "projector_encoded_bits": 20,
                "language_encoded_bits": 30,
                "total_encoded_bits": 60,
            },
            {},
        ),
    )
    monkeypatch.setattr(
        formal_runtime,
        "_development_result",
        lambda *_args, **_kwargs: {
            "evaluation_role": "development_only",
            "development_task_risk": 0.5,
            "semantic_risk_bound": 0.6,
            "visual_gain_guardrail": 0.1,
        },
    )
    result = formal_runtime.execute_formal_run(
        run,
        plan_path=DEFAULT_RUN_PLAN,
        results_root=tmp_path,
        artifact_root=None,
        device="cuda:0",
    )
    assert result["training_status"] == "reused_authoritative_p4096"
    assert result["target_module_encoded_bits"] is None
    assert result["target_module_encoded_bits_by_curve"] == {
        "vision": 10,
        "projector": 20,
        "language": 30,
    }
