# backend/src/utils/team_stats_utils.py
import pandas as pd
from .elo_engine import compute_career_elo
from .data_loader import results, races, drivers, constructors, constructor_results

def team_match_elo_timeline(team_name: str, season: int = 2021) -> pd.DataFrame:
    """
    Returns one row per race: {'race_id','date','avg_elo'} for
    all drivers in that constructor.
    """
    # find constructorId
    cons = constructors()
    cid = cons[cons["name"] == team_name]["constructorId"].squeeze()
    # driver membership via constructor_results
    cr = constructor_results()
    drs = cr[(cr["constructorId"]==cid) & (cr["year"]==season)]["driverId"].unique()
    codes = drivers()[drivers()["driverId"].isin(drs)]["code"].tolist()

    rows = []
    for c in codes:
        hist = compute_career_elo(c, season)
        hist = hist.rename(columns={"elo": c})
        rows.append(hist.set_index("race_id")[c])
    # combine and average
    df = pd.concat(rows, axis=1).mean(axis=1).reset_index()
    # bring back date
    dates = compute_career_elo(codes[0], season)[["race_id","date"]]
    return df.merge(dates, on="race_id")

def team_win_rate(team_name: str, season: int = 2021) -> dict:
    """
    Returns {'wins': X, 'podiums': Y, 'starts': Z, 'win_rate': ..., 'podium_rate': ...}
    """
    cr = constructor_results()
    cons = cr[(cr["name"]==team_name) & (cr["year"]==season)]
    starts = len(cons)
    wins = len(cons[cons["position"] == 1])
    podiums = len(cons[cons["position"].isin([1,2,3])])
    return {
        "starts": starts,
        "wins": wins,
        "podiums": podiums,
        "win_rate": wins / starts if starts else 0,
        "podium_rate": podiums / starts if starts else 0
    }
