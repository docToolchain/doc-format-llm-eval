"""Format adapters: one renderer and one validator per documentation format.

A new format plugs in by adding a class here and registering it in FORMATS.
"""

from __future__ import annotations

import html
import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Protocol

from markdown_it import MarkdownIt


class Format(Protocol):
    name: str
    extension: str

    def render(self, workspace: Path, masters: list[str]) -> dict[str, str]: ...

    def validate(self, workspace: Path) -> list[str]: ...


def html_to_text(markup: str) -> str:
    text = re.sub(r"<[^>]+>", "", markup)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def _tool(name: str) -> str:
    """Resolve a CLI tool next to the running interpreter first, then on PATH."""
    import sys

    local = Path(sys.executable).parent / name
    return str(local) if local.exists() else (shutil.which(name) or name)


class AsciiDoc:
    name = "asciidoc"
    extension = ".adoc"

    def render(self, workspace: Path, masters: list[str]) -> dict[str, str]:
        return {doc: html_to_text(self._asciidoctor(workspace / doc).stdout) for doc in masters}

    def validate(self, workspace: Path) -> list[str]:
        files = sorted(workspace.rglob("*.adoc"))
        return self._lint(workspace, files) + self._build_warnings(workspace, files)

    @staticmethod
    def _asciidoctor(path: Path) -> subprocess.CompletedProcess:
        return subprocess.run(
            [_tool("asciidoctor"), "-S", "safe", "-e", "-o", "-", path.name],
            cwd=path.parent, capture_output=True, text=True, check=False,
        )

    @staticmethod
    def _lint(workspace: Path, files: list[Path]) -> list[str]:
        if not files:
            return []
        result = subprocess.run(
            [_tool("asciidoc-linter"), "--format", "json", *[str(f) for f in files]],
            capture_output=True, text=True, check=False,
        )
        findings = json.loads(result.stdout or "{}").get("findings", [])
        return [
            f"{Path(f['file']).relative_to(workspace).as_posix()}:{f['line']}: "
            f"{f['rule_id']} {f['message']}"
            for f in findings
        ]

    def _build_warnings(self, workspace: Path, files: list[Path]) -> list[str]:
        """Asciidoctor reports missing includes and broken references on stderr."""
        warnings = []
        for f in files:
            for line in self._asciidoctor(f).stderr.splitlines():
                if line.strip():
                    warnings.append(f"{f.relative_to(workspace).as_posix()}: {line.strip()}")
        return warnings


class Gfm:
    name = "gfm"
    extension = ".md"

    def __init__(self) -> None:
        self._md = MarkdownIt("gfm-like")

    def render(self, workspace: Path, masters: list[str]) -> dict[str, str]:
        return {doc: html_to_text(self._md.render((workspace / doc).read_text())) for doc in masters}

    def validate(self, workspace: Path) -> list[str]:
        # GFM has no authoritative validator (PRD R-05): every input renders.
        return []


FORMATS: dict[str, Format] = {f.name: f for f in (AsciiDoc(), Gfm())}


def get_format(name: str) -> Format:
    return FORMATS[name]
