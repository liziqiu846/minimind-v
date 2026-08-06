#!/usr/bin/env python3
"""Small actual-MiniMind-V diagnosis-on/off trajectory equivalence audit."""

from __future__ import annotations

import argparse
import gc
import json
from pathlib import Path

import torch
from torch.utils.data import DataLoader
from transformers import AutoTokenizer

from dataset.stage2_dataset import Stage2CaptionDataset, stage2_collate
from experiments.phase3_private_vs_shared_v1.adapter_runtime import build_candidate_model
from experiments.stage2_model import tensor_state_sha256
from experiments.stage2_protocol import Stage2Protocol
from trainer.train_stage2 import learning_rate_at, permutation_for_epoch, seed_everything

from .common import load_protocol, sha256_file, write_json_atomic
from .configs import load_candidate
from .diagnosis import capture_rng, diagnose_replacement, fixed_index, rng_equal
from .train_one import _concat_micro_batches, _ghost_item

STAGE2_PROTOCOL = Path(__file__).resolve().parents[1] / "stage2_protocol_v2.json"


def _run(enabled: bool, audit: dict, device: torch.device, steps: int):
    protocol = load_protocol()
    torch.use_deterministic_algorithms(True)
    config = load_candidate("P-budget-2048-seed-43101")
    stage2 = Stage2Protocol.load(STAGE2_PROTOCOL, require_frozen=True)
    seed_everything(protocol["training"]["data_order_seed"])
    model = build_candidate_model(config, stage2, device=device)
    model.train()
    model.vision_encoder.eval()
    tokenizer = AutoTokenizer.from_pretrained(
        stage2.asset_path("tokenizer"), local_files_only=True
    )
    args = dict(
        tokenizer=tokenizer, model_group="M2", processor=model.processor,
        max_length=protocol["training"]["max_sequence_length"],
        image_token_count=protocol["training"]["image_token_count"],
    )
    dataset = Stage2CaptionDataset(audit["artifacts"]["train"]["path"], **args)
    ghost_pool = Stage2CaptionDataset(audit["artifacts"]["ghost_pool"]["path"], **args)
    permutation = permutation_for_epoch(
        len(dataset), protocol["training"]["data_order_seed"], 0
    )
    loader = iter(DataLoader(
        dataset, batch_size=protocol["training"]["micro_batch_size"],
        sampler=permutation.tolist(), num_workers=0, collate_fn=stage2_collate,
        drop_last=True,
    ))
    parameters = list(model.stage2_coordinates.parameters())
    optimizer = torch.optim.SGD(parameters, lr=protocol["training"]["learning_rate"])
    receipts = []
    for step in range(steps):
        window = [next(loader) for _ in range(
            protocol["training"]["gradient_accumulation_steps"]
        )]
        effective = _concat_micro_batches(window, device)
        lr = learning_rate_at(
            step, protocol["training"]["total_optimizer_steps"],
            protocol["training"]["learning_rate"],
        )
        optimizer.param_groups[0]["lr"] = lr
        if enabled:
            position = fixed_index(config["seed"], step, "batch-position", 16)
            ghost_index = fixed_index(
                config["seed"], step, "ghost", len(ghost_pool)
            )
            diagnose_replacement(
                model, parameters, effective,
                _ghost_item(ghost_pool, ghost_index, device),
                selected_position=position,
                accumulation=protocol["training"]["gradient_accumulation_steps"],
            )
        optimizer.zero_grad(set_to_none=True)
        for start in range(0, 16, 4):
            pixels = effective[2]
            chunk = (
                {key: value[start:start + 4] for key, value in pixels.items()}
                if isinstance(pixels, dict) else pixels[start:start + 4]
            )
            with torch.autocast("cuda", dtype=torch.bfloat16):
                loss = model(
                    input_ids=effective[0][start:start + 4],
                    labels=effective[1][start:start + 4],
                    pixel_values=chunk,
                ).loss
            (loss / 4).backward()
        optimizer.step()
        receipts.append({
            "parameter_sha256": tensor_state_sha256(
                model.stage2_coordinates.state_dict()
            ),
            "optimizer_state": optimizer.state_dict(),
            "learning_rate": lr,
            "rng": capture_rng(),
        })
    final = {
        "parameter_sha256": tensor_state_sha256(model.stage2_coordinates.state_dict()),
        "optimizer_state": optimizer.state_dict(),
        "learning_rate": optimizer.param_groups[0]["lr"],
        "rng": capture_rng(),
    }
    del model, dataset, ghost_pool
    gc.collect()
    torch.cuda.empty_cache()
    return receipts, final


def audit(data_audit_path: Path, output_path: Path, device_name: str, steps: int) -> dict:
    data_audit = json.loads(data_audit_path.read_text())
    if data_audit["status"] != "PASS":
        raise RuntimeError("trajectory audit requires PASS data audit")
    device = torch.device(device_name)
    disabled_steps, disabled_final = _run(False, data_audit, device, steps)
    enabled_steps, enabled_final = _run(True, data_audit, device, steps)
    step_checks = []
    for index, (off, on) in enumerate(zip(disabled_steps, enabled_steps)):
        step_checks.append({
            "step": index,
            "parameters_exact": off["parameter_sha256"] == on["parameter_sha256"],
            "sgd_state_exact": off["optimizer_state"] == on["optimizer_state"],
            "learning_rate_exact": off["learning_rate"] == on["learning_rate"],
            "rng_state_exact": rng_equal(off["rng"], on["rng"]),
        })
    final_checks = {
        "checkpoint_exact": (
            disabled_final["parameter_sha256"] == enabled_final["parameter_sha256"]
            and disabled_final["optimizer_state"] == enabled_final["optimizer_state"]
            and disabled_final["learning_rate"] == enabled_final["learning_rate"]
        ),
        "rng_state_exact": rng_equal(disabled_final["rng"], enabled_final["rng"]),
    }
    passed = all(all(
        row[key] for key in (
            "parameters_exact", "sgd_state_exact", "learning_rate_exact", "rng_state_exact"
        )
    ) for row in step_checks) and all(final_checks.values())
    result = {
        "schema_version": 1,
        "status": "PASS" if passed else "FAIL",
        "implementation": "actual_MiniMind_V_P_budget_2048_seed_43101",
        "tested_optimizer_steps": steps,
        "diagnosis_disabled_vs_enabled_steps": step_checks,
        "final": final_checks,
        "data_audit_sha256": sha256_file(data_audit_path),
    }
    write_json_atomic(output_path, result)
    if not passed:
        raise RuntimeError("trajectory consistency audit failed")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-audit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--steps", type=int, default=2, choices=(1, 2))
    args = parser.parse_args()
    print(json.dumps(audit(
        args.data_audit, args.output, args.device, args.steps
    ), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
