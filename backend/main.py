from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.departure_service import DepartureService
from backend.gtfs_station_repository import GtfsStationRepository
from backend.mta_client import MtaClient


app = FastAPI(
    title="MTA Train Display API",
    version="1.0.0"
)

# ---------------------------------------------------------
# Services
# ---------------------------------------------------------

station_repository = GtfsStationRepository()
mta_client = MtaClient()

departure_service = DepartureService(
    mta_client,
    station_repository
)

# ---------------------------------------------------------
# Frontend
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"


# Serve frontend static files
app.mount(
    "/static",
    StaticFiles(directory=FRONTEND_DIR),
    name="static"
)


# ---------------------------------------------------------
# Startup
# ---------------------------------------------------------

@app.on_event("startup")
def startup():
    print("Loading GTFS data...")

    station_repository.load()

    print("GTFS data loaded.")


# ---------------------------------------------------------
# Frontend
# ---------------------------------------------------------

@app.get("/")
def serve_frontend():

    return FileResponse(
        FRONTEND_DIR / "index.html"
    )


# ---------------------------------------------------------
# API
# ---------------------------------------------------------

@app.get("/api/stations/prospect-park/departures")
def get_prospect_park_departures():
    station = station_repository.find_station(
        "Prospect Park"
    )

    if station is None:
        raise HTTPException(
            status_code=404,
            detail="Prospect Park station not found"
        )

    board = departure_service.get_departures(
        station,
        limit=20
    )

    return {
        "station": station.name,
        "updated_at": board.feed_updated_at,
        "departures": [
            {
                "route": departure.route,
                "destination": departure.destination,
                "direction": departure.direction,
                "arrival_time": departure.arrival_time,
                "minutes": departure.minutes_until,
                "delay_seconds": departure.delay_seconds,
                "delay_minutes": departure.delay_minutes
            }
            for departure in board.departures
        ]
    }