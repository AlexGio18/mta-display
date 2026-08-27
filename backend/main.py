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
    print(f"Upcoming departures from {station.name}:")
    print()

    for departure in departures:
        print(
            f"{departure.route:>2} | "
            f"{departure.direction:<11} | "
            f"{departure.destination:<20} | "
            f"{departure.minutes_until:>2} min | "
            f"{departure.arrival_time.strftime('%I:%M:%S %p')}"
        )


if __name__ == "__main__":
    main()