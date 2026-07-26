#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .common import canonical_bytes
from .configs import generate_matrix, validate_matrix
from .confirmation import validate_confirmation_manifest
from .protocol_tools import validate_frozen_protocol


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("audit", "matrix", "formal-confirmation-preflight"))
    parser.add_argument("--confirmation-manifest", type=Path)
    parser.add_argument("--forbidden-development-hash", action="append", default=[])
    args = parser.parse_args()
    protocol_hash = validate_frozen_protocol()
    configs = generate_matrix()
    validate_matrix(configs)
    if args.command == "matrix":
        print(canonical_bytes({"protocol_sha256": protocol_hash, "configs": configs})
              .decode("utf-8"), end="")
    elif args.command == "formal-confirmation-preflight":
        receipt = validate_confirmation_manifest(
            args.confirmation_manifest, forbidden_hashes=args.forbidden_development_hash
        )
        print(json.dumps(receipt, ensure_ascii=False, indent=2))
    else:
        print(json.dumps({
            "status": "passed",
            "protocol_sha256": protocol_hash,
            "config_count": len(configs),
            "formal_training_started": False,
        }, indent=2))


if __name__ == "__main__":
    main()
