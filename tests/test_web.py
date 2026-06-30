from __future__ import annotations

from unittest.mock import patch

import pytest

from agent_reach_tech.channels.web import WebChannel, _normalize_url, _split_title_body


def test_normalize_url_adds_scheme():
    assert _normalize_url("owasp.org") == "https://owasp.org"


def test_normalize_url_requires_value():
    with pytest.raises(ValueError):
        _normalize_url("  ")


def test_split_title_body():
    text = "Title: OWASP\n\nSecurity content"
    title, body = _split_title_body(text)
    assert title == "OWASP"
    assert "Security content" in body


@patch.object(WebChannel, "http_get_text", return_value="Title: Example\n\nHello world")
def test_probe_ok(mock_get):
    status = WebChannel().probe()
    assert status.available is True
    assert status.name == "web"


@patch.object(WebChannel, "http_get_text", return_value="Title: Docs\n\nBody text")
def test_read_parses_title(mock_get):
    result = WebChannel().read("https://owasp.org")
    assert result["url"] == "https://owasp.org"
    assert result["title"] == "Docs"
    assert "Body text" in result["content"]


@patch.object(WebChannel, "http_get_text", return_value="raw markdown")
def test_read_raw(mock_get):
    result = WebChannel().read("owasp.org", raw=True)
    assert result["content"] == "raw markdown"