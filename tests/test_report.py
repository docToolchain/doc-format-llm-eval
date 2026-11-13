"""Tests for the results report (PRD: metrics per task x format x condition)."""

from types import SimpleNamespace as NS

from docbench.report import Row, summarize, to_asciidoc


def fake_log(fmt, feedback, success, facts=0.0, single=0.0, errors=0.0):
    def score(name, mean):
        return NS(name=name, metrics={"mean": NS(value=mean)})

    return NS(
        eval=NS(task="t03", task_args={"format": fmt, "feedback": feedback}, model="m"),
        results=NS(total_samples=5, scores=[
            score("success", success), score("fact_violations", facts),
            score("single_source_violations", single), score("validation_errors", errors),
        ]),
    )


def test_t03_summarize_sorts_by_task_format_feedback():
    rows = summarize([fake_log("gfm", True, 0.2), fake_log("asciidoc", False, 1.0)])

    assert rows == [
        Row("t03", "asciidoc", False, "m", 5, 1.0, 0.0, 0.0, 0.0),
        Row("t03", "gfm", True, "m", 5, 0.2, 0.0, 0.0, 0.0),
    ]


def test_t03_asciidoc_table_has_one_line_per_row():
    table = to_asciidoc([Row("t03", "gfm", True, "m", 5, 0.4, 1.2, 0.0, 0.0)])

    assert table.startswith("[cols=")
    assert "|t03 |gfm |with |m |5 |40% |1.2 |0.0 |0.0" in table
