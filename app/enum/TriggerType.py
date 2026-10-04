import enum


class TriggerType(enum.Enum):
     TIME = "TIME"
     SENSOR = "SENSOR"
     LOCATION = "LOCATION"
     DEVICE_STATE = "DEVICE_STATE"
