from enum import Enum

class SessionNames(Enum):
    FRIDAY_PRACTICE = "FP Friday"
    SATURDAY_PRACTICE = "FP Saturday"
    QUALIFYING = "Qualifying"
    RACE = "Race"

class SessionStatus(Enum):
    PRE_SESSION = "Pre Session"
    RUNNING = "Green"
    POST_SESSION = "Post Session"

class SessionMode(Enum):
    SIMULATE = "simulate"
    