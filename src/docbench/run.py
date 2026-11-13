"""Run T-03 for every format and both feedback conditions, then print the report.

Usage: python -m docbench.run --model anthropic/<model> [--epochs 5] [--log-dir logs]
"""

from __future__ import annotations

import argparse

from inspect_ai import eval as inspect_eval

from docbench.eval import t03
from docbench.report import summarize, to_asciidoc

FORMATS = ["asciidoc", "gfm"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, help="Inspect model name, e.g. anthropic/<model>")
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--log-dir", default="logs")
    args = parser.parse_args()

    tasks = [t03(format=f, feedback=fb) for f in FORMATS for fb in (False, True)]
    logs = inspect_eval(tasks, model=args.model, epochs=args.epochs, log_dir=args.log_dir)
    print(to_asciidoc(summarize(logs)), end="")


if __name__ == "__main__":
    main()
