"""Read-only dashboard aggregation helpers for the platform database."""
from __future__ import annotations

from typing import Any

from app.platform.repositories import PlatformRepository


def safe_records(repo: PlatformRepository, table: str, where: str = "", params: tuple = ()) -> list[dict[str, Any]]:
    try:
        return repo.list_records(table, where=where, params=params)
    except Exception:
        return []


def designs_for_projects(repo: PlatformRepository, projects: list[dict[str, Any]]) -> list[dict[str, Any]]:
    designs: list[dict[str, Any]] = []
    for project in projects:
        designs.extend(safe_records(repo, "designs", "project_id=?", (project["id"],)))
    return designs


def latest_quality(repo: PlatformRepository, design_id: str) -> float | None:
    results = safe_records(repo, "design_results", "design_id=?", (design_id,))
    scores = [r.get("quality_score") for r in results if r.get("quality_score") is not None]
    return float(scores[0]) if scores else None
