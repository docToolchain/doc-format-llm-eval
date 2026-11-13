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


SENTINEL = "SENTINEL-0001"


def test_t03_single_source_holds_when_every_master_renders_the_fragment():
    rendered = {"a.adoc": f"x {SENTINEL} y", "b.adoc": SENTINEL}

    violations = check_single_source("three", "five", "frag.adoc", rendered, SENTINEL)

    assert violations == []


def test_t03_single_source_detects_master_without_fragment():
    rendered = {"a.adoc": SENTINEL, "b.adoc": "inlined copy"}

    violations = check_single_source("three", "three", "frag.adoc", rendered, SENTINEL)

    assert violations == [
        "b.adoc: does not include frag.adoc",
        "frag.adoc: fragment not edited",
    ]
