"""Check a workspace after an LLM run. Runs inside the sandbox; prints JSON.

Usage: python -m docbench.check --task t03 --format asciidoc --workspace DIR --original DIR
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from docbench.checks import check_facts, check_single_source
from docbench.formats import get_format
from docbench.spec import load_task, read_tree


def run_check(task: str, format_name: str, workspace: Path, original: Path) -> dict:
    spec = load_task(task)
    fmt = get_format(format_name)
    fact_violations = check_facts(fmt.render(workspace, spec.masters[format_name]), spec.facts)
    single_source = _single_source(spec.fragment.get(format_name), original, workspace)
    validation_errors = fmt.validate(workspace)
    return {
        "success": not fact_violations and not single_source and not validation_errors,
        "fact_violations": fact_violations,
        "single_source_violations": single_source,
        "validation_errors": validation_errors,
    }


def _single_source(fragment: str | None, original: Path, workspace: Path) -> list[str] | None:
    """None when the format has no single source for this task (e.g. GFM copies)."""
    if fragment is None:
        return None
    return check_single_source(read_tree(original), read_tree(workspace), fragment)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", required=True)
    parser.add_argument("--format", required=True)
    parser.add_argument("--workspace", required=True, type=Path)
    parser.add_argument("--original", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(run_check(args.task, args.format, args.workspace, args.original)))


if __name__ == "__main__":
    main()
