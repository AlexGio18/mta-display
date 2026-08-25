from dataclasses import dataclass


@dataclass
class Station:
    id: str
    name: str
    latitude: float
    longitude: float
    stop_ids: list[str]