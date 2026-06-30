from __future__ import annotations

import json
import urllib.error
import urllib.request
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, ClassVar

from agent_reach_tech import __version__

DEFAULT_USER_AGENT = f"agent-reach-tech/{__version__}"


@dataclass(frozen=True)
class ChannelStatus:
    name: str
    available: bool
    message: str
    backend: str = ""
    category: str = "tech"

    def doctor_line(self) -> str:
        icon = "OK" if self.available else "!!"
        backend = f" [{self.backend}]" if self.backend else ""
        return f"  [{icon}] {self.name}{backend}: {self.message}"


class Channel(ABC):
    name: ClassVar[str] = "base"
    backend: ClassVar[str] = ""
    category: ClassVar[str] = "tech"
    optional: ClassVar[bool] = False

    @abstractmethod
    def probe(self) -> ChannelStatus:
        ...

    def _default_headers(self, extra: dict[str, str] | None = None) -> dict[str, str]:
        headers = {"User-Agent": DEFAULT_USER_AGENT}
        if extra:
            headers.update(extra)
        return headers

    def http_get_json(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        timeout: int = 20,
    ) -> Any:
        req = urllib.request.Request(url, headers=self._default_headers(headers))
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def http_get_text(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        timeout: int = 20,
    ) -> str:
        req = urllib.request.Request(url, headers=self._default_headers(headers))
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8")

    def http_post_json(
        self,
        url: str,
        payload: dict[str, Any],
        headers: dict[str, str] | None = None,
        timeout: int = 20,
    ) -> Any:
        body = json.dumps(payload).encode("utf-8")
        req_headers = self._default_headers(headers)
        req_headers.setdefault("Content-Type", "application/json")
        req = urllib.request.Request(url, data=body, headers=req_headers, method="POST")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def safe_probe(self) -> ChannelStatus:
        try:
            status = self.probe()
            if not status.category:
                return ChannelStatus(
                    name=status.name,
                    available=status.available,
                    message=status.message,
                    backend=status.backend,
                    category=self.category,
                )
            return status
        except urllib.error.URLError as e:
            return ChannelStatus(
                self.name,
                False,
                f"Network error: {e.reason}",
                self.backend,
                self.category,
            )
        except Exception as e:  # noqa: BLE001 — doctor must not crash
            return ChannelStatus(self.name, False, str(e), self.backend, self.category)