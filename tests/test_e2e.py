"""End-to-end run of T-03 in the Docker sandbox with a scripted mock model.

Proves the wiring: corpus -> sandbox -> agent tools -> checks -> score.
"""

import shutil
import subprocess

import pytest
from inspect_ai import eval as inspect_eval
from inspect_ai.model import ModelOutput, get_model

from docbench.eval import t03


def docker_available() -> bool:
    return shutil.which("docker") is not None and subprocess.run(
        ["docker", "info"], capture_output=True, check=False
    ).returncode == 0


pytestmark = [
    pytest.mark.e2e,
    pytest.mark.skipif(not docker_available(), reason="needs a Docker daemon"),
]


def scripted_model(*edits: dict):
    calls = [
        ModelOutput.for_tool_call("mockllm/model", "text_editor", {"command": "str_replace", **e})
        for e in edits
    ]
    calls.append(ModelOutput.for_tool_call("mockllm/model", "submit", {"answer": "done"}))
    return get_model("mockllm/model", custom_outputs=calls)


def run_log(task, model, tmp_path):
    [log] = inspect_eval(task, model=model, log_dir=str(tmp_path), display="none")
    assert log.status == "success", log.error
    return log


def run(task, model, tmp_path):
    return run_log(task, model, tmp_path).samples[0].scores["workspace_check"].value


def test_t03_asciidoc_fragment_edit_scores_success(tmp_path):
    model = scripted_model({
        "path": "/workspace/shared/deployment.adoc",
        "old_str": "three replicas", "new_str": "five replicas",
    })

    score = run(t03(format="asciidoc"), model, tmp_path)

    assert score["success"] == 1


def test_t03_gfm_single_copy_edit_scores_drift(tmp_path):
    model = scripted_model({
        "path": "/workspace/architecture.md",
        "old_str": "three replicas", "new_str": "five replicas",
    })

    score = run(t03(format="gfm"), model, tmp_path)

    assert score["success"] == 0
    assert score["fact_violations"] == 2


def test_t03_agent_cannot_rewrite_grading_files(tmp_path):
    model = scripted_model({
        "path": "/opt/docbench/tasks/t03.yaml",
        "old_str": "(five|5) replicas", "new_str": "(three|3) replicas",
    })

    log = run_log(t03(format="asciidoc"), model, tmp_path)

    [edit] = [m for m in log.samples[0].messages if m.role == "tool" and m.function == "text_editor"]
    assert edit.error is not None
    assert "denied" in edit.error.message.lower()
