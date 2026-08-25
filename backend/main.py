from departure_service import DepartureService
from gtfs_station_repository import GtfsStationRepository
from mta_client import MtaClient


def main():
    station_repository = GtfsStationRepository()

    print("Downloading GTFS data...")
    station_repository.load()

    station = station_repository.find_station("Prospect Park")

    if station is None:
        print("Station not found")
        return

    print()
    print(f"Station: {station.name}")
    print(f"Stop IDs: {station.stop_ids}")

    mta_client = MtaClient()

    departure_service = DepartureService(
        mta_client,
        station_repository
    )

    departures = departure_service.get_departures(
        station,
        limit=10
    )

    print()
    print("Upcoming departures:")
    print()

    for departure in departures:
        print(
            f"{departure.route} "
            f"{departure.minutes_until} min "
            f"({departure.stop_id}) "
            f"{departure.arrival_time.strftime('%I:%M:%S %p')}"
        )


if __name__ == "__main__":
    main()