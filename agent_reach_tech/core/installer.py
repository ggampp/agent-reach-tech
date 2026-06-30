from __future__ import annotations

import importlib.util
import subprocess
import sys
from dataclasses import dataclass, field

from agent_reach_tech.config_loader import PACKAGE_ROOT
from agent_reach_tech.core.deps import check_all_deps
from agent_reach_tech.core.subprocess_runner import which


@dataclass
class InstallAction:
    description: str
    command: list[str] | None = None
    executed: bool = False
    skipped: bool = False
    reason: str = ""


@dataclass
class InstallReport:
    env: str
    safe: bool
    dry_run: bool
    actions: list[InstallAction] = field(default_factory=list)

    def add(self, description: str, command: list[str] | None = None) -> None:
        self.actions.append(InstallAction(description=description, command=command))


def build_install_report(*, env: str = "auto", safe: bool = False, dry_run: bool = False) -> InstallReport:
    report = InstallReport(env=env, safe=safe, dry_run=dry_run)
    report.add("Install agent-reach-tech package (editable)", [sys.executable, "-m", "pip", "install", "-e", str(PACKAGE_ROOT)])

    if not _has_module("feedparser"):
        report.add("Install feedparser for RSS channel", [sys.executable, "-m", "pip", "install", "feedparser>=6.0"])

    if not _has_module("mcp"):
        report.add(
            "Install MCP SDK for agent-reach-tech mcp server",
            [sys.executable, "-m", "pip", "install", "agent-reach-tech[mcp]"],
        )

    report.add("Copy SKILL.md to agent skill directories", None)

    for dep in check_all_deps():
        if dep.available:
            continue
        if dep.name == "gh":
            report.add("Install GitHub CLI: winget install GitHub.cli", None)
        elif dep.name == "yt-dlp":
            report.add("Install yt-dlp: pip install yt-dlp", [sys.executable, "-m", "pip", "install", "yt-dlp"])
        elif dep.name == "mcporter":
            if safe:
                report.add("Optional: npm install -g mcporter (skipped in --safe)", None)
            else:
                report.add("Optional: install mcporter for Exa MCP", ["npm", "install", "-g", "mcporter"])

    if env == "server":
        report.add("Server mode: prefer EXA_API_KEY env var over browser tools", None)

    return report


def execute_install_report(report: InstallReport) -> InstallReport:
    from agent_reach_tech.core.skill_install import install_skill  # noqa: PLC0415

    for action in report.actions:
        if action.command is None:
            if "SKILL.md" in action.description:
                if report.dry_run:
                    action.skipped = True
                    action.reason = "dry-run"
                    install_skill(dry_run=True)
                    continue
                install_skill()
                action.executed = True
            else:
                action.skipped = True
                action.reason = "manual step"
            continue

        if report.dry_run:
            action.skipped = True
            action.reason = "dry-run"
            continue

        if report.safe and _is_system_command(action.command):
            action.skipped = True
            action.reason = "safe mode"
            continue

        try:
            result = subprocess.run(action.command, capture_output=True, text=True, check=False, timeout=120)
            action.executed = result.returncode == 0
            if not action.executed:
                action.reason = (result.stderr or result.stdout or "failed").strip()[:200]
        except Exception as e:  # noqa: BLE001
            action.skipped = True
            action.reason = str(e)

    return report


def _has_module(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def _is_system_command(command: list[str]) -> bool:
    if not command:
        return False
    exe = command[0].lower()
    return exe in {"npm", "winget", "brew", "apt", "apt-get"}