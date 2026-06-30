from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agent_reach_tech.config_loader import PACKAGE_ROOT


def catalog_path() -> Path:
    candidates = [
        PACKAGE_ROOT.parent / "manifests" / "projects.json",
        Path.cwd() / "manifests" / "projects.json",
    ]
    for path in candidates:
        if path.exists():
            return path
    raise FileNotFoundError(
        "manifests/projects.json not found — place catalog at ./manifests/ or parent repo"
    )


def load_catalog() -> dict[str, Any]:
    with catalog_path().open(encoding="utf-8") as f:
        return json.load(f)


def search(term: str, *, limit: int = 10) -> list[dict[str, Any]]:
    term_lower = term.lower().strip()
    if not term_lower:
        return []
    data = load_catalog()
    matches: list[tuple[int, dict[str, Any]]] = []
    for project in data.get("projects", []):
        score = _score_project(project, term_lower)
        if score > 0:
            matches.append((score, project))
    matches.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in matches[:limit]]


def _score_project(project: dict[str, Any], term: str) -> int:
    score = 0
    if term in project.get("id", "").lower():
        score += 100
    if term in project.get("name", "").lower():
        score += 80
    for field in ("summary", "notes"):
        if term in (project.get(field) or "").lower():
            score += 30
    for tag in project.get("tags", []):
        if term in tag.lower():
            score += 40
    for use in project.get("use_cases", []):
        if term in use.lower():
            score += 10
    return score