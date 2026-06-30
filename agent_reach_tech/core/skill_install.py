from __future__ import annotations

import shutil
from pathlib import Path

from agent_reach_tech.config_loader import PACKAGE_ROOT

SKILL_SRC = PACKAGE_ROOT / "skill" / "SKILL.md"


def skill_targets() -> list[Path]:
    home = Path.home()
    known = [".cursor", ".claude", ".grok", ".agents", ".codex", ".windsurf", ".antigravity", ".gemini"]
    targets: list[Path] = []
    seen: set[str] = set()

    for agent_dir in known:
        base = home / agent_dir
        if base.exists():
            target = base / "skills" / "agent-reach-tech" / "SKILL.md"
            targets.append(target)
            seen.add(str(target))

    if home.exists():
        for entry in home.iterdir():
            if not entry.is_dir() or not entry.name.startswith("."):
                continue
            skills_dir = entry / "skills"
            if skills_dir.is_dir():
                target = skills_dir / "agent-reach-tech" / "SKILL.md"
                key = str(target)
                if key not in seen:
                    targets.append(target)
                    seen.add(key)

    if not targets:
        targets.append(home / ".cursor" / "skills" / "agent-reach-tech" / "SKILL.md")
    return sorted(targets, key=str)


def install_skill(*, dry_run: bool = False) -> list[str]:
    if not SKILL_SRC.exists():
        raise FileNotFoundError(f"SKILL.md not found: {SKILL_SRC}")
    installed = []
    for target in skill_targets():
        if dry_run:
            installed.append(str(target))
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(SKILL_SRC, target)
        installed.append(str(target))
    return installed