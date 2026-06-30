from __future__ import annotations

import json
from io import StringIO
from unittest.mock import patch

from agent_reach_tech.cli import main


def test_route_command_json(capsys):
    code = main(["route", "analisar", "CVE-2024-9999", "--json"])
    assert code == 0
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["intent"] == "analyze_cve"


@patch("agent_reach_tech.research.evaluate_oss")
def test_research_oss_command(mock_eval, capsys):
    mock_eval.return_value = {"topic": "engram", "report": "## Pesquisa: engram", "evidence": []}
    code = main(["research", "oss", "engram", "--report"])
    assert code == 0
    assert "Pesquisa: engram" in capsys.readouterr().out


def test_format_command_from_json_string(capsys):
    payload = json.dumps(
        {
            "topic": "test",
            "summary": "ok",
            "evidence": [],
            "verdict": "observar",
            "reason": "test",
        }
    )
    code = main(["format", "--json", payload])
    assert code == 0
    assert "## Pesquisa: test" in capsys.readouterr().out