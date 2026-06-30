from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch

from agent_reach_tech.core.subprocess_runner import run_command, which


def test_run_command_success():
    mock_result = MagicMock(returncode=0, stdout="ok\n", stderr="")
    with patch("agent_reach_tech.core.subprocess_runner.subprocess.run", return_value=mock_result):
        result = run_command([sys.executable, "-c", "print('ok')"])
    assert result.success is True
    assert result.stdout == "ok\n"


def test_run_command_failure():
    mock_result = MagicMock(returncode=1, stdout="", stderr="error")
    with patch("agent_reach_tech.core.subprocess_runner.subprocess.run", return_value=mock_result):
        result = run_command(["false"])
    assert result.success is False
    assert result.stderr == "error"


def test_which_delegates_to_shutil():
    with patch("agent_reach_tech.core.subprocess_runner.shutil.which", return_value="/bin/gh") as mock:
        assert which("gh") == "/bin/gh"
        mock.assert_called_once_with("gh")