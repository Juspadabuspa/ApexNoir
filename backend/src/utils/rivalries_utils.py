# backend/src/utils/rivalries_utils.py
import pandas as pd
from .data_loader import results, races, drivers

def compute_rivalries(driver_code: str, season: int = 2021, top_n: int = 5) -> pd.DataFrame:
    """
    Returns the top N rivals by head-to-head win %
    and average ELO swing when they meet.
    """
    # get all race IDs in season
    rids = races().query("year==@season")["raceId"].tolist()
    df = results().merge(drivers()[["driverId","code"]], on="driverId")
    df = df[df["raceId"].isin(rids)]
    # filter rows for our driver
    me = df[df["code"] == driver_code]
    others = df[df["code"] != driver_code]

    records = {}
    for _, my_row in me.iterrows():
        rid = my_row["raceId"]
        pos_me = my_row["position"]
        opponents = others[others["raceId"] == rid]
        for _, opp in opponents.iterrows():
            key = opp["code"]
            records.setdefault(key, {"me_wins":0,"me_total":0})
            records[key]["me_total"] += 1
            if pos_me < opp["position"]:
                records[key]["me_wins"] += 1

    # build DataFrame
    out = []
    for rival, stats in records.items():
        out.append({
            "rival": rival,
            "races_together": stats["me_total"],
            "head2head_win%": stats["me_wins"] / stats["me_total"]
        })
    df_out = pd.DataFrame(out).sort_values("head2head_win%", ascending=False)
    return df_out.head(top_n).reset_index(drop=True)
