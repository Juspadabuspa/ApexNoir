# backend/tests/test_season_overview.py
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_season_overview_success(monkeypatch):
    # fake 2021 overview
    fake_overview = [
        {"code": "ham", "final_elo": 1620, "tier": "A", "wins": 5, "bubble": 35},
        {"code": "ver", "final_elo": 1580, "tier": "B", "wins": 3, "bubble": 25},
    ]
    monkeypatch.setattr("backend.main.compute_season_overview", lambda year: fake_overview)

    resp = client.get("/season/2021/overview")
    assert resp.status_code == 200
    assert resp.elapsed.total_seconds() < 0.25
    assert resp.json() == fake_overview
