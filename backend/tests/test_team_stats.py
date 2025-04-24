# backend/tests/test_team_stats.py
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

class FakeDF:
    def __init__(self, data):
        self._data = data
    def to_dict(self, orient):
        assert orient == "records"
        return self._data

def test_team_stats_success(monkeypatch):
    fake_timeline = [{"race_id": 1, "avg_elo": 1505}]
    fake_summary = {"starts": 5, "wins": 2, "podiums": 3, "win_rate": 0.4, "podium_rate": 0.6}

    monkeypatch.setattr("backend.main.team_match_elo_timeline",
                        lambda team, season: FakeDF(fake_timeline))
    monkeypatch.setattr("backend.main.team_win_rate",
                        lambda team, season: fake_summary)

    resp = client.get("/teams/Mercedes/stats?season=2021")
    assert resp.status_code == 200
    assert resp.elapsed.total_seconds() < 0.25

    body = resp.json()
    assert "timeline" in body and "summary" in body
    assert body["timeline"] == fake_timeline
    assert body["summary"] == fake_summary
