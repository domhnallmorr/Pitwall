from pydantic import BaseModel


class TitleSponsor(BaseModel):
    id: int
    name: str
    wealth: int
    start_year: int = 0
