from datetime import datetime

from gtfs_station_repository import GtfsStationRepository
from mta_client import MtaClient
from models.departure import Departure
from models.station import Station


class DepartureService:
    ROUTE_FEEDS = {
        "B": "bdfm",
        "Q": "nqrw",
        "S": "1234567",
    }

    def __init__(
        self,
        mta_client: MtaClient,
        station_repository: GtfsStationRepository
    ):
        self.mta_client = mta_client
        self.station_repository = station_repository

    def get_departures(
        self,
        station: Station,
        limit: int = 10
    ) -> list[Departure]:

        departures = []

        for route, feed_name in self.ROUTE_FEEDS.items():

            feed = self.mta_client.get_feed(feed_name)

            for entity in feed.entity:

                if not entity.HasField("trip_update"):
                    continue

                trip_update = entity.trip_update

                # Make sure this is the route we're looking for.
                if trip_update.trip.route_id != route:
                    continue

                for stop_update in trip_update.stop_time_update:

                    if stop_update.stop_id not in station.stop_ids:
                        continue

                    if not stop_update.HasField("arrival"):
                        continue

                    arrival_timestamp = stop_update.arrival.time

                    arrival_time = datetime.fromtimestamp(
                        arrival_timestamp
                    ).astimezone()

                    departures.append(
                        Departure(
                            route=route,
                            stop_id=stop_update.stop_id,
                            arrival_time=arrival_time
                        )
                    )

        departures.sort(
            key=lambda departure: departure.arrival_time
        )

        return departures[:limit]