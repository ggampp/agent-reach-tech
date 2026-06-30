from __future__ import annotations

import urllib.error

from agent_reach_tech.channels.base import Channel, ChannelStatus


class _BrokenChannel(Channel):
    name = "broken"
    backend = "test"

    def probe(self) -> ChannelStatus:
        raise urllib.error.URLError("timeout")


class _OkChannel(Channel):
    name = "ok"
    backend = "test-backend"

    def probe(self) -> ChannelStatus:
        return ChannelStatus("ok", True, "works", "test-backend", "tech")


def test_channel_status_doctor_line_ok():
    status = ChannelStatus("hackernews", True, "reachable", "Algolia", "tech")
    line = status.doctor_line()
    assert "[OK]" in line
    assert "hackernews" in line
    assert "Algolia" in line


def test_channel_status_doctor_line_fail():
    status = ChannelStatus("web", False, "down", "", "base")
    assert "[!!]" in status.doctor_line()


def test_safe_probe_handles_network_error():
    status = _BrokenChannel().safe_probe()
    assert status.available is False
    assert "Network error" in status.message


def test_safe_probe_success():
    status = _OkChannel().safe_probe()
    assert status.available is True
    assert status.backend == "test-backend"