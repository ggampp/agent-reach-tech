from __future__ import annotations

import pytest

from agent_reach_tech.channels.registry import reset_registry


@pytest.fixture(autouse=True)
def _reset_channel_cache():
    reset_registry(restore_defaults=True)
    yield
    reset_registry(restore_defaults=True)