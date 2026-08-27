import csv
import io
import zipfile

import requests
from backend.models.station import Station
from backend.models.trip import Trip

class GtfsStationRepository:
    GTFS_URL = "https://rrgtfsfeeds.s3.amazonaws.com/gtfs_subway.zip"

 
    def __init__(self):
        self.stops = []
        self.trips = {}
        self.realtime_trips = {}

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

            with archive.open("trips.txt") as file:
                text_file = io.TextIOWrapper(
                    file,
                    encoding="utf-8"
                )

                reader = csv.DictReader(text_file)

                for row in reader:
                    trip = Trip(
                        id=row["trip_id"],
                        route_id=row["route_id"],
                        direction_id=row.get("direction_id", ""),
                        headsign=row.get("trip_headsign", "")
                    )

                    self.trips[trip.id] = trip
                    realtime_trip_id = self._get_realtime_trip_id(
                        trip.id
                    )

                    if realtime_trip_id:
                        self.realtime_trips[realtime_trip_id] = trip

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

    def get_trip(self, realtime_trip_id: str) -> Trip | None:
        trip = self.realtime_trips.get(realtime_trip_id)

        if trip is not None:
            return trip

        # Fallback for MTA trip ID formatting differences.
        for static_trip_id, trip in self.trips.items():
            if static_trip_id.endswith(realtime_trip_id):
                return trip

        return None

    @staticmethod
    def _get_realtime_trip_id(trip_id: str) -> str | None:
        parts = trip_id.split("_", 1)

        if len(parts) != 2:
            return None

        remainder = parts[1]

        # The realtime ID starts with the numeric trip portion.
        if not remainder or not remainder[0].isdigit():
            return None

        return remainder