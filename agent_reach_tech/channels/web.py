from __future__ import annotations

from typing import Any
from urllib.parse import quote, urlparse

from .base import Channel, ChannelStatus

JINA_READER = "https://r.jina.ai/"
PROBE_URL = "https://example.com"


def _normalize_url(url: str) -> str:
    url = url.strip()
    if not url:
        raise ValueError("URL is required")
    parsed = urlparse(url)
    if not parsed.scheme:
        url = f"https://{url}"
    return url


def _split_title_body(text: str) -> tuple[str | None, str]:
    lines = text.strip().splitlines()
    if not lines:
        return None, ""
    if lines[0].startswith("Title:"):
        title = lines[0].removeprefix("Title:").strip()
        body = "\n".join(lines[1:]).strip()
        return title or None, body
    return None, text.strip()


class WebChannel(Channel):
    name = "web"
    backend = "Jina Reader"
    category = "base"

    def probe(self) -> ChannelStatus:
        url = self._jina_url(PROBE_URL)
        text = self.http_get_text(url, timeout=15)
        ok = len(text.strip()) > 20
        return ChannelStatus(
            self.name,
            ok,
            "Jina Reader reachable" if ok else "Empty or unexpected response from Jina Reader",
            self.backend,
            self.category,
        )

    def read(self, url: str, *, raw: bool = False) -> dict[str, Any]:
        target = _normalize_url(url)
        jina_url = self._jina_url(target)
        text = self.http_get_text(jina_url, timeout=45)
        if raw:
            return {"url": target, "content": text, "backend": self.backend}
        title, body = _split_title_body(text)
        return {
            "url": target,
            "title": title,
            "content": body,
            "length": len(body),
            "backend": self.backend,
        }

    def _jina_url(self, target: str) -> str:
        return f"{JINA_READER}{quote(target, safe=':/?#[]@!$&\'()*+,;=%')}"