from pydantic import BaseModel
from typing import Optional


class TeamPrincipal(BaseModel):
    id: int
    name: str
    country: Optional[str] = None
    age: int
    skill: int
    contract_length: int = 0
    team_id: Optional[int] = None
    active: bool = True
    owns_team: bool = False
