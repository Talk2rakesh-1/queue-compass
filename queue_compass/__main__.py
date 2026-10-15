"""JSON files only; never load executable/pickle model artifacts."""

import argparse
import json
import sys
from pathlib import Path

from .model import Router, evaluate


def read_json(path):
    with Path(path).open("rb") as stream:
        payload = stream.read(2_000_001)
    if len(payload) > 2_000_000:
        raise ValueError("JSON file exceeds 2 MB")
    return json.loads(payload)


def main():
    parser = argparse.ArgumentParser(description="Local human-reviewed ticket routing")
    parser.add_argument("command", choices=["predict", "evaluate", "validate"])
    parser.add_argument("--training", type=Path, default=Path("data/train.json"))
    parser.add_argument(
        "--input",
        type=Path,
        help="JSON object {text: ...} for predict, labeled array for evaluate",
    )
    args = parser.parse_args()
    try:
        router = Router(read_json(args.training))
        if args.command == "validate":
            result = {
                "classes": sorted(router.documents),
                "examples": router.size,
                "vocabulary": len(router.vocabulary),
            }
        else:
            if args.input is None:
                parser.error("--input is required")
            data = read_json(args.input)
            if args.command == "predict":
                if not isinstance(data, dict) or set(data) != {"text"}:
                    raise ValueError("prediction input must be an object with only text")
                result = router.predict(data["text"])
            else:
                result = evaluate(router, data)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except (ValueError, OSError, TypeError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
