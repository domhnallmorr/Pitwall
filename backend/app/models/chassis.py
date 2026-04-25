from pydantic import BaseModel


class Chassis(BaseModel):
    id: int
    team_id: int
    name: str
    wear: int = 0

