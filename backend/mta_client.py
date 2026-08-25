import requests
from google.transit import gtfs_realtime_pb2


class MtaClient:
    FEEDS = {
        "1234567": (
            "https://api-endpoint.mta.info/"
            "Dataservice/mtagtfsfeeds/nyct%2Fgtfs"
        ),
        "ace": (
            "https://api-endpoint.mta.info/"
            "Dataservice/mtagtfsfeeds/nyct%2Fgtfs-ace"
        ),
        "bdfm": (
            "https://api-endpoint.mta.info/"
            "Dataservice/mtagtfsfeeds/nyct%2Fgtfs-bdfm"
        ),
        "g": (
            "https://api-endpoint.mta.info/"
            "Dataservice/mtagtfsfeeds/nyct%2Fgtfs-g"
        ),
        "jz": (
            "https://api-endpoint.mta.info/"
            "Dataservice/mtagtfsfeeds/nyct%2Fgtfs-jz"
        ),
        "l": (
            "https://api-endpoint.mta.info/"
            "Dataservice/mtagtfsfeeds/nyct%2Fgtfs-l"
        ),
        "nqrw": (
            "https://api-endpoint.mta.info/"
            "Dataservice/mtagtfsfeeds/nyct%2Fgtfs-nqrw"
        ),
        "si": (
            "https://api-endpoint.mta.info/"
            "Dataservice/mtagtfsfeeds/nyct%2Fgtfs-si"
        ),
    }

    def get_feed(self, feed_name: str) -> gtfs_realtime_pb2.FeedMessage:
        if feed_name not in self.FEEDS:
            raise ValueError(f"Unknown feed: {feed_name}")

        url = self.FEEDS[feed_name]

        response = requests.get(url, timeout=10)
        response.raise_for_status()

        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(response.content)

        return feed
