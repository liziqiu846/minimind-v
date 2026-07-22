#!/usr/bin/env python3
"""Run the fixed two-model, 153-image Phase 3 v5 engineering pilot."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ in (None, ""):
    _script_dir = Path(__file__).resolve().parent
    sys.path = [entry for entry in sys.path if Path(entry or ".").resolve() != _script_dir]
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from experiments.phase3.canonical_io import validate_disjoint_roots
from experiments.phase3.phase3_protocol_v5 import Phase3ProtocolV5
from experiments.phase3.runner_common import execute_evaluation
from experiments.phase3.status import (
    Phase3ArgumentParser, Phase3Blocked, Phase3HardFailure, execute_with_status, require_status_output,
)


def parse_args() -> argparse.Namespace:
    parser = Phase3ArgumentParser(description=__doc__)
    for name in (
        "protocol", "expected_registry", "verification_receipt", "prepared_data_dir",
        "coco_root", "stage2_artifact_root", "output_dir",
    ):
        parser.add_argument("--" + name.replace("_", "-"), type=Path, required=True)
    parser.add_argument("--stage2-protocol", type=Path, default=Path("experiments/stage2_protocol_v2.json"))
    parser.add_argument("--device", required=True)
    parser.add_argument("--item-batch-size", type=int, required=True)
    parser.add_argument("--confirm-protocol-hash", required=True)
    require_status_output(parser)
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    def operation():
        validate_disjoint_roots(
            input_roots=[
                args.protocol.parent, args.expected_registry.parent, args.verification_receipt.parent,
                args.prepared_data_dir, args.coco_root, args.stage2_artifact_root,
                args.stage2_protocol.parent,
            ],
            output_roots=[args.output_dir, args.status_output.parent],
            forbidden_exact=[Path("/"), Path.home(), Path(__file__).resolve().parents[2]],
        )
        protocol = Phase3ProtocolV5.load(args.protocol)
        if protocol.raw_sha256 != args.confirm_protocol_hash:
            raise Phase3HardFailure("pilot_protocol_hash_mismatch", "confirmed protocol hash mismatch")
        filenames = (args.prepared_data_dir / "pilot_filenames.txt").read_text(encoding="utf-8").splitlines()
        try:
            return execute_evaluation(
                run_mode="pilot", model_ids=["M1-root-none", "M3-root-43101"], filenames=filenames,
                protocol_path=args.protocol, expected_registry_path=args.expected_registry,
                verification_receipt_path=args.verification_receipt,
                prepared_data_dir=args.prepared_data_dir, coco_root=args.coco_root,
                artifact_root=args.stage2_artifact_root, output_dir=args.output_dir,
                device=args.device, item_batch_size=args.item_batch_size,
                stage2_protocol_path=args.stage2_protocol, metric_version="v5",
            )
        except FileNotFoundError as error:
            raise Phase3Blocked("blocked_pilot_resource", str(error)) from error
        except RuntimeError as error:
            message = str(error).lower()
            if any(token in message for token in ("unavailable", "not verified", "out of memory")):
                raise Phase3Blocked("blocked_pilot_resource", str(error)) from error
            raise Phase3HardFailure("pilot_runtime_failure", str(error)) from error
        except (ValueError, FileExistsError, OSError) as error:
            raise Phase3HardFailure("pilot_invariant_failure", str(error)) from error

    return execute_with_status("run_phase3_pilot_v5", args.status_output, operation)


if __name__ == "__main__":
    raise SystemExit(main())
