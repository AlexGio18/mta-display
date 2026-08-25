import csv
import io
import zipfile

import requests
from models.station import Station

class GtfsStationRepository:
    GTFS_URL = "https://rrgtfsfeeds.s3.amazonaws.com/gtfs_subway.zip"

 
    def __init__(self):
        self.stops = []

    def load(self):
        response = requests.get(
            self.GTFS_URL,
            timeout=30
        )

        response.raise_for_status()

        with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
            with archive.open("stops.txt") as file:
                text_file = io.TextIOWrapper(
                    file,
                    encoding="utf-8"
                )

                reader = csv.DictReader(text_file)

                self.stops = list(reader)

    def find_station(self, name: str) -> Station | None:
        station = next(
            (
                stop
                for stop in self.stops
                if stop["stop_name"].lower() == name.lower()
                and stop["location_type"] == "1"
            ),
            None
        )

        if station is None:
            return None

        station_id = station["stop_id"]

        child_stops = [
            stop
            for stop in self.stops
            if stop["parent_station"] == station_id
        ]

        stop_ids = [
            stop["stop_id"]
            for stop in child_stops
            if stop["location_type"] in ("", "0")
        ]

        return Station(
            id=station_id,
            name=station["stop_name"],
            latitude=float(station["stop_lat"]),
            longitude=float(station["stop_lon"]),
            stop_ids=stop_ids
        )