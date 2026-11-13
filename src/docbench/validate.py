"""Validator feedback for the LLM. Runs inside the sandbox.

Usage: python -m docbench.validate --format asciidoc --workspace DIR
"""

from __future__ import annotations

import argparse
from pathlib import Path

from docbench.formats import get_format


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--format", required=True)
    parser.add_argument("--workspace", required=True, type=Path)
    args = parser.parse_args()
    errors = get_format(args.format).validate(args.workspace)
    print("\n".join(errors) if errors else "No problems found.")


if __name__ == "__main__":
    main()
