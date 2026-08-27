from dataclasses import dataclass
from datetime import datetime


@dataclass
class Departure:
    route: str
    destination: str
    direction: str
    arrival_time: datetime

    @property
    def minutes_until(self) -> int:
        seconds = (
            self.arrival_time - datetime.now().astimezone()
        ).total_seconds()

        return max(0, round(seconds / 60))