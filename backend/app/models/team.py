from pydantic import BaseModel
from typing import Optional

class Team(BaseModel):
    id: int
    name: str
    country: str
    driver1_id: Optional[int] = None
    driver2_id: Optional[int] = None
