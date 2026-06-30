from __future__ import annotations

from unittest.mock import patch

from agent_reach_tech.channels.base import ChannelStatus
from unittest.mock import MagicMock

from agent_reach_tech.doctor import run_doctor


def _mock_channel(name: str, ok: bool, *, optional: bool = False, category: str = "tech"):
    ch = MagicMock()
    ch.name = name
    ch.optional = optional
    ch.safe_probe.return_value = ChannelStatus(name, ok, "ok", "b", category)
    return ch


@patch("agent_reach_tech.doctor.get_all_channels")
def test_run_doctor_required_failure(mock_channels):
    mock_channels.return_value = [
        _mock_channel("github", True, category="base"),
        _mock_channel("cve_nvd", False),
    ]
    assert run_doctor() == 1


@patch("agent_reach_tech.doctor.get_all_channels")
def test_run_doctor_optional_failure_ok(mock_channels):
    mock_channels.return_value = [
        _mock_channel("github", True, category="base"),
        _mock_channel("exa_search", False, optional=True, category="base"),
    ]
    assert run_doctor() == 0