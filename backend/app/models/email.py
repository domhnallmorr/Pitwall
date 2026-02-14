from pydantic import BaseModel
from enum import Enum
from typing import Optional


class EmailCategory(str, Enum):
    GENERAL = "GENERAL"
    RACE_RESULT = "RACE_RESULT"
    SEASON = "SEASON"


class Email(BaseModel):
    id: int
    sender: str
    subject: str
    body: str
    week: int
    year: int
    read: bool = False
    category: EmailCategory = EmailCategory.GENERAL
