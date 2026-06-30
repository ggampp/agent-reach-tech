from __future__ import annotations

from agent_reach_tech.config_loader import CONFIG_DIR, load_yaml
from agent_reach_tech.core.deps import check_all_deps
from agent_reach_tech.channels.registry import get_all_channels


def run_doctor(*, standalone: bool = True) -> int:
    print("")
    print("Agent Reach Tech — Status")
    print("=" * 40)

    cfg = load_yaml("channels.yaml")
    if cfg.get("standalone"):
        print("  Mode: standalone")
    print("")

    print("External dependencies:")
    for dep in check_all_deps():
        print(dep.doctor_line())

    channels = get_all_channels()
    by_category: dict[str, list] = {}
    required_ok = 0
    required_total = 0
    optional_ok = 0
    optional_total = 0

    print("")
    for channel in channels:
        status = channel.safe_probe()
        by_category.setdefault(status.category, []).append((channel, status))
        if channel.optional:
            optional_total += 1
            if status.available:
                optional_ok += 1
        else:
            required_total += 1
            if status.available:
                required_ok += 1

    for category, items in sorted(by_category.items()):
        print(f"Channels ({category}):")
        for channel, status in items:
            suffix = " (optional)" if channel.optional else ""
            line = status.doctor_line()
            if channel.optional and suffix not in line:
                line = line.replace(f"] {status.name}", f"] {status.name}{suffix}", 1)
            print(line)

    feeds = load_yaml("feeds.yaml").get("feeds", {})
    if feeds:
        print("")
        print("RSS feed categories:")
        for cat, items in feeds.items():
            print(f"  {cat}: {len(items)} feeds")

    print("")
    print(f"Config: {CONFIG_DIR}")
    print(f"Registered channels: {', '.join(ch.name for ch in channels)}")
    print(f"Required channels ready: {required_ok}/{required_total}")
    if optional_total:
        print(f"Optional channels ready: {optional_ok}/{optional_total}")
    print("")
    return 0 if required_ok == required_total else 1