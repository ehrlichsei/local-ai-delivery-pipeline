"""Command-line wrapper that validates an issue agent patch before applying it."""

import sys
from pathlib import Path

from issue_patch import validate_patch_paths


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python agents/validate_issue_patch.py <patch-file>")
    patch_path = Path(sys.argv[1])
    paths = validate_patch_paths(patch_path.read_text(encoding="utf-8"))
    print("Patch paths allowed: " + ", ".join(paths))


if __name__ == "__main__":
    main()
