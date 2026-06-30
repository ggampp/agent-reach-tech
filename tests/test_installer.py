from __future__ import annotations

from agent_reach_tech.core.installer import build_install_report, execute_install_report


def test_build_install_report_has_actions():
    report = build_install_report(env="auto", safe=True, dry_run=True)
    assert len(report.actions) >= 2
    assert report.safe is True


def test_execute_dry_run_skips_commands():
    report = build_install_report(dry_run=True, safe=False)
    report = execute_install_report(report)
    assert all(a.skipped or a.command is None for a in report.actions if a.command)