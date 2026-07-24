from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import torch
from PIL import Image
from torch import nn

from experiments.phase3_v6.scoring.common import sha256_file
from experiments.phase3_v6.scoring.image_feature_cache import (
    ProjectedFeatureCache,
)
from experiments.phase3_v6.scoring.run_scoring import (
    _load_valid_shard,
    _write_shard,
)


class Processor:
    def to_dict(self):
        return {"name": "synthetic", "size": 2}

    def __call__(self, *, images, return_tensors):
        assert return_tensors == "pt"
        values = []
        for image in images:
            values.append(
                torch.tensor(list(image.getdata()), dtype=torch.float32)
                .reshape(2, 2, 3)
                .permute(2, 0, 1)
            )
        return {"pixel_values": torch.stack(values)}


class Encoder(nn.Module):
    def forward(self, pixel_values):
        means = pixel_values.mean(dim=(1, 2, 3))
        hidden = means[:, None, None].repeat(1, 2, 3)
        return SimpleNamespace(last_hidden_state=hidden)


class Projector(nn.Module):
    def __init__(self):
        super().__init__()
        self.linear = nn.Linear(3, 4, bias=False)
        with torch.no_grad():
            self.linear.weight.copy_(
                torch.tensor(
                    [
                        [1.0, 0.0, 0.0],
                        [0.0, 1.0, 0.0],
                        [0.0, 0.0, 1.0],
                        [1.0, 1.0, 1.0],
                    ]
                )
            )

    def forward(self, value):
        return self.linear(value)


class Model(nn.Module):
    def __init__(self):
        super().__init__()
        self.vision_encoder = Encoder()
        self.vision_proj = Projector()
        self.processor = Processor()
        self.config = SimpleNamespace(image_token_len=2, image_hidden_size=3)


def test_cache_hit_reuses_exact_projected_feature(tmp_path):
    image_path = tmp_path / "image.jpg"
    Image.new("RGB", (2, 2), color=(2, 4, 6)).save(image_path)
    entries = {
        "image.jpg": {
            "image_path": str(image_path),
            "image_sha256": sha256_file(image_path),
            "normalized_pixel_sha256": "a" * 64,
            "image_size_bytes": image_path.stat().st_size,
        }
    }
    model = Model()
    cache = ProjectedFeatureCache(
        model,
        model_id="synthetic",
        checkpoint_sha256="b" * 64,
        image_entries=entries,
        device="cpu",
    )
    pixels = cache.actual_pixel_values("image.jpg")
    direct = model.vision_proj(
        model.vision_encoder(**pixels).last_hidden_state
    )
    cache.precompute(["image.jpg"], batch_size=1)
    assert torch.equal(direct[0], cache.features["image.jpg"])
    cache.install()
    with cache.activate(["image.jpg"]):
        encoded = model.vision_encoder(
            **cache.dummy_pixel_values(1)
        ).last_hidden_state
        cached = model.vision_proj(encoded)
    assert torch.equal(direct, cached)
    assert cache.receipt()["encoded_image_count"] == 1
    assert cache.receipt()["hit_count"] == 1


def test_interrupted_shard_resume_requires_all_hashes(tmp_path):
    data = tmp_path / "part.jsonl"
    manifest = tmp_path / "part.manifest.json"
    rows = [{"sample_id": "a", "value": 1.0}]
    _write_shard(
        data,
        manifest,
        rows,
        protocol_sha="p" * 64,
        checkpoint_sha="c" * 64,
    )
    loaded = _load_valid_shard(
        data,
        manifest,
        protocol_sha="p" * 64,
        checkpoint_sha="c" * 64,
        expected_sample_ids=["a"],
    )
    assert loaded == rows
    assert (
        _load_valid_shard(
            data,
            manifest,
            protocol_sha="x" * 64,
            checkpoint_sha="c" * 64,
            expected_sample_ids=["a"],
        )
        is None
    )

