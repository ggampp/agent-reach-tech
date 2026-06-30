from __future__ import annotations

from agent_reach_tech.channels.base import Channel, ChannelStatus
from agent_reach_tech.channels.registry import (
    channel_names,
    get_all_channels,
    get_channel,
    probe_all,
    register_channel,
    reset_registry,
)


class _TempChannel(Channel):
    name = "temp_test"
    backend = "mock"

    def probe(self) -> ChannelStatus:
        return ChannelStatus(self.name, True, "mock ok", self.backend, "test")


def test_get_all_channels_includes_all_ten():
    names = {ch.name for ch in get_all_channels()}
    assert names == {
        "github",
        "web",
        "youtube",
        "rss",
        "exa_search",
        "reddit",
        "hackernews",
        "lobsters",
        "cve_nvd",
        "osv",
    }


def test_get_channel_by_name():
    ch = get_channel("hackernews")
    assert ch is not None
    assert ch.name == "hackernews"


def test_channel_names_order():
    names = channel_names()
    assert "hackernews" in names
    assert len(names) >= 10


def test_register_channel_extends_registry():
    reset_registry()
    register_channel(_TempChannel)
    names = channel_names()
    assert "temp_test" in names
    ch = get_channel("temp_test")
    assert ch is not None


def test_probe_all_returns_status_per_channel():
    statuses = probe_all()
    assert len(statuses) == len(get_all_channels())
    assert all(s.name for s in statuses)