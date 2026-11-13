"""Turn Inspect AI logs into a results table (AsciiDoc).

Usage: python -m docbench.report [LOG_DIR]
"""

from __future__ import annotations

import sys
from dataclasses import dataclass

HEADER = "|Task |Format |Feedback |Model |Runs |Success |Fact violations |Single-source violations |Validation errors"


@dataclass(frozen=True)
class Row:
    task: str
    format: str
    feedback: bool
    model: str
    runs: int
    success: float
    fact_violations: float
    single_source_violations: float
    validation_errors: float


def summarize(logs) -> list[Row]:
    rows = [_row(log) for log in logs if log.results]
    return sorted(rows, key=lambda r: (r.task, r.format, r.feedback, r.model))


def _row(log) -> Row:
    means = {s.name: s.metrics["mean"].value for s in log.results.scores}
    args = log.eval.task_args
    return Row(
        task=log.eval.task, format=args["format"], feedback=bool(args["feedback"]),
        model=log.eval.model, runs=log.results.total_samples,
        success=means["success"], fact_violations=means["fact_violations"],
        single_source_violations=means["single_source_violations"],
        validation_errors=means["validation_errors"],
    )


def to_asciidoc(rows: list[Row]) -> str:
    lines = ['[cols="1,1,1,2,1,1,1,1,1",options="header"]', "|===", HEADER]
    for r in rows:
        lines.append(
            f"|{r.task} |{r.format} |{'with' if r.feedback else 'without'} |{r.model} |{r.runs} "
            f"|{r.success:.0%} |{r.fact_violations:.1f} |{r.single_source_violations:.1f} "
            f"|{r.validation_errors:.1f}"
        )
    lines.append("|===")
    return "\n".join(lines) + "\n"


def main() -> None:
    from inspect_ai.log import list_eval_logs, read_eval_log

    log_dir = sys.argv[1] if len(sys.argv) > 1 else "logs"
    logs = [read_eval_log(info) for info in list_eval_logs(log_dir)]
    print(to_asciidoc(summarize(logs)), end="")


if __name__ == "__main__":
    main()
