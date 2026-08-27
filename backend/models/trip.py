from dataclasses import dataclass


@dataclass
class Trip:
    id: str
    route_id: str
    direction_id: str
    headsign: str