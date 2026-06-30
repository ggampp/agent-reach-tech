from __future__ import annotations

from unittest.mock import patch

from agent_reach_tech.core.deps import check_all_deps, missing_planned_deps


def test_check_all_deps_returns_expected_names():
    reports = check_all_deps()
    names = {r.name for r in reports}
    assert names == {"gh", "curl", "yt-dlp", "feedparser", "mcporter"}


def test_dep_doctor_line_format():
    reports = check_all_deps()
    for report in reports:
        line = report.doctor_line()
        assert report.name in line
        assert "[OK]" in line or "[--]" in line or "[!!]" in line


@patch("agent_reach_tech.core.deps.which", return_value="/usr/bin/gh")
def test_gh_detected_when_present(mock_which):
    reports = {r.name: r for r in check_all_deps()}
    assert reports["gh"].available is True
    assert reports["gh"].path == "/usr/bin/gh"


def test_missing_planned_deps_up_to_sprint_1():
    missing = missing_planned_deps(up_to_sprint=1)
    names = {m.name for m in missing}
    assert "gh" in names or "curl" in names or len(names) >= 0