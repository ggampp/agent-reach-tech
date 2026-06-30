from __future__ import annotations

from typing import TypeVar

from .base import Channel, ChannelStatus
from .cve_nvd import CveNvdChannel
from .exa_search import ExaSearchChannel
from .github import GitHubChannel
from .hackernews import HackerNewsChannel
from .lobsters import LobstersChannel
from .osv import OsvChannel
from .reddit import RedditChannel
from .rss import RssChannel
from .web import WebChannel
from .youtube import YouTubeChannel

T = TypeVar("T", bound=type[Channel])

_DEFAULT_CHANNEL_CLASSES: list[type[Channel]] = [
    GitHubChannel,
    WebChannel,
    YouTubeChannel,
    RssChannel,
    ExaSearchChannel,
    RedditChannel,
    HackerNewsChannel,
    LobstersChannel,
    CveNvdChannel,
    OsvChannel,
]

_CHANNEL_CLASSES: list[type[Channel]] = list(_DEFAULT_CHANNEL_CLASSES)

_instances: dict[str, Channel] | None = None


def register_channel(cls: T) -> T:
    if cls not in _CHANNEL_CLASSES:
        _CHANNEL_CLASSES.append(cls)
        reset_registry()
    return cls


def _ensure_instances() -> dict[str, Channel]:
    global _instances
    if _instances is None:
        _instances = {cls.name: cls() for cls in _CHANNEL_CLASSES}
    return _instances


def get_all_channels() -> list[Channel]:
    return list(_ensure_instances().values())


def get_channel(name: str) -> Channel | None:
    return _ensure_instances().get(name)


def probe_all() -> list[ChannelStatus]:
    return [channel.safe_probe() for channel in get_all_channels()]


def reset_registry(*, restore_defaults: bool = False) -> None:
    """Clear cached channel instances. Tests may restore default channel list."""
    global _instances, _CHANNEL_CLASSES
    _instances = None
    if restore_defaults:
        _CHANNEL_CLASSES = list(_DEFAULT_CHANNEL_CLASSES)


def channel_names() -> list[str]:
    return [cls.name for cls in _CHANNEL_CLASSES]