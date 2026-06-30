from __future__ import annotations

from typing import Any

from .base import Channel, ChannelStatus

OSV_API = "https://api.osv.dev/v1"


class OsvChannel(Channel):
    name = "osv"
    backend = "OSV.dev API"

    ECOSYSTEM_MAP = {
        "npm": "npm",
        "pypi": "PyPI",
        "python": "PyPI",
        "go": "Go",
        "cargo": "crates.io",
        "rust": "crates.io",
        "maven": "Maven",
        "nuget": "NuGet",
    }

    def probe(self) -> ChannelStatus:
        payload = {"package": {"name": "lodash", "ecosystem": "npm"}}
        result = self._post("/query", payload)
        ok = "vulns" in result
        return ChannelStatus(
            self.name,
            ok,
            "OSV.dev API reachable" if ok else "Unexpected OSV response",
            self.backend,
        )

    def query_package(self, ecosystem: str, package: str) -> dict[str, Any]:
        eco = self.ECOSYSTEM_MAP.get(ecosystem.lower(), ecosystem)
        result = self._post("/query", {"package": {"name": package, "ecosystem": eco}})
        vulns = result.get("vulns", [])
        return {
            "ecosystem": eco,
            "package": package,
            "count": len(vulns),
            "vulnerabilities": [_format_vuln(v) for v in vulns[:20]],
        }

    def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self.http_post_json(f"{OSV_API}{path}", payload)


def _format_vuln(v: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": v.get("id"),
        "summary": v.get("summary"),
        "severity": v.get("severity"),
        "published": v.get("published"),
        "modified": v.get("modified"),
        "references": [r.get("url") for r in v.get("references", []) if r.get("url")][:5],
        "affected": v.get("affected", [])[:3],
    }