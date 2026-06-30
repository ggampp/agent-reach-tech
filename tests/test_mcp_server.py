from __future__ import annotations

import builtins
import importlib.util
from unittest.mock import patch


def test_mcp_server_module_importable():
    spec = importlib.util.find_spec("agent_reach_tech.mcp_server")
    assert spec is not None


def test_run_mcp_without_sdk_returns_error(capsys):
    real_import = builtins.__import__

    def mock_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "mcp.server.fastmcp" or (fromlist and "fastmcp" in fromlist):
            raise ImportError("No module named 'mcp.server.fastmcp'")
        return real_import(name, globals, locals, fromlist, level)

    from agent_reach_tech.mcp_server import run_mcp

    with patch("builtins.__import__", side_effect=mock_import):
        code = run_mcp()
    captured = capsys.readouterr()
    assert code == 1
    assert "MCP SDK" in captured.err