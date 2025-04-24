# backend/tests/test_rivalries.py
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_rivalries_success(monkeypatch):
    fake_rivals = [
        {"rival": "ver", "races_together": 10, "head2head_win%": 0.6},
        {"rival": "lec", "races_together": 10, "head2head_win%": 0.4},
    ]
    monkeypatch.setattr("backend.main.compute_rivalries", lambda code, season: fake_rivals)

    resp = client.get("/drivers/ham/rivalries?season=2021")
    assert resp.status_code == 200
    assert resp.elapsed.total_seconds() < 0.25
    assert resp.json() == fake_rivals

def test_rivalries_not_found(monkeypatch):
    monkeypatch.setattr("backend.main.compute_rivalries", lambda code, season: [])
    resp = client.get("/drivers/ham/rivalries")
    assert resp.status_code == 404
    assert "no rivalries" in resp.json()["detail"].lower()
