"""Verified in-memory projected visual-feature cache."""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Iterable, Mapping

import torch
from PIL import Image, ImageOps
from torch import nn

from experiments.phase3_v6.scoring.common import (
    canonical_json_bytes,
    sha256_bytes,
    utf8_key,
)


FEATURE_FORMAT_VERSION = "phase3-v6-projected-vision-f32-cpu-v1"


class _InjectedVisionEncoder(nn.Module):
    def __init__(self, base: nn.Module, owner: "ProjectedFeatureCache") -> None:
        super().__init__()
        self.base = base
        self.owner = owner

    def forward(self, **_: Any) -> Any:
        keys = self.owner.active_keys
        if keys is None:
            raise RuntimeError("projected-feature cache has no active image keys")
        batch = len(keys)
        placeholder = torch.empty(
            (
                batch,
                self.owner.image_token_count,
                self.owner.image_hidden_size,
            ),
            dtype=torch.float32,
            device=self.owner.device,
        )
        return SimpleNamespace(last_hidden_state=placeholder)


class _InjectedVisionProjector(nn.Module):
    def __init__(self, base: nn.Module, owner: "ProjectedFeatureCache") -> None:
        super().__init__()
        self.base = base
        self.owner = owner

    def forward(self, _: torch.Tensor) -> torch.Tensor:
        keys = self.owner.active_keys
        if keys is None:
            raise RuntimeError("projected-feature cache has no active image keys")
        missing = [key for key in keys if key not in self.owner.features]
        if missing:
            raise KeyError(f"projected-feature cache miss: {missing[:3]}")
        self.owner.hit_count += len(keys)
        return torch.stack(
            [
                self.owner.features[key].to(
                    device=self.owner.device,
                    dtype=torch.float32,
                    non_blocking=False,
                )
                for key in keys
            ],
            dim=0,
        )


class ProjectedFeatureCache:
    """Cache post-projector features once per image and frozen model."""

    def __init__(
        self,
        model,
        *,
        model_id: str,
        checkpoint_sha256: str,
        image_entries: Mapping[str, Mapping[str, Any]],
        device: str,
    ) -> None:
        if not hasattr(model, "vision_encoder") or not hasattr(
            model, "vision_proj"
        ):
            raise TypeError("projected-feature cache requires a visual model")
        self.model = model
        self.model_id = model_id
        self.checkpoint_sha256 = checkpoint_sha256
        self.image_entries = {
            str(key): dict(value) for key, value in image_entries.items()
        }
        self.device = device
        self.base_encoder = model.vision_encoder
        self.base_projector = model.vision_proj
        self.processor = model.processor
        self.image_token_count = int(model.config.image_token_len)
        self.image_hidden_size = int(model.config.image_hidden_size)
        processor_config = self.processor.to_dict()
        self.processor_config_sha256 = sha256_bytes(
            canonical_json_bytes(processor_config)
        )
        self.features: dict[str, torch.Tensor] = {}
        self.feature_sha256: dict[str, str] = {}
        self.cache_keys: dict[str, str] = {}
        self.encoder_forward_call_count = 0
        self.encoded_image_count = 0
        self.hit_count = 0
        self.active_keys: list[str] | None = None
        self.installed = False

    def _key_payload(self, filename: str) -> dict[str, Any]:
        image = self.image_entries[filename]
        return {
            "feature_format_version": FEATURE_FORMAT_VERSION,
            "model_id": self.model_id,
            "model_checkpoint_sha256": self.checkpoint_sha256,
            "filename": filename,
            "image_sha256": image["image_sha256"],
            "normalized_pixel_sha256": image["normalized_pixel_sha256"],
            "image_processor_config_sha256": self.processor_config_sha256,
            "dtype": "float32",
            "storage_device": "cpu",
            "extraction_device": self.device.split(":")[0],
            "image_token_count": self.image_token_count,
            "image_hidden_size": self.image_hidden_size,
        }

    def _cache_key(self, filename: str) -> str:
        return sha256_bytes(canonical_json_bytes(self._key_payload(filename)))

    @staticmethod
    def _load_image(path: str | Path) -> Image.Image:
        with Image.open(path) as opened:
            opened.load()
            return ImageOps.exif_transpose(opened).convert("RGB")

    def precompute(
        self,
        filenames: Iterable[str],
        *,
        batch_size: int,
    ) -> None:
        if self.installed:
            raise RuntimeError("cannot precompute after cache injection")
        names = sorted(set(filenames), key=utf8_key)
        if batch_size < 1:
            raise ValueError("vision cache batch size must be positive")
        self.base_encoder.eval()
        self.base_projector.eval()
        for offset in range(0, len(names), batch_size):
            batch_names = names[offset : offset + batch_size]
            images = [
                self._load_image(self.image_entries[name]["image_path"])
                for name in batch_names
            ]
            processed = self.processor(images=images, return_tensors="pt")
            processed = {
                key: value.to(
                    device=self.device,
                    dtype=torch.float32,
                    non_blocking=False,
                )
                for key, value in processed.items()
            }
            with torch.inference_mode():
                encoded = self.base_encoder(**processed).last_hidden_state
                projected = self.base_projector(encoded)
            self.encoder_forward_call_count += 1
            if projected.shape[0] != len(batch_names):
                raise RuntimeError("vision cache batch dimension mismatch")
            if projected.shape[1] != self.image_token_count:
                raise RuntimeError("vision cache image-token dimension mismatch")
            if not torch.isfinite(projected).all():
                raise FloatingPointError("vision cache contains non-finite values")
            for index, name in enumerate(batch_names):
                feature = projected[index].detach().to(
                    device="cpu", dtype=torch.float32
                ).contiguous()
                raw = feature.view(torch.uint8).numpy().tobytes()
                self.features[name] = feature
                self.feature_sha256[name] = sha256_bytes(raw)
                self.cache_keys[name] = self._cache_key(name)
                self.encoded_image_count += 1
        if len(self.features) != len(names):
            raise RuntimeError("vision cache did not populate every requested image")

    def install(self) -> None:
        if self.installed:
            raise RuntimeError("projected-feature cache is already installed")
        if not self.features:
            raise RuntimeError("cannot install an empty projected-feature cache")
        self.model.vision_encoder = _InjectedVisionEncoder(
            self.base_encoder, self
        )
        self.model.vision_proj = _InjectedVisionProjector(
            self.base_projector, self
        )
        self.installed = True

    @contextmanager
    def activate(self, filenames: list[str]):
        if not self.installed:
            raise RuntimeError("projected-feature cache is not installed")
        if self.active_keys is not None:
            raise RuntimeError("nested projected-feature cache activation")
        if any(name not in self.features for name in filenames):
            raise KeyError("activation includes an uncached image")
        self.active_keys = list(filenames)
        try:
            yield
        finally:
            self.active_keys = None

    def dummy_pixel_values(self, batch_size: int) -> dict[str, torch.Tensor]:
        return {
            "pixel_values": torch.empty(
                (batch_size, 3, 1, 1),
                dtype=torch.float32,
                device=self.device,
            )
        }

    def actual_pixel_values(
        self, filename: str, *, batch_size: int = 1
    ) -> dict[str, torch.Tensor]:
        if batch_size < 1:
            raise ValueError("actual pixel batch size must be positive")
        image = self._load_image(self.image_entries[filename]["image_path"])
        processed = self.processor(images=[image], return_tensors="pt")
        return {
            key: value.repeat(
                batch_size, *([1] * (value.ndim - 1))
            ).to(
                device=self.device, dtype=torch.float32, non_blocking=False
            )
            for key, value in processed.items()
        }

    def receipt(self) -> dict[str, Any]:
        total_bytes = sum(
            feature.numel() * feature.element_size()
            for feature in self.features.values()
        )
        return {
            "cache_mode": "model_local_cpu_memory_projected_features",
            "feature_format_version": FEATURE_FORMAT_VERSION,
            "model_id": self.model_id,
            "checkpoint_sha256": self.checkpoint_sha256,
            "processor_config_sha256": self.processor_config_sha256,
            "unique_cached_image_count": len(self.features),
            "encoded_image_count": self.encoded_image_count,
            "encoder_forward_call_count": self.encoder_forward_call_count,
            "hit_count": self.hit_count,
            "feature_total_bytes": total_bytes,
            "feature_shapes": [
                list(shape)
                for shape in sorted(
                    {tuple(value.shape) for value in self.features.values()}
                )
            ],
            "feature_dtype": "float32",
            "feature_storage_device": "cpu",
            "cache_key_sha256": sha256_bytes(
                canonical_json_bytes(
                    {
                        key: self.cache_keys[key]
                        for key in sorted(self.cache_keys, key=utf8_key)
                    }
                )
            ),
            "feature_content_sha256": sha256_bytes(
                canonical_json_bytes(
                    {
                        key: self.feature_sha256[key]
                        for key in sorted(self.feature_sha256, key=utf8_key)
                    }
                )
            ),
        }
