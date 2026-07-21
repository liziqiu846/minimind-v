import os
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STAGE2_PROTOCOL = ROOT / "experiments/stage2_protocol_v2.json"
VALIDATION = ROOT / "dataset/stage2_confirm_v2_seed2028/validation.parquet"
VALIDATION_SHA256 = "72456b3a6f43800a2302fbc376f905335c9bb52b5b8bdad5ddee07ec99f942e8"


class Phase3Stage2IntegrationTests(unittest.TestCase):
    def test_strict_confirmation_fixture_parity(self):
        artifact_root = os.environ.get("STAGE2_ARTIFACT_ROOT")
        if not artifact_root or not VALIDATION.is_file():
            self.skipTest(
                "blocked_integration_fixture: verified M1 and/or strict confirmation validation unavailable"
            )

        import torch
        from transformers import AutoTokenizer

        if not torch.cuda.is_available():
            self.skipTest("blocked_integration_fixture: CUDA is unavailable")

        from dataset.stage2_dataset import Stage2CaptionDataset, stage2_collate
        from experiments.evaluate_stage2_risk import sample_risk_bits
        from experiments.phase3.canonical_io import sha256_bytes, snapshot_file
        from experiments.phase3.caption_scorer import smoothed_nll_bits
        from experiments.phase3.stage2_adapter_loader import load_verified_model
        from experiments.stage2_protocol import Stage2Protocol

        self.assertEqual(sha256_bytes(snapshot_file(VALIDATION)), VALIDATION_SHA256)
        protocol = Stage2Protocol.load(STAGE2_PROTOCOL, require_frozen=True)
        protocol.verify_immutable_inputs()
        confirmation = protocol.verify_confirmation_data(VALIDATION, "validation")
        self.assertEqual(confirmation["data_sha256"], VALIDATION_SHA256)

        device = torch.device(os.environ.get("PHASE3_INTEGRATION_DEVICE", "cuda:0"))
        model, metadata, loaded_protocol = load_verified_model(
            "M1-root-none",
            artifact_root=Path(artifact_root),
            stage2_protocol_path=STAGE2_PROTOCOL,
            device=device,
            dtype=torch.float32,
        )
        self.assertEqual(metadata["model_group"], "M1")
        self.assertIsNone(metadata["mapping_root"])
        tokenizer = AutoTokenizer.from_pretrained(
            loaded_protocol.asset_path("tokenizer"), local_files_only=True
        )
        dataset = Stage2CaptionDataset(
            VALIDATION,
            tokenizer,
            model_group="M1",
            processor=model.processor,
            max_length=loaded_protocol.payload["training"]["max_sequence_length"],
            image_token_count=loaded_protocol.payload["model"]["image_token_count"],
        )
        sample_ids = []
        for index in range(len(dataset)):
            row = dataset.dataset[index]
            self.assertIn("sample_id", row, "strict validation row is missing sample_id")
            sample_ids.append(str(row["sample_id"]))
        self.assertEqual(
            len(sample_ids), len(set(sample_ids)),
            "strict validation sample_id values are not unique",
        )
        ordered_indices = sorted(
            range(len(dataset)),
            key=lambda index: str(dataset.dataset[index]["sample_id"]).encode("utf-8"),
        )
        selected = None
        for index in ordered_indices:
            try:
                selected = dataset[index]
                break
            except (KeyError, TypeError, ValueError, OSError):
                continue
        self.assertIsNotNone(selected, "strict validation has no processable M1 row")
        input_ids, labels, pixels = stage2_collate([selected])
        input_ids = input_ids.to(device)
        labels = labels.to(device)
        pixels = (
            {name: value.to(device) for name, value in pixels.items()}
            if isinstance(pixels, dict)
            else pixels.to(device)
        )

        try:
            for condition, pixel_values in (("correct", pixels), ("none", None)):
                with self.subTest(condition=condition), torch.inference_mode(), torch.autocast(
                    device_type="cuda", dtype=torch.bfloat16
                ):
                    logits = model(
                        input_ids=input_ids,
                        attention_mask=None,
                        pixel_values=pixel_values,
                    ).logits
                phase3_values, phase3_counts = smoothed_nll_bits(logits, labels, alpha=0.5)
                stage2_values, stage2_counts = sample_risk_bits(logits, labels, alpha=0.5)
                self.assertTrue(torch.equal(phase3_counts, stage2_counts))
                self.assertTrue(
                    torch.allclose(phase3_values, stage2_values, rtol=0.0, atol=1e-5),
                    f"{condition} Phase 3 score differs from frozen Stage 2 score",
                )
        finally:
            del model
            torch.cuda.empty_cache()


if __name__ == "__main__":
    unittest.main()
