# backend/tests/test_driver_elo.py
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_driver_elo_success(monkeypatch):
    # fake a one‐race career ELO history
    fake_data = [{"race_id": 1, "date": "2021-03-28", "elo": 1550}]
    monkeypatch.setattr("backend.main.compute_career_elo", lambda code, season: fake_data)

    resp = client.get("/drivers/ham/elo?season=2021")
    assert resp.status_code == 200
    assert resp.elapsed.total_seconds() < 0.25
    body = resp.json()
    assert isinstance(body, list)
    assert body == fake_data

def test_driver_elo_not_found(monkeypatch):
    # simulate no data → 404
    monkeypatch.setattr("backend.main.compute_career_elo", lambda code, season: [])
    resp = client.get("/drivers/xxx/elo")
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"].lower()
