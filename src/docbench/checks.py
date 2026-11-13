"""Deterministic checks. Each function is a pure operation over text."""

from __future__ import annotations

import re

from docbench.spec import Facts


def check_facts(rendered: dict[str, str], facts: Facts) -> list[str]:
    """Every master document must contain all required facts and no forbidden ones."""
    violations = []
    for doc, text in rendered.items():
        for pattern in facts.must_contain:
            if not re.search(pattern, text, re.IGNORECASE):
                violations.append(f"{doc}: missing '{pattern}'")
        for pattern in facts.must_not_contain:
            if re.search(pattern, text, re.IGNORECASE):
                violations.append(f"{doc}: forbidden '{pattern}'")
    return violations


def check_single_source(
    original: dict[str, str], edited: dict[str, str], fragment: str
) -> list[str]:
    """The change belongs in the fragment; every include of it must survive."""
    directive = f"include::{fragment}[]"
    violations = []
    for doc, text in original.items():
        if directive in text and directive not in edited.get(doc, ""):
            violations.append(f"{doc}: include of {fragment} removed")
    if edited.get(fragment) == original.get(fragment):
        violations.append(f"{fragment}: fragment not edited")
    return violations
