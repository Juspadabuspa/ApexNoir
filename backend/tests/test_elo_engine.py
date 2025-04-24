# backend/tests/test_elo_engine.py

import pytest
import pandas as pd

from backend.src.utils.elo_engine import (
    _expected,
    _score,
    _update_race_elos,
    compute_career_elo,
    K_FACTOR,
)

def test_expected_equal_ratings():
    # Two equal ratings should give an expected score of 0.5
    assert _expected(1500, 1500) == pytest.approx(0.5)

def test_expected_unequal_ratings():
    # Higher rating vs lower rating => expected > 0.5
    e_high = _expected(1600, 1400)
    e_low = _expected(1400, 1600)
    assert e_high > 0.5
    assert e_low < 0.5
    # And they should sum to ~1
    assert e_high + e_low == pytest.approx(1.0)

def test_score_win_tie_loss():
    # If pos_a < pos_b, A wins → 1.0
    assert _score(1, 2) == 1.0
    # Tie → 0.5
    assert _score(1, 1) == 0.5
    # Loss → 0.0
    assert _score(2, 1) == 0.0

def test_update_race_elos(monkeypatch):
    # Prepare a fake drivers() and results() for a single race with two drivers
    drivers_df = pd.DataFrame({
        "driverId": [1, 2],
        "code": ["A", "B"]
    })
    results_df = pd.DataFrame({
        "raceId": [100, 100],
        "driverId": [1, 2],
        "position": [1, 2]
    })

    # Monkeypatch the data sources inside elo_engine
    monkeypatch.setattr(
        "backend.src.utils.elo_engine.drivers",
        lambda: drivers_df
    )
    monkeypatch.setattr(
        "backend.src.utils.elo_engine.results",
        lambda: results_df
    )

    prev_elos = {"A": 1500.0, "B": 1500.0}
    new_elos = _update_race_elos(season=2021, prev_elos=prev_elos, race_id=100)

    # Expected delta: K_FACTOR * (score - expected) = 32 * (1 - 0.5) = +16 for A
    assert new_elos["A"] == pytest.approx(1500.0 + K_FACTOR * 0.5)
    assert new_elos["B"] == pytest.approx(1500.0 - K_FACTOR * 0.5)

def test_compute_career_elo_single_race(monkeypatch):
    # 1) races() has one race in 2021
    races_df = pd.DataFrame({
        "raceId": [100],
        "year": [2021],
        "date": ["2021-03-28"]
    })
    monkeypatch.setattr(
        "backend.src.utils.elo_engine.races",
        lambda: races_df
    )

    # 2) drivers() lists TWO drivers, A and B
    drivers_df = pd.DataFrame({
        "driverId": [1, 2],
        "code": ["A", "B"]
    })
    monkeypatch.setattr(
        "backend.src.utils.elo_engine.drivers",
        lambda: drivers_df
    )

    # 3) results() has TWO rows: A finished 1st, B finished 2nd
    results_df = pd.DataFrame({
        "raceId": [100, 100],
        "driverId": [1, 2],
        "position": [1, 2]
    })
    monkeypatch.setattr(
        "backend.src.utils.elo_engine.results",
        lambda: results_df
    )

    # Now compute career elo for A
    df = compute_career_elo("A", season=2021)

    # It should be a DataFrame with exactly one row
    assert isinstance(df, pd.DataFrame)
    assert df.shape[0] == 1

    row = df.iloc[0]
    assert row["race_id"] == 100
    assert row["date"] == "2021-03-28"

    # Elo change: 1500 + K*(1 - 0.5) = 1500 + 32*0.5 = 1516
    expected_delta = K_FACTOR * (_score(1, 2) - _expected(1500, 1500))
    assert row["elo"] == pytest.approx(1500 + expected_delta)
