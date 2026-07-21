import tempfile
import unittest
from pathlib import Path

import numpy as np

from experiments.phase3.aggregate_by_image import aggregate_rows, empirical_metric_means, visual_row_metrics
from experiments.phase3.build_phase3_bundle import _public_value, build_bundle
from experiments.phase3.canonical_io import (
    atomic_write_bytes, atomic_write_json, atomic_write_jsonl, inventory_files,
    load_json_snapshot, sha256_bytes, snapshot_file,
)
from experiments.phase3.nll_diagnostics import write_nll_store
from experiments.phase3.runner_common import NLL_DISCLAIMER, verified_image_payload
from experiments.phase3.runner_common import _degenerate_sensitivity
from experiments.phase3.verify_phase3_bundle import verify_bundle


class Phase3BundleTests(unittest.TestCase):
    def _synthetic_run(self, root: Path):
        static = root / "static"
        run = root / "run"
        static.mkdir(); run.mkdir()
        protocol = static / "phase3_protocol_candidate_v4.json"
        code_manifest = static / "phase3_code_manifest_v2.json"
        authority = static / "phase3_stage2_authority_manifest_v2.json"
        repository_static = Path(__file__).resolve().parents[1] / "experiments/phase3"
        atomic_write_bytes(
            code_manifest,
            snapshot_file(repository_static / "phase3_code_manifest_v2.json"),
        )
        atomic_write_bytes(
            authority,
            snapshot_file(repository_static / "phase3_stage2_authority_manifest_v2.json"),
        )
        expected = run / "expected_model_registry.json"
        receipt = run / "model_verification_receipt.json"
        data = run / "data_manifest.json"
        split = run / "split_manifest.json"
        atomic_write_bytes(
            expected,
            snapshot_file(repository_static / "phase3_expected_model_registry.json"),
        )
        registry = load_json_snapshot(expected)
        receipt_rows = []
        for model in registry["models"]:
            receipt_rows.append({
                "model_id": model["model_id"],
                "method": model["method"],
                "mapping_root": model["mapping_root"],
                "resolved_relative_path": model["artifact_relative_path"],
                "expected_sha256": model["artifact_sha256"],
                "actual_sha256": model["artifact_sha256"],
                "expected_size_bytes": model["artifact_size_bytes"],
                "actual_size_bytes": model["artifact_size_bytes"],
                "decoded_method": model["method"],
                "decoded_mapping_root": model["mapping_root"],
                "status": "verified",
                "error_code": None,
            })
        atomic_write_json(receipt, {
            "schema_version": 2,
            "receipt_type": "phase3_stage2_artifact_verification_v3",
            "artifact_batch_id": registry["artifact_batch_id"],
            "authority_id": registry["authority_id"],
            "stage2_reference_commit": registry["stage2_reference_commit"],
            "rerun_source_commit": registry["rerun_source_commit"],
            "recovery_verification_sha256": registry["recovery_verification_sha256"],
            "expected_model_registry_sha256": sha256_bytes(snapshot_file(expected)),
            "authority_manifest_sha256": registry["authority_manifest_sha256"],
            "decoder_id": registry["decoder_id"],
            "decoder_source_sha256": registry["decoder_source_sha256"],
            "model_count": 10,
            "overall_status": "verified",
            "models": receipt_rows,
        })
        indices = [
            {"row_index": i, "row_key": f"x:{i}", "category": "x", "numeric_id": i, "filename": f"{i + 1:012d}.jpg", "source_row_sha256": f"{i + 1:064x}"}
            for i in range(8)
        ]
        index_path = run / "canonical_row_index.jsonl"
        atomic_write_jsonl(index_path, indices)
        index_raw = snapshot_file(index_path)
        commitment = sha256_bytes(b"".join(
            str(row["row_index"]).encode("ascii") + b"\0" + row["source_row_sha256"].encode("ascii") + b"\n"
            for row in indices
        ))
        atomic_write_json(split, {"split_version": "phase3-v1", "canonical_row_commitment_sha256": commitment})
        degenerate_path = run / "degenerate_rows.json"
        atomic_write_json(degenerate_path, {
            "schema_version": 1, "degenerate_row_count": 0, "affected_image_group_count": 0,
            "type_counts": {}, "rows": [],
        })
        degenerate_raw = snapshot_file(degenerate_path)
        atomic_write_json(data, {
            "manifest_type": "synthetic-data",
            "canonical_row_commitment_sha256": commitment,
            "artifacts": [
                {"relative_path": "canonical_row_index.jsonl", "size_bytes": len(index_raw), "sha256": sha256_bytes(index_raw)},
                {"relative_path": "degenerate_rows.json", "size_bytes": len(degenerate_raw), "sha256": sha256_bytes(degenerate_raw)},
            ],
        })
        candidate = load_json_snapshot(repository_static / "phase3_protocol_candidate_v4.json")
        candidate["data_manifest_sha256"] = sha256_bytes(snapshot_file(data))
        candidate["split_manifest_sha256"] = sha256_bytes(snapshot_file(split))
        candidate["overlap_audit_input_sha256"] = None
        candidate["missing_required_fields"] = [
            "complete_overlap_input_definition", "overlap_audit_input_sha256",
        ]
        candidate["candidate_status"] = "incomplete"
        atomic_write_json(protocol, candidate)
        values = {
            "b_img_pos1_raw": 0.2, "b_img_pos1": 0.2,
            "b_img_pos2_raw": 0.4, "b_img_pos2": 0.4,
            "b_img_neg_raw": 1.1, "b_img_neg": 1.1,
            "b_none_pos1_raw": 0.2, "b_none_pos1": 0.2,
            "b_none_pos2_raw": 0.4, "b_none_pos2": 0.4,
            "b_none_neg_raw": 1.0, "b_none_neg": 1.0,
            "raw_image_margin": 0.8,
            "raw_none_margin": 0.7,
            "raw_visual_increment": 0.1,
        }
        rows = [
            {
                "schema_version": 1, "run_mode": "smoke", "model_id": "M1-root-none", "method": "M1",
                "mapping_root": None, **index, **visual_row_metrics(values),
            }
            for index in indices
        ]
        groups = aggregate_rows(rows)
        atomic_write_jsonl(run / "row_level_results.jsonl", rows)
        atomic_write_jsonl(run / "image_group_results.jsonl", groups)
        atomic_write_json(run / "metrics_summary.json", {
            "schema_version": 1,
            "run_mode": "smoke",
            "bound_name": None,
            "certificate_status": "not_applicable_non_certifying",
            "confidence_statement": None,
            "complete_model_independence_disclosure": None,
            "estimand_scope": (
                "SugarCrepe++ represented target image-text construction distribution conditional on "
                "no project-history image overlap"
            ),
            "finite_population_guarantee": False,
            "all_natural_images_claim": False,
            "external_base_pretraining_overlap": "unknown",
            "certificate_scope": "project_controlled_image_group_disjoint_certifying_subset_only",
            "delta_families_joint_95_percent_claim": False,
            "m0_cross_input_comparison": "descriptive_different_input_conditions_only",
            "models": [{
                "model_id": "M1-root-none", "n_unique_image_groups": 8,
                "empirical_risks": empirical_metric_means(groups),
                "bound_status": "not_applicable_non_certifying",
                "bounds": {name: None for name in ("positive_brier_risk", "visual_semantic_loss", "positive_invariance_loss")},
                "exploratory_compression_bounds": {name: None for name in ("positive_brier_risk", "visual_semantic_loss", "positive_invariance_loss")},
            }],
        })
        nll_entries = []
        for index in indices:
            for condition in ("correct", "none"):
                for role in ("pos1", "pos2", "negative"):
                    nll_entries.append({**index, "model_id": "M1-root-none", "condition": condition, "caption_role": role, "values": np.array([1.0, 2.0], dtype=np.float32)})
        summary = write_nll_store(run / "nll/M1-root-none", nll_entries)
        atomic_write_json(run / "nll_tail_summary.json", {
            "schema_version": 1, "disclaimer": NLL_DISCLAIMER,
            "models": {"M1-root-none": summary},
        })
        for name, value in (
            ("numerical_diagnostics.json", {
                "token_brier_below_zero_count": 0, "token_brier_above_two_count": 0,
                "caption_clip_low_count": 0, "caption_clip_high_count": 0, "nan_inf_count": 0,
            }),
            ("timing.json", {"elapsed_seconds": 0.1}),
            ("degenerate_sensitivity_summary.json", _degenerate_sensitivity(rows, {"rows": []})),
            ("run_config.json", {
                "device": "cpu", "logical_data": "prepared",
                "model_ids": ["M1-root-none"],
                "filenames": [row["filename"] for row in indices],
            }),
            ("environment.json", {"python": "test", "device": "cpu"}),
            ("run_status.json", {"schema_version": 1, "status": "success", "run_mode": "smoke"}),
        ):
            atomic_write_json(run / name, value)
        filenames_hash = sha256_bytes(("\n".join(row["filename"] for row in indices) + "\n").encode("utf-8"))
        manifest = {
            "schema_version": 1, "run_mode": "smoke", "run_status": "success",
            "protocol_sha256": sha256_bytes(snapshot_file(protocol)),
            "phase3_source_commit": None, "protocol_repository_commit": None,
            "protocol_tag": None, "protocol_tag_object": None,
            "phase3_code_manifest_sha256": sha256_bytes(snapshot_file(code_manifest)),
            "stage2_authority_manifest_sha256": sha256_bytes(snapshot_file(authority)),
            "expected_model_registry_sha256": sha256_bytes(snapshot_file(expected)),
            "model_verification_receipt_sha256": sha256_bytes(snapshot_file(receipt)),
            "data_manifest_sha256": sha256_bytes(snapshot_file(data)),
            "split_manifest_sha256": sha256_bytes(snapshot_file(split)),
            "overlap_audit_receipt_sha256": None, "formal_approval_sha256": None,
            "ordered_model_ids": ["M1-root-none"], "ordered_filenames_sha256": filenames_hash,
            "row_result_count": 8, "image_group_result_count": 8,
            "files": inventory_files(run, excluded=("run_manifest.json",)),
            "exclusion_rule": "run_manifest.json and transient lock/temp files are excluded",
        }
        atomic_write_json(run / "run_manifest.json", manifest)
        return run, protocol, code_manifest

    def test_builder_and_cpu_verifier_recompute(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            run, protocol, code = self._synthetic_run(root)
            bundle = root / "bundle"
            result = build_bundle(run, protocol, code, bundle)
            verified = verify_bundle(bundle)
            self.assertEqual(result["bundle_content_hash"], verified["bundle_content_hash"])
            self.assertEqual(verified["row_count"], 8)
            self.assertFalse((bundle / "data/sugarcrepe_pp_canonical.jsonl").exists())
            atomic_write_bytes(bundle / "results/metrics_summary.json", b"{}\n")
            with self.assertRaises(ValueError):
                verify_bundle(bundle)

    def test_public_config_sanitizes_paths_and_rejects_secrets(self):
        value = _public_value({"artifact_root": "/home/person/private"})
        self.assertEqual(value["artifact_root"]["logical_path_alias"], "artifact_root")
        with self.assertRaises(ValueError):
            _public_value({"token": "hf_secretvalue"})

    def test_image_bytes_are_rechecked_at_use_time(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            image = root / "000000000001.jpg"
            atomic_write_bytes(image, b"first")
            expected = {"filename": image.name, "status": "ready", "size_bytes": 5, "sha256": sha256_bytes(b"first")}
            self.assertEqual(verified_image_payload(root, image.name, expected), b"first")
            atomic_write_bytes(image, b"changed")
            with self.assertRaisesRegex(RuntimeError, "image_changed_after_manifest"):
                verified_image_payload(root, image.name, expected)


if __name__ == "__main__":
    unittest.main()
