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
    original_fragment: str | None,
    edited_fragment: str | None,
    fragment: str,
    rendered_with_sentinel: dict[str, str],
    sentinel: str,
) -> list[str]:
    """The change belongs in the fragment, and every master must still render it.

    The caller writes a sentinel into the fragment and renders the masters.
    A master that no longer shows the sentinel has dropped the include, whether
    it was deleted, commented out or hidden behind an inactive conditional.
    """
    violations = [
        f"{doc}: does not include {fragment}"
        for doc, text in rendered_with_sentinel.items()
        if sentinel not in text
    ]
    if edited_fragment == original_fragment:
        violations.append(f"{fragment}: fragment not edited")
    return violations
