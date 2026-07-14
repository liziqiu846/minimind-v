"""A reproducible low-dimensional subspace for the VLM projector."""

import hashlib
import math

import torch
import torch.nn.functional as F
from torch import nn


def fixed_state_sha256(module: nn.Module) -> str:
    """Hash every fixed buffer needed to reconstruct a subspace module."""
    digest = hashlib.sha256()
    for name, tensor in sorted(module.named_buffers()):
        value = tensor.detach().cpu().contiguous()
        digest.update(name.encode())
        digest.update(str(value.dtype).encode())
        digest.update(str(tuple(value.shape)).encode())
        digest.update(value.view(torch.uint8).numpy().tobytes())
    return digest.hexdigest()


class HashedSubspaceLinear(nn.Module):
    """A fixed linear layer whose weight update is controlled by few coordinates."""

    def __init__(self, in_features, out_features, subspace_dim, seed) -> None:
        super().__init__()
        generator = torch.Generator().manual_seed(seed)
        base_weight = torch.empty(out_features, in_features)
        nn.init.kaiming_uniform_(base_weight, a=math.sqrt(5), generator=generator)
        bound = 1.0 / math.sqrt(in_features)
        base_bias = torch.empty(out_features).uniform_(-bound, bound, generator=generator)

        shape = (out_features, in_features)
        coordinate_index = torch.randint(subspace_dim, shape, generator=generator)
        signs = 2 * torch.randint(2, shape, generator=generator) - 1
        counts = torch.bincount(
            coordinate_index.flatten(), minlength=subspace_dim
        )
        if torch.any(counts == 0):
            raise RuntimeError("subspace mapping contains an unused coordinate")
        coordinate_scale = signs / counts[coordinate_index].sqrt()

        self.coordinates = nn.Parameter(torch.zeros(subspace_dim))
        self.register_buffer("base_weight", base_weight, persistent=False)
        self.register_buffer("base_bias", base_bias, persistent=False)
        self.register_buffer("coordinate_index", coordinate_index, persistent=False)
        self.register_buffer("coordinate_scale", coordinate_scale.float(), persistent=False)

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        delta = self.coordinates[self.coordinate_index] * self.coordinate_scale
        return F.linear(inputs, self.base_weight + delta, self.base_bias)


class LowDimensionalProjector(nn.Module):
    """The MiniMind-V projector with a block-diagonal random subspace update."""

    def __init__(
        self,
        in_dim: int,
        out_dim: int,
        subspace_dim: int = 1024,
        seed: int = 42,
        train_norm: bool = False,
    ) -> None:
        super().__init__()
        if subspace_dim < 2:
            raise ValueError("subspace_dim must be at least two")

        first_dim = subspace_dim // 2
        self.subspace_dim = subspace_dim
        self.seed = seed
        self.train_norm = train_norm
        self.normalization = nn.LayerNorm(in_dim, elementwise_affine=False)
        if train_norm:
            self.normalization_scale = nn.Parameter(torch.zeros(in_dim))
            self.normalization_bias = nn.Parameter(torch.zeros(in_dim))
        self.input_projection = HashedSubspaceLinear(in_dim, out_dim, first_dim, seed)
        self.activation = nn.GELU()
        self.output_projection = HashedSubspaceLinear(
            out_dim, out_dim, subspace_dim - first_dim, seed + 1
        )

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        normalized = self.normalization(inputs)
        if self.train_norm:
            normalized = normalized * (1.0 + self.normalization_scale)
            normalized = normalized + self.normalization_bias
        hidden = self.input_projection(normalized)
        return self.output_projection(self.activation(hidden))
