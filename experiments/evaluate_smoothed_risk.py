#!/usr/bin/env python3
"""Evaluate smoothed conditional token NLL, averaging samples equally."""

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path
from statistics import NormalDist

import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset, Subset
from tqdm import tqdm

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from dataset.lm_dataset import VLMDataset
from model.model_vlm import VLMConfig
from model.subspace_projector import fixed_state_sha256
from experiments.phase2_protocol import FrozenProtocol, validate_split_artifact
from experiments.quantize_subspace import state_dict_sha256_v1
from trainer.trainer_utils import init_vlm_model, vlm_collate_fn


DEFAULT_ALPHA_GRID = (0.0001, 0.001, 0.005, 0.01, 0.05, 0.1, 0.25, 0.5)
PAIRED_SHUFFLE_PROTOCOL = "sha256_rank_pair_swap_v1"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def model_asset_fingerprints(tokenizer_path: Path, vision_model_path: Path) -> dict:
    """Identify the fixed tokenizer, processor, and vision encoder used for risk."""
    tokenizer_path = tokenizer_path.resolve()
    vision_model_path = vision_model_path.resolve()
    return {
        "tokenizer": {
            "path": str(tokenizer_path),
            "files": {
                name: sha256_file(tokenizer_path / name)
                for name in ("tokenizer.json", "tokenizer_config.json")
            },
        },
        "vision_model": {
            "path": str(vision_model_path),
            "files": {
                name: sha256_file(vision_model_path / name)
                for name in (
                    "config.json",
                    "model.safetensors",
                    "preprocessor_config.json",
                )
            },
        },
    }


def apply_image_condition(pixel_values, condition: str):
    """Keep or remove images; mismatching is now done at dataset level."""
    if condition == "correct":
        return pixel_values
    if condition == "none":
        return None
    raise ValueError(f"unsupported image condition: {condition}")


def paired_derangement(size: int, seed: int) -> tuple[int, ...]:
    """Pair SHA-256-ranked samples and swap each pair, independent of batches."""
    if size < 4 or size % 2:
        raise ValueError("paired_shuffled evaluation needs an even sample count >= 4")
    prefix = f"{PAIRED_SHUFFLE_PROTOCOL}\0{seed}\0".encode()
    order = sorted(
        range(size),
        key=lambda index: (hashlib.sha256(prefix + str(index).encode()).digest(), index),
    )
    permutation = list(range(size))
    for left, right in zip(order[::2], order[1::2], strict=True):
        permutation[left], permutation[right] = right, left
    return tuple(permutation)


def permutation_sha256(permutation: tuple[int, ...]) -> str:
    digest = hashlib.sha256()
    for index in permutation:
        digest.update(index.to_bytes(8, "little", signed=False))
    return digest.hexdigest()


class PairedImageDataset(Dataset):
    """Return each text with both its correct image and its fixed donor image."""

    def __init__(self, dataset: Dataset, permutation: tuple[int, ...]):
        self.dataset = dataset
        self.permutation = permutation

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, index):
        input_ids, labels, correct_pixels = self.dataset[index]
        _, _, donor_pixels = self.dataset[self.permutation[index]]
        return input_ids, labels, correct_pixels, donor_pixels


def paired_vlm_collate_fn(batch):
    input_ids, labels, correct_pixels = vlm_collate_fn(
        [(item[0], item[1], item[2]) for item in batch]
    )
    _, _, donor_pixels = vlm_collate_fn(
        [(item[0], item[1], item[3]) for item in batch]
    )
    return input_ids, labels, correct_pixels, donor_pixels


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-path", type=Path, required=True)
    parser.add_argument("--data-role", choices=("train", "validation"))
    parser.add_argument("--split-manifest", type=Path)
    parser.add_argument("--protocol-path", type=Path)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--model-kind",
        choices=("diagnostic_unquantized", "decoded_quantized"),
        required=True,
    )
    parser.add_argument("--alphas", nargs="+", type=float, default=DEFAULT_ALPHA_GRID)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--num-workers", type=int, default=2)
    parser.add_argument("--max-samples", type=int, default=0)
    parser.add_argument(
        "--image-condition",
        choices=("correct", "paired_shuffled", "none"),
        default="correct",
    )
    parser.add_argument("--paired-shuffle-seed", type=int, default=20260714)
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument(
        "--dtype", choices=("bfloat16", "float16", "float32"), default="bfloat16"
    )
    parser.add_argument("--tokenizer-path", type=Path, default=REPO_ROOT / "model")
    parser.add_argument(
        "--vision-model-path",
        type=Path,
        default=REPO_ROOT / "model/siglip2-base-p32-256-ve",
    )
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def resolve_run(args: argparse.Namespace) -> tuple[dict, Path]:
    manifest = json.loads((args.run_dir / "manifest.json").read_text())
    run_id = manifest["run_id"]
    hidden_size = manifest["model"]["hidden_size"]
    checkpoint = args.checkpoint or (
        args.run_dir / "weights" / f"{run_id}_{hidden_size}.pth"
    )
    if args.model_kind == "decoded_quantized" and args.checkpoint is None:
        raise ValueError("decoded_quantized evaluation requires --checkpoint")
    return manifest, checkpoint


def load_model(args: argparse.Namespace, manifest: dict, checkpoint: Path):
    projector = manifest["model"].get("projector", {"type": "standard"})
    config = VLMConfig(
        hidden_size=manifest["model"]["hidden_size"],
        num_hidden_layers=manifest["model"]["num_hidden_layers"],
        max_seq_len=manifest["training"]["max_seq_len"],
        projector_type=projector["type"],
        subspace_dim=projector.get("subspace_dim", 1024),
        subspace_seed=projector.get("subspace_seed", 42),
        subspace_train_norm=projector.get("train_norm", False),
    )
    model, tokenizer, processor = init_vlm_model(
        config,
        from_weight="none",
        tokenizer_path=str(args.tokenizer_path),
        vision_model_path=str(args.vision_model_path),
        device=args.device,
        freeze_llm=2,
    )
    if projector["type"] == "subspace":
        actual_hash = fixed_state_sha256(model.vision_proj)
        if actual_hash != projector["fixed_state_sha256"]:
            raise ValueError("subspace projector does not match the recorded fixed state")
    state_dict = torch.load(checkpoint, map_location="cpu", weights_only=True)
    checkpoint_state_sha256 = state_dict_sha256_v1(state_dict)
    incompatible = model.load_state_dict(state_dict, strict=False)
    bad_missing = [
        key for key in incompatible.missing_keys if not key.startswith("vision_encoder.")
    ]
    if bad_missing or incompatible.unexpected_keys:
        raise ValueError("checkpoint does not match the recorded model architecture")
    model.eval()
    return model, tokenizer, processor, config, checkpoint_state_sha256


def validate_evaluation_protocol(protocol: FrozenProtocol, args, manifest: dict) -> dict:
    if not args.split_manifest or not args.data_role:
        raise ValueError("Phase 2 evaluation requires --split-manifest and --data-role")
    protocol.verify_files(REPO_ROOT, "implementation_files")
    protocol.verify_environment(REPO_ROOT)
    protocol.verify_files(REPO_ROOT, "assets")
    protocol.verify_asset("tokenizer_json", args.tokenizer_path / "tokenizer.json")
    protocol.verify_asset(
        "tokenizer_config", args.tokenizer_path / "tokenizer_config.json"
    )
    protocol.verify_asset("vision_config", args.vision_model_path / "config.json")
    protocol.verify_asset(
        "vision_weights", args.vision_model_path / "model.safetensors"
    )
    protocol.verify_asset(
        "vision_processor", args.vision_model_path / "preprocessor_config.json"
    )
    if manifest.get("protocol_sha256") != protocol.sha256:
        raise ValueError("run manifest does not reference this frozen protocol")
    protocol.require(
        "evaluation",
        {
            "batch_size": args.batch_size,
            "num_workers": args.num_workers,
            "max_samples": args.max_samples,
            "dtype": args.dtype,
        },
        ("batch_size", "num_workers", "max_samples", "dtype"),
    )
    if args.data_role == "train":
        expected_alphas = [protocol.payload["certificate"]["alpha"]]
        allowed_conditions = {"correct"}
    else:
        expected_alphas = protocol.payload["diagnostics"]["alpha_grid"]
        allowed_conditions = set(protocol.payload["diagnostics"]["image_conditions"])
    if list(args.alphas) != expected_alphas or args.image_condition not in allowed_conditions:
        raise ValueError("alphas or image condition do not match the frozen protocol")
    if (
        args.image_condition == "paired_shuffled"
        and args.paired_shuffle_seed
        != protocol.payload["diagnostics"]["paired_shuffle_seed"]
    ):
        raise ValueError("paired shuffle seed does not match the frozen protocol")
    return validate_split_artifact(
        args.split_manifest, args.data_path, args.data_role, protocol
    )


def build_loader(args, tokenizer, processor, config):
    dataset = VLMDataset(
        str(args.data_path),
        tokenizer,
        preprocess=processor,
        max_length=config.max_seq_len,
        image_special_token=config.image_special_token,
        image_token_len=config.image_token_len,
        augment=False,
    )
    if args.max_samples:
        dataset = Subset(dataset, range(min(args.max_samples, len(dataset))))
    permutation = None
    collate_fn = vlm_collate_fn
    if args.image_condition == "paired_shuffled":
        permutation = paired_derangement(len(dataset), args.paired_shuffle_seed)
        dataset = PairedImageDataset(dataset, permutation)
        collate_fn = paired_vlm_collate_fn
    loader = DataLoader(
        dataset,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.num_workers,
        pin_memory=args.device.startswith("cuda"),
        collate_fn=collate_fn,
    )
    return loader, permutation


def smoothed_risk_grid_bits(logits, labels, alphas, ignore_index=-100):
    logits = logits[:, :-1].float()
    labels = labels[:, 1:]
    mask = labels.ne(ignore_index)
    counts = mask.sum(dim=1)
    if torch.any(counts == 0):
        raise ValueError("every sample needs at least one target token")
    safe_labels = labels.masked_fill(~mask, 0)
    target_log_p = F.log_softmax(logits, dim=-1).gather(
        -1, safe_labels.unsqueeze(-1)
    ).squeeze(-1)
    alpha = torch.as_tensor(alphas, device=logits.device, dtype=target_log_p.dtype)
    smoothed_log_p = torch.logaddexp(
        target_log_p.unsqueeze(0) + torch.log1p(-alpha)[:, None, None],
        (torch.log(alpha) - math.log(logits.shape[-1]))[:, None, None],
    )
    token_bits = (-smoothed_log_p / math.log(2)).masked_fill(~mask.unsqueeze(0), 0)
    risks = token_bits.sum(dim=2) / counts.unsqueeze(0)
    return risks.detach(), counts.detach()


def smoothed_autoregressive_risk_bits(logits, labels, alpha, ignore_index=-100):
    risks, counts = smoothed_risk_grid_bits(logits, labels, [alpha], ignore_index)
    return risks[0], counts


def paired_difference_summary(differences, permutation, confidence=0.95):
    """Summarize mismatch-minus-correct effects over independent sample pairs."""
    left = [index for index, donor in enumerate(permutation) if index < donor]
    right = [permutation[index] for index in left]
    pair_effects = (differences[:, left] + differences[:, right]) / 2
    means = pair_effects.mean(dim=1)
    standard_errors = pair_effects.std(dim=1, unbiased=True) / math.sqrt(len(left))
    z_value = NormalDist().inv_cdf((1.0 + confidence) / 2.0)
    return means, standard_errors, z_value


def move_pixels(pixel_values, device):
    if isinstance(pixel_values, dict):
        return {key: value.to(device) for key, value in pixel_values.items()}
    return pixel_values.to(device)


@torch.inference_mode()
def evaluate(model, loader, args):
    sums = torch.zeros(len(args.alphas), dtype=torch.float64)
    sample_count = target_token_count = vocab_size = 0
    amp_dtype = {"bfloat16": torch.bfloat16, "float16": torch.float16}.get(
        args.dtype, torch.float32
    )
    use_amp = args.device.startswith("cuda") and args.dtype != "float32"

    for input_ids, labels, pixels in tqdm(loader, desc="Evaluating"):
        input_ids = input_ids.to(args.device)
        labels = labels.to(args.device)
        pixels = apply_image_condition(pixels, args.image_condition)
        if pixels is not None:
            pixels = move_pixels(pixels, args.device)
        with torch.autocast("cuda", dtype=amp_dtype, enabled=use_amp):
            logits = model(input_ids=input_ids, pixel_values=pixels).logits
        risks, counts = smoothed_risk_grid_bits(logits, labels, args.alphas)
        sums += risks.double().sum(dim=1).cpu()
        sample_count += risks.shape[1]
        target_token_count += counts.sum().item()
        vocab_size = logits.shape[-1]

    return {
        "sample_count": sample_count,
        "target_token_count": target_token_count,
        "mean_target_tokens_per_sample": target_token_count / sample_count,
        "vocab_size": vocab_size,
        "aggregation": "mean_tokens_within_sample_then_mean_samples",
        "risks": [
            {"alpha": alpha, "mean_sample_risk_bits": total / sample_count}
            for alpha, total in zip(args.alphas, sums.tolist(), strict=True)
        ],
    }


@torch.inference_mode()
def evaluate_paired(model, loader, args, permutation):
    correct_sums = torch.zeros(len(args.alphas), dtype=torch.float64)
    shuffled_sums = torch.zeros(len(args.alphas), dtype=torch.float64)
    difference_batches = []
    sample_count = target_token_count = vocab_size = 0
    amp_dtype = {"bfloat16": torch.bfloat16, "float16": torch.float16}.get(
        args.dtype, torch.float32
    )
    use_amp = args.device.startswith("cuda") and args.dtype != "float32"

    for input_ids, labels, correct_pixels, donor_pixels in tqdm(
        loader, desc="Evaluating paired images"
    ):
        input_ids = input_ids.to(args.device)
        labels = labels.to(args.device)
        correct_pixels = move_pixels(correct_pixels, args.device)
        donor_pixels = move_pixels(donor_pixels, args.device)
        with torch.autocast("cuda", dtype=amp_dtype, enabled=use_amp):
            correct_logits = model(
                input_ids=input_ids, pixel_values=correct_pixels
            ).logits
            shuffled_logits = model(
                input_ids=input_ids, pixel_values=donor_pixels
            ).logits
        correct, counts = smoothed_risk_grid_bits(
            correct_logits, labels, args.alphas
        )
        shuffled, _ = smoothed_risk_grid_bits(shuffled_logits, labels, args.alphas)
        correct_sums += correct.double().sum(dim=1).cpu()
        shuffled_sums += shuffled.double().sum(dim=1).cpu()
        difference_batches.append((shuffled - correct).double().cpu())
        sample_count += correct.shape[1]
        target_token_count += counts.sum().item()
        vocab_size = correct_logits.shape[-1]

    differences = torch.cat(difference_batches, dim=1)
    means, standard_errors, z_value = paired_difference_summary(
        differences, permutation
    )
    rows = []
    for index, alpha in enumerate(args.alphas):
        mean = means[index].item()
        standard_error = standard_errors[index].item()
        rows.append(
            {
                "alpha": alpha,
                "correct_mean_sample_risk_bits": correct_sums[index].item()
                / sample_count,
                "shuffled_mean_sample_risk_bits": shuffled_sums[index].item()
                / sample_count,
                "mean_difference_bits": mean,
                "standard_error_bits": standard_error,
                "ci95_lower_bits": mean - z_value * standard_error,
                "ci95_upper_bits": mean + z_value * standard_error,
            }
        )
    return {
        "sample_count": sample_count,
        "pair_count": sample_count // 2,
        "target_token_count": target_token_count,
        "mean_target_tokens_per_sample": target_token_count / sample_count,
        "vocab_size": vocab_size,
        "aggregation": "mean_tokens_within_sample_then_disjoint_pair_effects",
        "paired_diagnostic": rows,
    }


def main():
    args = parse_args()
    if args.output.exists() and not args.overwrite:
        raise FileExistsError(f"output already exists: {args.output}")
    manifest, checkpoint = resolve_run(args)
    checkpoint_sha256 = sha256_file(checkpoint)
    data_sha256 = sha256_file(args.data_path)
    protocol = FrozenProtocol.load(args.protocol_path) if args.protocol_path else None
    if protocol and args.overwrite:
        raise ValueError("frozen Phase 2 outputs cannot be overwritten")
    split_metadata = (
        validate_evaluation_protocol(protocol, args, manifest) if protocol else None
    )
    model, tokenizer, processor, config, checkpoint_state_sha256 = load_model(
        args, manifest, checkpoint
    )
    loader, permutation = build_loader(args, tokenizer, processor, config)
    summary = (
        evaluate_paired(model, loader, args, permutation)
        if permutation is not None
        else evaluate(model, loader, args)
    )
    result = {
        "run_id": manifest["run_id"],
        "model_kind": args.model_kind,
        "checkpoint": str(checkpoint.resolve()),
        "checkpoint_sha256": checkpoint_sha256,
        "checkpoint_state_sha256": checkpoint_state_sha256,
        "data_path": str(args.data_path.resolve()),
        "data_sha256": data_sha256,
        "image_condition": args.image_condition,
        "evaluation": {
            "batch_size": args.batch_size,
            "num_workers": args.num_workers,
            "max_samples": args.max_samples,
            "device": args.device,
            "dtype": args.dtype,
        },
        "runtime": {
            "python": sys.version.split()[0],
            "torch": torch.__version__,
            "cuda_runtime": torch.version.cuda,
            "device_name": (
                torch.cuda.get_device_name(args.device)
                if args.device.startswith("cuda")
                else None
            ),
        },
        "model_assets": model_asset_fingerprints(
            args.tokenizer_path, args.vision_model_path
        ),
        "alpha_grid": list(args.alphas),
        "alpha_choice_bits": (
            protocol.payload["certificate"]["alpha_selection_bits"]
            if protocol
            else math.ceil(math.log2(len(args.alphas)))
        ),
        **summary,
    }
    if protocol:
        result["protocol"] = protocol.reference()
        result["dataset_split"] = split_metadata
    if permutation is not None:
        result["paired_shuffle"] = {
            "protocol": PAIRED_SHUFFLE_PROTOCOL,
            "seed": args.paired_shuffle_seed,
            "permutation_sha256": permutation_sha256(permutation),
            "confidence_interval": "normal_approximation_over_disjoint_pair_effects",
            "coverage": "pointwise_95_percent_per_predeclared_alpha",
            "causal_interpretation": False,
            "diagnostic_only": True,
        }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    temporary.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    temporary.replace(args.output)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
