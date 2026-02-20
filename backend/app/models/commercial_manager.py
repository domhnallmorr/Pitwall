from pydantic import BaseModel
from typing import Optional


class CommercialManager(BaseModel):
    id: int
    name: str
    age: int
    skill: int
    contract_length: int = 0
    salary: int = 0
    team_id: Optional[int] = None

