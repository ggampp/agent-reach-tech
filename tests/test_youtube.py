from __future__ import annotations

import json
from unittest.mock import patch

from agent_reach_tech.channels.youtube import YouTubeChannel
from agent_reach_tech.core.subprocess_runner import RunResult


def _ok(stdout: str) -> RunResult:
    return RunResult(["yt-dlp"], 0, stdout, "")


@patch("agent_reach_tech.channels.youtube.which", return_value=None)
def test_probe_without_ytdlp(_):
    assert YouTubeChannel().probe().available is False


@patch("agent_reach_tech.channels.youtube.run_command")
@patch("agent_reach_tech.channels.youtube.which", return_value="/bin/yt-dlp")
def test_info(mock_which, mock_run):
    mock_run.return_value = _ok(json.dumps({"id": "abc", "title": "Test", "webpage_url": "https://youtu.be/abc"}))
    data = YouTubeChannel().info("https://youtu.be/abc")
    assert data["title"] == "Test"