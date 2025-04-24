# backend/src/utils/elo_engine.py
import numpy as np
import pandas as pd
from .data_loader import results, races, drivers

K_FACTOR = 32
BASE_ELO = 1500

def _expected(ra: float, rb: float) -> float:
    """Standard ELO expected score of A vs B."""
    return 1.0 / (1 + 10 ** ((rb - ra) / 400))

def _score(pos_a: int, pos_b: int) -> float:
    """Head-to-head score: if A beat B, score=1; if tied, 0.5; else 0."""
    if pos_a < pos_b:
        return 1.0
    elif pos_a == pos_b:
        return 0.5
    else:
        return 0.0

def _update_race_elos(season: int, prev_elos: dict, race_id: int) -> dict:
    """
    Given a dict driver_code→prev_elo, run one race’s ELO update
    and return updated dict.
    """
    df_res = results()
    # gather only this race results, merge on driver code
    race_df = df_res[df_res["raceId"] == race_id].merge(
        drivers()[["driverId","code"]],
        left_on="driverId", right_on="driverId"
    )
    # build positions dict
    pos = {row["code"]: row["position"] for _, row in race_df.iterrows()}
    participants = list(pos.keys())
    deltas = {d: 0.0 for d in participants}

    # pairwise updates
    for i, a in enumerate(participants):
        for b in participants[i+1:]:
            ea = _expected(prev_elos[a], prev_elos[b])
            sa = _score(pos[a], pos[b])
            eb = 1 - ea
            sb = 1 - sa
            deltas[a] += K_FACTOR * (sa - ea)
            deltas[b] += K_FACTOR * (sb - eb)

    # apply deltas
    new_elos = prev_elos.copy()
    for d in participants:
        new_elos[d] = prev_elos[d] + deltas[d]
    return new_elos

def compute_career_elo(driver_code: str, season: int = 2021) -> pd.DataFrame:
    """
    Returns DataFrame: ['race_id','date','elo'] steps through each round.
    """
    # init all drivers to base
    all_codes = drivers()["code"].unique()
    elos = {c: BASE_ELO for c in all_codes}

    # filter races for season
    season_races = (
        races()[races()["year"] == season]
        .sort_values("date")[["raceId","date"]]
        .to_dict(orient="records")
    )

    records = []
    for r in season_races:
        elos = _update_race_elos(season, elos, r["raceId"])
        records.append({
            "race_id": r["raceId"],
            "date": r["date"],
            "elo": elos.get(driver_code, BASE_ELO)
        })

    return pd.DataFrame(records)

def compute_season_overview(season: int = 2021) -> pd.DataFrame:
    """
    Final ELO for all drivers + tier group + bubble‐chart size.
    """
    # run full season
    df = compute_career_elo  # alias
    final = []
    for code in drivers()["code"].unique():
        hist = compute_career_elo(code, season)
        final.append({"code": code, "final_elo": hist["elo"].iloc[-1]})
    df_final = pd.DataFrame(final).sort_values("final_elo", ascending=False)

    # assign quartile tiers
    df_final["tier"] = pd.qcut(df_final["final_elo"], 4, labels=["D","C","B","A"])
    # bubble size ~ wins in season
    win_counts = (
        results()[results()["position"] == 1]
        .merge(races()[["raceId","year"]], on="raceId")
        .query("year==@season")
        .groupby("driverId").size()
    )
    # map driverId->code
    id2code = {r["driverId"]: r["code"] for _, r in drivers().iterrows()}
    df_final["wins"] = df_final["code"].map(
        lambda c: win_counts.get(
            next(k for k,v in id2code.items() if v==c), 0
        )
    )
    df_final["bubble"] = df_final["wins"] * 5 + 10
    return df_final.reset_index(drop=True)

