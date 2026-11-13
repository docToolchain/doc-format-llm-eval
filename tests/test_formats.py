"""Tests for format adapters: rendering and validation (PRD R-01, R-05)."""

from pathlib import Path

from docbench.formats import get_format


def write(root: Path, files: dict[str, str]) -> Path:
    for rel, content in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    return root


def test_r01_asciidoc_render_resolves_include(tmp_path):
    ws = write(tmp_path, {
        "main.adoc": "= Main\n\ninclude::shared/frag.adoc[]\n",
        "shared/frag.adoc": "Five replicas.\n",
    })

    rendered = get_format("asciidoc").render(ws, ["main.adoc"])

    assert "Five replicas." in rendered["main.adoc"]
    assert "include::" not in rendered["main.adoc"]


def test_r05_asciidoc_validate_reports_missing_include(tmp_path):
    ws = write(tmp_path, {"main.adoc": "= Main\n\ninclude::missing.adoc[]\n"})

    errors = get_format("asciidoc").validate(ws)

    assert any("missing.adoc" in e for e in errors)


def test_r05_asciidoc_validate_accepts_clean_document(tmp_path):
    ws = write(tmp_path, {"main.adoc": "= Main\n\n== Section\n\nText.\n"})

    assert get_format("asciidoc").validate(ws) == []


def test_gfm_render_produces_plain_text(tmp_path):
    ws = write(tmp_path, {"main.md": "# Main\n\nRuns as **five** replicas.\n"})

    rendered = get_format("gfm").render(ws, ["main.md"])

    assert "Runs as five replicas." in rendered["main.md"]


def test_r05_gfm_has_no_validator(tmp_path):
    ws = write(tmp_path, {"main.md": "# Main\n\n[broken](#nowhere)\n"})

    assert get_format("gfm").validate(ws) == []
