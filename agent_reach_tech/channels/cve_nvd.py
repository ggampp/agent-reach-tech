from __future__ import annotations

import os
from typing import Any

from .base import Channel, ChannelStatus

NVD_API = "https://services.nvd.nist.gov/rest/json/cves/2.0"


class CveNvdChannel(Channel):
    name = "cve_nvd"
    backend = "NVD API 2.0"

    def _headers(self) -> dict[str, str]:
        headers = {"User-Agent": "agent-reach-tech/0.1"}
        key = os.environ.get("NVD_API_KEY", "").strip()
        if key:
            headers["apiKey"] = key
        return headers

    def probe(self) -> ChannelStatus:
        data = self.http_get_json(f"{NVD_API}?resultsPerPage=1", headers=self._headers())
        total = data.get("totalResults", 0)
        has_key = bool(os.environ.get("NVD_API_KEY"))
        msg = f"NVD API OK ({total} CVEs indexed)"
        if not has_key:
            msg += " — set NVD_API_KEY for higher rate limits"
        return ChannelStatus(self.name, True, msg, self.backend)

    def get_cve(self, cve_id: str) -> dict[str, Any] | None:
        cve_id = cve_id.upper().strip()
        data = self.http_get_json(f"{NVD_API}?cveId={cve_id}", headers=self._headers())
        vulns = data.get("vulnerabilities", [])
        if not vulns:
            return None
        return _format_cve(vulns[0])

    def search(self, keyword: str, limit: int = 10) -> list[dict[str, Any]]:
        from urllib.parse import quote

        q = quote(keyword)
        data = self.http_get_json(
            f"{NVD_API}?keywordSearch={q}&resultsPerPage={limit}",
            headers=self._headers(),
        )
        return [_format_cve(v) for v in data.get("vulnerabilities", [])]


def _format_cve(entry: dict[str, Any]) -> dict[str, Any]:
    cve = entry.get("cve", {})
    cve_id = cve.get("id")
    descriptions = cve.get("descriptions", [])
    desc_en = next((d["value"] for d in descriptions if d.get("lang") == "en"), "")
    metrics = cve.get("metrics", {})
    cvss = _extract_cvss(metrics)
    refs = [r.get("url") for r in cve.get("references", []) if r.get("url")]
    return {
        "id": cve_id,
        "description": desc_en,
        "cvss": cvss,
        "published": cve.get("published"),
        "last_modified": cve.get("lastModified"),
        "references": refs[:10],
        "url": f"https://nvd.nist.gov/vuln/detail/{cve_id}" if cve_id else None,
    }


def _extract_cvss(metrics: dict[str, Any]) -> dict[str, Any] | None:
    for key in ("cvssMetricV31", "cvssMetricV30", "cvssMetricV2"):
        items = metrics.get(key)
        if items:
            data = items[0].get("cvssData", {})
            return {
                "version": data.get("version"),
                "score": data.get("baseScore"),
                "severity": data.get("baseSeverity") or items[0].get("baseSeverity"),
                "vector": data.get("vectorString"),
            }
    return None