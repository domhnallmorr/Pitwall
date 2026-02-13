from pydantic import BaseModel
from typing import Optional

class Circuit(BaseModel):
    id: int
    name: str
    country: str
    location: str
    laps: int
    base_laptime_ms: int # stored as ms
    length_km: float
    overtaking_delta: float
    power_factor: float
    track_map_path: Optional[str] = None
