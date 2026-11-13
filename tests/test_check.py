"""Integration tests for the T-03 check against the real corpus."""

import shutil

from docbench.check import run_check
from docbench.spec import CORPUS_DIR


def workspace(tmp_path, fmt):
    ws = tmp_path / "ws"
    shutil.copytree(CORPUS_DIR / fmt, ws)
    return ws


def replace(path, old, new):
    path.write_text(path.read_text().replace(old, new))


def test_t03_untouched_corpus_fails(tmp_path):
    ws = workspace(tmp_path, "asciidoc")

    result = run_check("t03", "asciidoc", ws, CORPUS_DIR / "asciidoc")

    assert result["success"] is False
    assert "shared/deployment.adoc: fragment not edited" in result["single_source_violations"]


def test_t03_asciidoc_fragment_edit_succeeds(tmp_path):
    ws = workspace(tmp_path, "asciidoc")
    replace(ws / "shared/deployment.adoc", "three replicas", "five replicas")

    result = run_check("t03", "asciidoc", ws, CORPUS_DIR / "asciidoc")

    assert result == {
        "success": True,
        "fact_violations": [],
        "single_source_violations": [],
        "validation_errors": [],
    }


def test_t03_gfm_partial_edit_drifts(tmp_path):
    ws = workspace(tmp_path, "gfm")
    replace(ws / "architecture.md", "three replicas", "five replicas")

    result = run_check("t03", "gfm", ws, CORPUS_DIR / "gfm")

    assert result["success"] is False
    assert result["single_source_violations"] is None
    assert result["fact_violations"] == [
        "operations.md: missing '(five|5) replicas'",
        "operations.md: forbidden '(three|3) replicas'",
    ]
