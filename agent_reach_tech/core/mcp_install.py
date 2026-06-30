from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

MCP_ENTRY = {
    "command": "agent-reach-tech",
    "args": ["mcp"],
    "env": {},
}

TOML_BLOCK = """
[mcp_servers.agent-reach-tech]
command = "agent-reach-tech"
args = ["mcp"]
enabled = true
"""


def _merge_json_mcp(path: Path, *, dry_run: bool = False) -> str:
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
    else:
        data = {}
    servers = data.setdefault("mcpServers", {})
    if "agent-reach-tech" in servers:
        return f"skip (exists): {path}"
    servers["agent-reach-tech"] = dict(MCP_ENTRY)
    if not dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return f"installed: {path}"


def _append_toml_mcp(path: Path, *, dry_run: bool = False) -> str:
    if not path.exists():
        return f"skip (missing): {path}"
    text = path.read_text(encoding="utf-8")
    if "[mcp_servers.agent-reach-tech]" in text:
        return f"skip (exists): {path}"
    if not dry_run:
        path.write_text(text.rstrip() + TOML_BLOCK, encoding="utf-8")
    return f"installed: {path}"


def _grok_mcp_add(*, dry_run: bool = False) -> str:
    if dry_run:
        return "planned: grok mcp add agent-reach-tech -- agent-reach-tech mcp"
    try:
        result = subprocess.run(
            ["grok", "mcp", "add", "agent-reach-tech", "--", "agent-reach-tech", "mcp"],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        if result.returncode == 0:
            return "installed: grok user config (~/.grok/config.toml)"
        if "already" in (result.stdout + result.stderr).lower():
            return "skip (exists): grok"
        return f"grok failed ({result.returncode}): {result.stderr.strip() or result.stdout.strip()}"
    except FileNotFoundError:
        return "skip: grok CLI not found"
    except subprocess.TimeoutExpired:
        return "skip: grok mcp add timed out"


def install_mcp_configs(*, project_root: Path | None = None, dry_run: bool = False) -> list[str]:
    home = Path.home()
    results: list[str] = []

    for rel in (
        ".cursor/mcp.json",
        ".claude/mcp.json",
        ".gemini/config/mcp_config.json",  # Antigravity / Gemini Agent
    ):
        results.append(_merge_json_mcp(home / rel, dry_run=dry_run))

    results.append(_append_toml_mcp(home / ".codex/config.toml", dry_run=dry_run))
    results.append(_grok_mcp_add(dry_run=dry_run))

    if project_root:
        results.append(_merge_json_mcp(project_root / ".cursor/mcp.json", dry_run=dry_run))
        grok_project = project_root / ".grok/config.toml"
        if grok_project.exists():
            results.append(_append_toml_mcp(grok_project, dry_run=dry_run))
        elif not dry_run:
            grok_project.parent.mkdir(parents=True, exist_ok=True)
            grok_project.write_text(
                '[mcp_servers.agent-reach-tech]\ncommand = "agent-reach-tech"\nargs = ["mcp"]\nenabled = true\n',
                encoding="utf-8",
            )
            results.append(f"installed: {grok_project}")
        else:
            results.append(f"planned: {grok_project}")

    return results


def main(argv: list[str] | None = None) -> int:
    dry_run = "--dry-run" in (argv or sys.argv[1:])
    project = None
    for i, arg in enumerate(argv or sys.argv[1:]):
        if arg == "--project" and i + 1 < len(argv or sys.argv[1:]):
            project = Path((argv or sys.argv[1:])[i + 1])
    if project is None:
        project = Path.cwd()
        if (project / "agent-reach-tech").is_dir():
            project = project
        elif project.name == "agent-reach-tech":
            project = project.parent

    for line in install_mcp_configs(project_root=project, dry_run=dry_run):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())