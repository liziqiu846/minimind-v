import tempfile
import unittest
from pathlib import Path

import torch

from experiments.quantize_checkpoint import (
    decode_archive,
    encode_archive,
    pack_codes,
    read_metadata,
    unpack_codes,
)


class QuantizedCheckpointTest(unittest.TestCase):
    def test_packed_codes_round_trip_for_all_supported_widths(self):
        for bits in range(2, 9):
            codes = torch.arange((1 << bits) - 1, dtype=torch.int16)
            restored = unpack_codes(pack_codes(codes, bits), bits, codes.numel())
            self.assertTrue(torch.equal(restored, codes))

    def test_absolute_and_delta_tensors_decode(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            reference_path = root / "reference.pth"
            trained_path = root / "trained.pth"
            archive_path = root / "weights.mmq"
            decoded_path = root / "decoded.pth"
            reference = {"frozen": torch.tensor([1.0]), "delta": torch.zeros(4)}
            trained = {
                "frozen": reference["frozen"].clone(),
                "delta": torch.tensor([-1.0, -0.25, 0.25, 1.0]),
                "absolute": torch.tensor([[-2.0, 0.0, 2.0]]),
            }
            torch.save(reference, reference_path)
            torch.save(trained, trained_path)

            encode_archive(
                trained_path,
                reference_path,
                ["delta", "absolute"],
                bits=4,
                archive_path=archive_path,
            )
            decode_archive(archive_path, reference_path, decoded_path)
            decoded = torch.load(decoded_path, weights_only=True)
            metadata = read_metadata(archive_path)

            self.assertTrue(torch.equal(decoded["frozen"], reference["frozen"]))
            self.assertEqual([item["baseline"] for item in metadata["tensors"]], ["reference", "zero"])
            for name in ("delta", "absolute"):
                scale = next(item["scale"] for item in metadata["tensors"] if item["name"] == name)
                error = (decoded[name].float() - trained[name]).abs().max().item()
                self.assertLessEqual(error, scale / 2 + 1e-3)

    def test_tied_embedding_is_encoded_once(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            reference_path = root / "reference.pth"
            trained_path = root / "trained.pth"
            archive_path = root / "weights.mmq"
            decoded_path = root / "decoded.pth"
            reference = {
                "model.embed_tokens.weight": torch.zeros(2, 2),
                "lm_head.weight": torch.zeros(2, 2),
            }
            changed = torch.tensor([[0.1, 0.2], [0.3, 0.4]])
            trained = {
                "model.embed_tokens.weight": changed,
                "lm_head.weight": changed.clone(),
            }
            torch.save(reference, reference_path)
            torch.save(trained, trained_path)

            metadata = encode_archive(
                trained_path,
                reference_path,
                ["model.embed_tokens.weight"],
                bits=8,
                archive_path=archive_path,
            )
            decode_archive(archive_path, reference_path, decoded_path)
            decoded = torch.load(decoded_path, weights_only=True)

            self.assertEqual(metadata["parameter_count"], 4)
            self.assertEqual(len(metadata["tensors"]), 1)
            self.assertTrue(torch.equal(decoded["lm_head.weight"], decoded["model.embed_tokens.weight"]))


if __name__ == "__main__":
    unittest.main()
