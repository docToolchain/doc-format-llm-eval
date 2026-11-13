"""Task specifications: tasks live as YAML data in tasks/, not in code."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
TASKS_DIR = ROOT / "tasks"
CORPUS_DIR = ROOT / "corpus"


@dataclass(frozen=True)
class Facts:
    must_contain: list[str] = field(default_factory=list)
    must_not_contain: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class TaskSpec:
    id: str
    title: str
    change_request: str
    masters: dict[str, list[str]]
    fragment: dict[str, str]
    facts: Facts


def load_task(name: str, tasks_dir: Path = TASKS_DIR) -> TaskSpec:
    data = yaml.safe_load((tasks_dir / f"{name}.yaml").read_text())
    return TaskSpec(
        id=data["id"],
        title=data["title"],
        change_request=data["change_request"],
        masters=data["masters"],
        fragment=data.get("fragment", {}),
        facts=Facts(**data["facts"]),
    )


def read_tree(root: Path) -> dict[str, str]:
    """All text files below root, keyed by POSIX path relative to root."""
    return {
        p.relative_to(root).as_posix(): p.read_text()
        for p in sorted(root.rglob("*"))
        if p.is_file()
    }
