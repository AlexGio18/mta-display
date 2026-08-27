from dataclasses import dataclass
from datetime import datetime

from backend.models.departure import Departure


@dataclass
class DepartureBoard:
    feed_updated_at: datetime
    retrieved_at: datetime
    departures: list[Departure]