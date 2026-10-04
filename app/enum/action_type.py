import enum


class ActionType(enum.Enum):
    TURN_ON = "TURN_ON"
    TURN_OFF = "TURN_OFF"
    SET_LEVEL = "SET_LEVEL"
    SET_TEMPERATURE = "SET_TEMPERATURE"
    LOCK = "LOCK"
