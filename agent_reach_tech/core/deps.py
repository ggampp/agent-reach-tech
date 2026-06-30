from __future__ import annotations

import importlib.util
import sys
from dataclasses import dataclass

from agent_reach_tech.core.subprocess_runner import which


@dataclass(frozen=True)
class DepReport:
    name: str
    available: bool
    path: str | None
    required: bool
    note: str = ""
    sprint: str = ""

    def doctor_line(self) -> str:
        if self.available:
            detail = self.path or self.note
            suffix = f": {detail}" if detail else ""
            return f"  [OK] {self.name}{suffix}"
        level = "!!" if self.required else "--"
        hint = f" — {self.note}" if self.note else ""
        return f"  [{level}] {self.name}: not found{hint}"


def _module_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def check_all_deps() -> list[DepReport]:
    reports: list[DepReport] = []

    gh = which("gh")
    reports.append(
        DepReport(
            name="gh",
            available=gh is not None,
            path=gh,
            required=False,
            note="GitHub repos, issues, search (Sprint 1)",
            sprint="1",
        )
    )

    curl = which("curl")
    reports.append(
        DepReport(
            name="curl",
            available=curl is not None,
            path=curl,
            required=False,
            note="Web via Jina Reader (Sprint 1)",
            sprint="1",
        )
    )

    ytdlp = which("yt-dlp") or which("yt_dlp")
    reports.append(
        DepReport(
            name="yt-dlp",
            available=ytdlp is not None,
            path=ytdlp,
            required=False,
            note="YouTube subtitles (Sprint 2)",
            sprint="2",
        )
    )

    feedparser_ok = _module_available("feedparser")
    reports.append(
        DepReport(
            name="feedparser",
            available=feedparser_ok,
            path=sys.executable if feedparser_ok else None,
            required=False,
            note="pip install feedparser (Sprint 2)" if not feedparser_ok else "RSS feeds",
            sprint="2",
        )
    )

    mcporter = which("mcporter")
    reports.append(
        DepReport(
            name="mcporter",
            available=mcporter is not None,
            path=mcporter,
            required=False,
            note="Exa semantic search via MCP (Sprint 3)",
            sprint="3",
        )
    )

    return reports


def available_deps() -> list[DepReport]:
    return [d for d in check_all_deps() if d.available]


def missing_planned_deps(up_to_sprint: int | None = None) -> list[DepReport]:
    deps = check_all_deps()
    if up_to_sprint is None:
        return [d for d in deps if not d.available]
    return [
        d
        for d in deps
        if not d.available and d.sprint.isdigit() and int(d.sprint) <= up_to_sprint
    ]