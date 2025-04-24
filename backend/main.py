# backend/main.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.src.utils.data_loader import _load_all_csvs
from backend.src.utils.elo_engine import compute_career_elo, compute_season_overview
from backend.src.utils.rivalries_utils import compute_rivalries
from backend.src.utils.team_stats_utils import team_match_elo_timeline, team_win_rate

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan handler to preload data on startup.
    """
    _load_all_csvs()   # cache all CSVs
    yield               # application runs after this point
    # no shutdown logic needed

app = FastAPI(
    title="Black & Gold F1 Analytics API",
    lifespan=lifespan
)

# Enable CORS for your frontend (adjust origin as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

@app.get("/drivers/{code}/elo")
def driver_elo(code: str, season: int = 2021):
    """
    Return a driver’s career ELO history for the given season.
    """
    result = compute_career_elo(code, season)

    # Handle both real DataFrame and test‐stubbed list
    if isinstance(result, list):
        data = result
    else:
        if result.empty:
            raise HTTPException(status_code=404, detail="Driver or season not found")
        data = result.to_dict(orient="records")

    if not data:
        raise HTTPException(status_code=404, detail="Driver or season not found")
    return data

@app.get("/season/{year}/overview")
def season_overview(year: int):
    """
    Return final ELO standings, tier groups, and bubble‐chart data for the season.
    """
    result = compute_season_overview(year)
    # If stubbed as list
    if isinstance(result, list):
        return result
    return result.to_dict(orient="records")

@app.get("/drivers/{code}/rivalries")
def rivalries(code: str, season: int = 2021):
    """
    Return top N rivalries for the given driver in the season.
    """
    result = compute_rivalries(code, season)

    if isinstance(result, list):
        data = result
    else:
        data = [] if result.empty else result.to_dict(orient="records")

    if not data:
        raise HTTPException(status_code=404, detail="No rivalries found")
    return data

@app.get("/teams/{team}/stats")
def team_stats(team: str, season: int = 2021):
    """
    Return match‐by‐match ELO timeline and win‐rate summary for the team.
    """
    tl = team_match_elo_timeline(team, season)
    timeline = tl if isinstance(tl, list) else tl.to_dict(orient="records")
    summary = team_win_rate(team, season)
    return {"timeline": timeline, "summary": summary}
