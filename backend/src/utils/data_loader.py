# backend/src/utils/data_loader.py
import pandas as pd
from functools import lru_cache
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"

@lru_cache(maxsize=1)
def _load_all_csvs():
    dfs = {}
    for csv in DATA_DIR.glob("*.csv"):
        key = csv.stem  # e.g. 'drivers', 'results', etc.
        dfs[key] = pd.read_csv(csv)
    return dfs

def get_df(name: str) -> pd.DataFrame:
    dfs = _load_all_csvs()
    if name not in dfs:
        raise KeyError(f"No CSV named '{name}.csv'")
    return dfs[name]

# Convenience getters:
def drivers() -> pd.DataFrame:
    return get_df("drivers")

def results() -> pd.DataFrame:
    return get_df("results")

def races() -> pd.DataFrame:
    return get_df("races")

def constructors() -> pd.DataFrame:
    return get_df("constructors")

def constructor_results() -> pd.DataFrame:
    return get_df("constructor_results")

def qualifying() -> pd.DataFrame:
    return get_df("qualifying")

def lap_times() -> pd.DataFrame:
    return get_df("lap_times")

def seasons() -> pd.DataFrame:
    return get_df("seasons")

def circuits() -> pd.DataFrame:
    return get_df("circuits")

def pit_stops() -> pd.DataFrame:
    return get_df("pit_stops")

def status() -> pd.DataFrame:
    return get_df("status")

def driver_standings() -> pd.DataFrame:
    return get_df("driver_standings")

def constructor_standings() -> pd.DataFrame:
    return get_df("constructor_standings")

def sprint_results() -> pd.DataFrame:
    return get_df("sprint_results")

