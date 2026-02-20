from pydantic import BaseModel
from typing import Optional

class Team(BaseModel):
    id: int
    name: str
    country: str
    car_speed: int = 50
    workforce: int = 0
    technical_director_id: Optional[int] = None
    driver1_id: Optional[int] = None
    driver2_id: Optional[int] = None
    points: int = 0
    balance: int = 0
    facilities: int = 0
