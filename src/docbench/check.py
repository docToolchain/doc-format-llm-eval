"""Check a workspace after an LLM run. Runs inside the sandbox; prints JSON.

Usage: python -m docbench.check --task t03 --format asciidoc --workspace DIR --original DIR
"""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path

from docbench.checks import check_facts, check_single_source
from docbench.formats import Format, get_format
from docbench.spec import load_task

SENTINEL = "DOCBENCH-SENTINEL-7f3a"


def run_check(task: str, format_name: str, workspace: Path, original: Path) -> dict:
    spec = load_task(task)
    fmt = get_format(format_name)
    fact_violations = check_facts(fmt.render(workspace, spec.masters[format_name]), spec.facts)
    single_source = _single_source(
        fmt, spec.fragment.get(format_name), spec.masters[format_name], original, workspace
    )
    validation_errors = fmt.validate(workspace)
    return {
        "success": not fact_violations and not single_source and not validation_errors,
        "fact_violations": fact_violations,
        "single_source_violations": single_source,
        "validation_errors": validation_errors,
    }


def _single_source(
    fmt: Format, fragment: str | None, masters: list[str], original: Path, workspace: Path
) -> list[str] | None:
    """None when the format has no single source for this task (e.g. GFM copies)."""
    if fragment is None:
        return None
    return check_single_source(
        _read(original / fragment),
        _read(workspace / fragment),
        fragment,
        _render_with_sentinel(fmt, workspace, fragment, masters),
        SENTINEL,
    )


def _read(path: Path) -> str | None:
    return path.read_text() if path.is_file() else None


def _render_with_sentinel(fmt: Format, workspace: Path, fragment: str, masters: list[str]) -> dict[str, str]:
    with tempfile.TemporaryDirectory() as tmp:
        probe = Path(tmp) / "ws"
        shutil.copytree(workspace, probe)
        (probe / fragment).parent.mkdir(parents=True, exist_ok=True)
        (probe / fragment).write_text(SENTINEL + "\n")
        return fmt.render(probe, masters)


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
