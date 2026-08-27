from datetime import datetime, timedelta

from backend.gtfs_station_repository import GtfsStationRepository
from backend.mta_client import MtaClient
from backend.models.departure_board import DepartureBoard
from backend.models.departure import Departure
from backend.models.station import Station


class DepartureService:
    ROUTE_FEEDS = {
        "B": "bdfm",
        "Q": "nqrw",
        "S": "si",
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

        now = datetime.now().astimezone()
        minimum_arrival_time = now + timedelta(seconds=30)

        # Get the unique feeds required for this station.
        feed_names = list(
            set(self.ROUTE_FEEDS.values())
        )

        # Fetch each feed once.
        feeds = self.mta_client.get_feeds(
            feed_names
        )

        feed_timestamps = [
            feed.header.timestamp
            for feed in feeds.values()
            if feed.header.HasField("timestamp")
        ]

        feed_updated_at = datetime.fromtimestamp(
            max(feed_timestamps)
        ).astimezone()

        for route, feed_name in self.ROUTE_FEEDS.items():
            feed = feeds[feed_name]

            # print(feed.entity)
            for entity in feed.entity:

                if not entity.HasField("trip_update"):
                    continue

                trip_update = entity.trip_update
                trip = trip_update.trip

                if trip.route_id != route:
                    continue

                # Find the static GTFS information for this trip.
                trip_info = self.station_repository.get_trip(
                    trip.trip_id
                )
                if trip_info is None:
                    print(
                        f"Could not find static trip for "
                        f"realtime trip ID: {trip.trip_id}"
                    )
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

                    delay_seconds = 0

                    if stop_update.arrival.HasField("delay"):
                        delay_seconds = stop_update.arrival.delay

                    if arrival_time < minimum_arrival_time:
                        continue

                    direction = self._get_direction(
                        trip_info.direction_id
                    )

                    departures.append(
                        Departure(
                            route=route,
                            destination=trip_info.headsign,
                            direction=direction,
                            arrival_time=arrival_time,
                            delay_seconds=delay_seconds
                        )
                    )

        departures.sort(
            key=lambda departure: departure.arrival_time
        )

        return DepartureBoard(
            feed_updated_at=feed_updated_at,
            retrieved_at=now,
            departures=departures[:limit]
        )
    
    @staticmethod
    def _get_direction(
        direction_id: str
    ) -> str:

        if direction_id.__eq__("0"):
            return "Manhattan-bound"

        if direction_id.endswith("1"):
            return "Brooklyn-bound"

        return direction_id