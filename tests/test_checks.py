"""Tests for the deterministic checks of T-03 (edit shared fragment)."""

from docbench.checks import check_facts, check_single_source
from docbench.spec import Facts

FACTS = Facts(must_contain=[r"(five|5) replicas"], must_not_contain=[r"(three|3) replicas"])


def test_t03_facts_hold_in_every_master():
    rendered = {"a.adoc": "runs as five replicas", "b.adoc": "runs as 5 replicas"}

    assert check_facts(rendered, FACTS) == []


def test_t03_facts_report_each_master_that_drifted():
    rendered = {"a.adoc": "runs as five replicas", "b.adoc": "runs as three replicas"}

    violations = check_facts(rendered, FACTS)

    assert violations == [
        "b.adoc: missing '(five|5) replicas'",
        "b.adoc: forbidden '(three|3) replicas'",
    ]


def test_t03_facts_ignore_case():
    assert check_facts({"a.md": "Five Replicas"}, FACTS) == []


def test_t03_single_source_holds_when_only_fragment_changed():
    original = {
        "architecture.adoc": "== Deployment\n\ninclude::shared/deployment.adoc[]\n",
        "shared/deployment.adoc": "three replicas\n",
    }
    edited = {**original, "shared/deployment.adoc": "five replicas\n"}

    assert check_single_source(original, edited, "shared/deployment.adoc") == []


def test_t03_single_source_detects_inlined_include():
    original = {
        "architecture.adoc": "include::shared/deployment.adoc[]\n",
        "shared/deployment.adoc": "three replicas\n",
    }
    edited = {"architecture.adoc": "five replicas\n", "shared/deployment.adoc": "three replicas\n"}

    violations = check_single_source(original, edited, "shared/deployment.adoc")

    assert "architecture.adoc: include of shared/deployment.adoc removed" in violations
    assert "shared/deployment.adoc: fragment not edited" in violations
