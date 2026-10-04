import enum


class Protocol(enum.Enum):
    MQTT = "MQTT"
    HTTP = "HTTP"
    COAP = "COAP"