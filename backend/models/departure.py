from dataclasses import dataclass
from datetime import datetime


@dataclass
class Departure:
    route: str
    destination: str
    direction: str
    arrival_time: datetime
    delay_seconds: int | None = None

    @property
    def minutes_until(self) -> int:
        seconds = (
            self.arrival_time - datetime.now().astimezone()
        ).total_seconds()

        return max(0, round(seconds / 60))

    @property
    def delay_minutes(self) -> int | None:
        if self.delay_seconds is None:
            return None
        
        return round(self.delay_seconds / 60)