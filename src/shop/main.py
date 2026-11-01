"""Console entry point."""
from __future__ import annotations

import sys
from pathlib import Path

from shop.config import Config
from shop.pipeline import run_pipeline


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 2:
        print("Usage: python -m shop.main <input.csv> <output.json>")
        return 2
    stats = run_pipeline(Path(args[0]), Path(args[1]), Config.from_env())
    for key, value in stats.items():
        print(f"{key}: {value:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
