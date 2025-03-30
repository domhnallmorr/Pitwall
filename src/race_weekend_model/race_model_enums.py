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
    

class ParticipantStatus(Enum):
    IN_PITS = "PIT"
    RETIRED = "Retired"
    RUNNING = "Running"
    PITTING_IN = "Pitting In"

class RetirementReasons(Enum):
    MECHANICAL = "Mechanical"
    CRASH = "Crash"

class OvertakingStatus(Enum):
    NONE = "None"
    ATTACKING = "Attacking"
    HOLD_BACK = "Hold Back" # if car in front is attempting overtake, then car behind is holds back
