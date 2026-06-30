from __future__ import annotations

import json
from typing import Any

from agent_reach_tech.core.subprocess_runner import run_command, which

from .base import Channel, ChannelStatus


class YouTubeChannel(Channel):
    name = "youtube"
    backend = "yt-dlp"
    category = "base"

    def _ytdlp(self) -> str | None:
        return which("yt-dlp") or which("yt_dlp")

    def probe(self) -> ChannelStatus:
        ytdlp = self._ytdlp()
        if not ytdlp:
            return ChannelStatus(
                self.name,
                False,
                "yt-dlp not installed — pip install yt-dlp",
                self.backend,
                self.category,
            )
        result = run_command([ytdlp, "--version"], timeout=10)
        if not result.success:
            return ChannelStatus(self.name, False, result.stderr.strip(), self.backend, self.category)
        version = result.stdout.strip().splitlines()[0] if result.stdout else "yt-dlp"
        return ChannelStatus(self.name, True, version, self.backend, self.category)

    def info(self, url: str) -> dict[str, Any]:
        ytdlp = self._require_ytdlp()
        result = run_command(
            [ytdlp, "--dump-json", "--skip-download", url],
            timeout=90,
        )
        if not result.success:
            raise RuntimeError(result.stderr.strip() or "yt-dlp failed")
        data = json.loads(result.stdout)
        return {
            "id": data.get("id"),
            "title": data.get("title"),
            "url": data.get("webpage_url") or url,
            "channel": data.get("channel"),
            "duration": data.get("duration"),
            "view_count": data.get("view_count"),
            "upload_date": data.get("upload_date"),
            "description": (data.get("description") or "")[:500],
            "subtitles": list((data.get("subtitles") or {}).keys())[:10],
            "automatic_captions": list((data.get("automatic_captions") or {}).keys())[:5],
        }

    def subtitles(self, url: str, lang: str = "en") -> dict[str, Any]:
        ytdlp = self._require_ytdlp()
        result = run_command(
            [
                ytdlp,
                "--skip-download",
                "--write-auto-sub",
                "--sub-lang",
                lang,
                "--print",
                "%(title)s",
                url,
            ],
            timeout=90,
        )
        sub_result = run_command(
            [ytdlp, "--dump-json", "--skip-download", "--print", "automatic_captions", url],
            timeout=60,
        )
        captions: dict[str, Any] = {}
        if sub_result.success and sub_result.stdout.strip():
            try:
                meta = json.loads(run_command([ytdlp, "--dump-json", "--skip-download", url], timeout=90).stdout)
                auto = meta.get("automatic_captions") or {}
                if lang in auto and auto[lang]:
                    captions = {"lang": lang, "formats": [c.get("ext") for c in auto[lang][:3]]}
            except (json.JSONDecodeError, RuntimeError):
                pass
        return {
            "url": url,
            "lang": lang,
            "status": "ok" if result.success else "partial",
            "message": result.stderr.strip() or result.stdout.strip(),
            "captions": captions,
            "hint": "Use agent-reach-tech web for transcript pages or yt-dlp --write-subs locally",
        }

    def search(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        ytdlp = self._require_ytdlp()
        result = run_command(
            [ytdlp, f"ytsearch{limit}:{query}", "--dump-json", "--flat-playlist"],
            timeout=90,
        )
        if not result.success:
            raise RuntimeError(result.stderr.strip() or "yt-dlp search failed")
        items = []
        for line in result.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            items.append(
                {
                    "id": entry.get("id"),
                    "title": entry.get("title"),
                    "url": entry.get("url") or f"https://www.youtube.com/watch?v={entry.get('id')}",
                    "duration": entry.get("duration"),
                    "channel": entry.get("channel") or entry.get("uploader"),
                }
            )
        return items

    def _require_ytdlp(self) -> str:
        ytdlp = self._ytdlp()
        if not ytdlp:
            raise RuntimeError("yt-dlp not installed")
        return ytdlp