"""Inspect AI tasks. Orchestration only: corpus, tasks and checks stay framework-independent."""

from __future__ import annotations

import json
from pathlib import Path

from inspect_ai import Task, task
from inspect_ai.agent import react
from inspect_ai.dataset import Sample
from inspect_ai.scorer import Score, Target, mean, scorer, stderr
from inspect_ai.solver import TaskState
from inspect_ai.tool import Tool, text_editor, tool
from inspect_ai.util import sandbox

from docbench.spec import load_task

COMPOSE = Path(__file__).resolve().parents[2] / "docker" / "compose.yaml"
SANDBOX_ROOT = "/opt/docbench"
WORKSPACE = "/workspace"
# The model edits as this unprivileged user; only the scorer runs as root.
AGENT_USER = "agent"

FORMAT_LABELS = {"asciidoc": "AsciiDoc", "gfm": "GitHub Flavored Markdown"}

PROMPT = """\
You maintain technical documentation written in {label}. It lives in {workspace}.

Change request: {change_request}

Edit the files in {workspace} to implement the change request.{feedback_hint}
When you are done, call submit."""

FEEDBACK_HINT = (
    "\nUse the validate tool to check the documentation."
    " Fix every reported problem before you submit."
)


@tool
def validate(format_name: str) -> Tool:
    async def execute() -> str:
        """Validate the documentation in /workspace and list every problem found.

        Returns:
            The problems, one per line, or "No problems found."
        """
        result = await sandbox().exec(
            ["python3", "-m", "docbench.validate", "--format", format_name, "--workspace", WORKSPACE],
            user=AGENT_USER,
        )
        return (result.stdout + result.stderr).strip()

    return execute


@scorer(metrics={
    "success": [mean(), stderr()],
    "fact_violations": [mean()],
    "single_source_violations": [mean()],
    "validation_errors": [mean()],
})
def workspace_check(task_name: str, format_name: str):
    async def score(state: TaskState, target: Target) -> Score:
        result = await sandbox().exec([
            "python3", "-m", "docbench.check", "--task", task_name, "--format", format_name,
            "--workspace", WORKSPACE, "--original", f"{SANDBOX_ROOT}/corpus/{format_name}",
        ])
        data = json.loads(result.stdout)
        return Score(
            value={
                "success": int(data["success"]),
                "fact_violations": len(data["fact_violations"]),
                "single_source_violations": len(data["single_source_violations"] or []),
                "validation_errors": len(data["validation_errors"]),
            },
            explanation=json.dumps(data, indent=2),
        )

    return score


def build_prompt(task_name: str, format_name: str, feedback: bool) -> str:
    spec = load_task(task_name)
    return PROMPT.format(
        label=FORMAT_LABELS[format_name],
        workspace=WORKSPACE,
        change_request=spec.change_request,
        feedback_hint=FEEDBACK_HINT if feedback else "",
    )


@task
def t03(format: str = "asciidoc", feedback: bool = False) -> Task:
    """T-03: edit a paragraph shared by two master documents."""
    tools = [text_editor(user=AGENT_USER)] + ([validate(format)] if feedback else [])
    return Task(
        dataset=[Sample(
            input=build_prompt("t03", format, feedback),
            setup=(
                f"cp -r {SANDBOX_ROOT}/corpus/{format}/. {WORKSPACE}/"
                f" && chown -R {AGENT_USER}:{AGENT_USER} {WORKSPACE}"
            ),
        )],
        solver=react(tools=tools),
        scorer=workspace_check("t03", format),
        sandbox=("docker", str(COMPOSE)),
        metadata={"format": format, "feedback": feedback},
    )
