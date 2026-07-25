import copy

import pytest
import torch
import torch.nn.functional as F
from torch import nn

from experiments.phase4_m4_v1.m4_configs import load_frozen_config
from experiments.phase4_m4_v1.mms2_v2 import (
    decode_mms2_v2,
    encode_mms2_v2,
    quantize_coordinate_blocks,
)
from experiments.phase4_m4_v1.train_m4 import (
    build_coordinate_optimizer,
    cpu_smoke_step,
    frozen_parameter_hash,
    validate_optimizer_parameter_set,
)
from model.hybrid_subspace_lora import (
    COORDINATE_BLOCKS,
    HybridCoordinateStore,
    HybridFactorMapping,
    HybridSubspaceLoRALinear,
    HybridTargetSpec,
    inject_hybrid_subspace_lora,
    iter_hybrid_layers,
    load_m4_coordinate_state,
    m4_coordinate_parameters,
    m4_coordinate_state,
    target_specs_from_registry,
    validate_target_aliases,
)


TOY_DIMENSIONS = {
    "shared_coordinates": 1024,
    "vision_private_coordinates": 436,
    "projector_private_coordinates": 1745,
    "language_private_coordinates": 891,
}
TOY_REGISTRY = {
    "modules": {
        "vision": {
            "rank": 4,
            "targets": [
                {
                    "canonical_name": "vision",
                    "in_features": 1024,
                    "out_features": 1024,
                }
            ],
        },
        "projector": {
            "rank": 32,
            "targets": [
                {
                    "canonical_name": "projector",
                    "in_features": 512,
                    "out_features": 512,
                }
            ],
        },
        "language": {
            "rank": 4,
            "targets": [
                {
                    "canonical_name": "language",
                    "in_features": 2048,
                    "out_features": 2048,
                }
            ],
        },
    }
}


class ToyM4(nn.Module):
    def __init__(self):
        super().__init__()
        self.vision = nn.Linear(1024, 1024, bias=True)
        self.projector = nn.Linear(512, 512, bias=True)
        self.language = nn.Linear(2048, 2048, bias=True)


@pytest.fixture(scope="module")
def hybrid_model():
    torch.manual_seed(7301)
    model = ToyM4()
    inject_hybrid_subspace_lora(
        model, 43101, TOY_REGISTRY, TOY_DIMENSIONS
    )
    return model


def _zero_coordinates(model):
    with torch.no_grad():
        for _, parameter in m4_coordinate_parameters(model):
            parameter.zero_()


def _layer_update(layer, inputs):
    return layer(inputs) - layer.base(inputs)


def test_private_coordinates_only_affect_their_module(hybrid_model):
    model = hybrid_model
    layers = {layer.module_group: layer for layer in iter_hybrid_layers(model)}
    inputs = {
        group: torch.linspace(-0.5, 0.5, layer.spec.in_features).view(1, -1)
        for group, layer in layers.items()
    }
    for selected in ("vision", "projector", "language"):
        _zero_coordinates(model)
        block = f"{selected}_private_coordinates"
        parameter = dict(m4_coordinate_parameters(model))[block]
        with torch.no_grad():
            parameter.copy_(
                torch.linspace(-0.3, 0.3, parameter.numel())
            )
        for group, layer in layers.items():
            update = _layer_update(layer, inputs[group])
            if group == selected:
                assert torch.count_nonzero(update).item() > 0
            else:
                assert torch.equal(update, torch.zeros_like(update))


def test_shared_coordinates_affect_all_three_modules(hybrid_model):
    model = hybrid_model
    _zero_coordinates(model)
    shared = dict(m4_coordinate_parameters(model))["shared_coordinates"]
    with torch.no_grad():
        shared.copy_(torch.linspace(-0.2, 0.2, shared.numel()))
    for layer in iter_hybrid_layers(model):
        inputs = torch.linspace(
            -0.5, 0.5, layer.spec.in_features
        ).view(1, -1)
        assert torch.count_nonzero(_layer_update(layer, inputs)).item() > 0


def test_branch_additivity_has_no_shared_private_cross_term(hybrid_model):
    model = hybrid_model
    for layer in iter_hybrid_layers(model):
        _zero_coordinates(model)
        shared = dict(m4_coordinate_parameters(model))[
            "shared_coordinates"
        ]
        private = dict(m4_coordinate_parameters(model))[
            layer.private_block_id
        ]
        shared_value = torch.linspace(-0.2, 0.25, shared.numel())
        private_value = torch.linspace(-0.15, 0.3, private.numel())
        inputs = torch.linspace(
            -0.4, 0.4, layer.spec.in_features
        ).view(1, -1)
        with torch.no_grad():
            shared.copy_(shared_value)
            private.copy_(private_value)
            combined = _layer_update(layer, inputs)
            private.zero_()
            shared_only = _layer_update(layer, inputs)
            shared.zero_()
            private.copy_(private_value)
            private_only = _layer_update(layer, inputs)
        torch.testing.assert_close(
            combined,
            shared_only + private_only,
            rtol=2e-5,
            atol=2e-5,
        )


def test_rank_fairness_and_outer_scale_applied_once(hybrid_model):
    for layer in iter_hybrid_layers(hybrid_model):
        assert layer.shared_rank + layer.private_rank == layer.old_rank
        assert layer.shared_rank == layer.private_rank
        assert layer.outer_scale == 1.0

    base = nn.Linear(3, 2, bias=False)
    spec = HybridTargetSpec(
        module_group="vision",
        canonical_name="small",
        old_rank=4,
        shared_rank=2,
        private_rank=2,
        in_features=3,
        out_features=2,
        outer_scale=0.25,
    )
    store = HybridCoordinateStore(
        {
            "shared_coordinates": 1,
            "vision_private_coordinates": 1,
            "projector_private_coordinates": 1,
            "language_private_coordinates": 1,
        }
    )
    mappings = {}
    for branch, block in (
        ("shared", "shared_coordinates"),
        ("private", "vision_private_coordinates"),
    ):
        mappings[(branch, "A")] = HybridFactorMapping(
            block, "A", torch.zeros(6, dtype=torch.long), torch.ones(6)
        )
        mappings[(branch, "B")] = HybridFactorMapping(
            block, "B", torch.zeros(4, dtype=torch.long), torch.ones(4)
        )
    layer = HybridSubspaceLoRALinear(
        base, spec, store, mappings, mapping_root=43101
    )
    with torch.no_grad():
        store.shared_coordinates.fill_(0.2)
        store.vision_private_coordinates.fill_(-0.1)
    inputs = torch.tensor([[0.4, -0.3, 0.2]])
    shared_a, shared_b = layer.branch_factors("shared")
    private_a, private_b = layer.branch_factors("private")
    expected_update = 0.25 * (
        F.linear(F.linear(inputs, shared_a), shared_b)
        + F.linear(F.linear(inputs, private_a), private_b)
    )
    torch.testing.assert_close(
        layer(inputs) - base(inputs), expected_update, rtol=0, atol=1e-7
    )


def test_all_zero_coordinates_equal_base_model_exactly(hybrid_model):
    _zero_coordinates(hybrid_model)
    for layer in iter_hybrid_layers(hybrid_model):
        inputs = torch.randn(2, layer.spec.in_features)
        assert torch.equal(layer(inputs), layer.base(inputs))


def test_optimizer_is_exactly_four_coordinates_and_base_hash_is_stable(
    hybrid_model,
):
    model = hybrid_model
    _zero_coordinates(model)
    config, _ = load_frozen_config("M4-shared-1024-root-43101")
    optimizer = build_coordinate_optimizer(model, config["training"])
    receipt = validate_optimizer_parameter_set(model, optimizer)
    assert receipt["coordinate_parameter_count"] == 4
    assert receipt["coordinate_element_count"] == 4096
    before = frozen_parameter_hash(model)
    losses = []
    for layer in iter_hybrid_layers(model):
        inputs = torch.randn(1, layer.spec.in_features)
        losses.append(layer(inputs).float().square().mean())
    step = cpu_smoke_step(model, optimizer, sum(losses))
    assert step["frozen_parameters_unchanged"] is True
    assert frozen_parameter_hash(model) == before
    assert any(
        torch.count_nonzero(value).item()
        for value in m4_coordinate_state(model).values()
    )


def test_in_memory_quantized_and_archive_decoded_logits_match(hybrid_model):
    model = hybrid_model
    config, _ = load_frozen_config("M4-shared-1024-root-43101")
    torch.manual_seed(7302)
    source = {
        name: torch.randn(dimension) * 0.1
        for name, dimension in config["coordinate_dimensions"].items()
    }
    in_memory = quantize_coordinate_blocks(source, config)
    load_m4_coordinate_state(model, in_memory)
    inputs = {
        layer.module_group: torch.randn(2, layer.spec.in_features)
        for layer in iter_hybrid_layers(model)
    }
    reference = {
        layer.module_group: layer(inputs[layer.module_group]).detach().clone()
        for layer in iter_hybrid_layers(model)
    }
    archive, _ = encode_mms2_v2(source, config)
    decoded, _ = decode_mms2_v2(archive)
    load_m4_coordinate_state(model, decoded)
    for layer in iter_hybrid_layers(model):
        logits = layer(inputs[layer.module_group]).detach()
        assert torch.equal(logits, reference[layer.module_group])


class AliasModel(nn.Module):
    pass


def _alias_specs():
    registry = {
        "modules": {
            "vision": {
                "rank": 4,
                "targets": [
                    {
                        "canonical_name": "vision",
                        "in_features": 4,
                        "out_features": 4,
                    }
                ],
            },
            "projector": {
                "rank": 32,
                "targets": [
                    {
                        "canonical_name": "projector",
                        "in_features": 4,
                        "out_features": 4,
                    }
                ],
            },
            "language": {"rank": 4, "targets": []},
        }
    }
    return target_specs_from_registry(registry)


@pytest.mark.parametrize("alias_kind", ["module", "parameter", "storage"])
def test_target_module_parameter_and_storage_aliases_fail(alias_kind):
    model = AliasModel()
    if alias_kind == "module":
        shared = nn.Linear(4, 4, bias=False)
        model.vision = shared
        model.projector = shared
    else:
        model.vision = nn.Linear(4, 4, bias=False)
        model.projector = nn.Linear(4, 4, bias=False)
        if alias_kind == "parameter":
            model.projector.weight = model.vision.weight
        else:
            model.projector.weight = nn.Parameter(model.vision.weight.data)
    with pytest.raises(ValueError, match=f"{alias_kind.title()} alias|{alias_kind} alias"):
        validate_target_aliases(model, _alias_specs())
