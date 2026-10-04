# app/models/mqtt_client.py

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.models.base_entity import BaseEntity


class MqttClient(BaseEntity):
    __tablename__ = "mqtt_clients"

    client_id = Column(String, nullable=False, unique=True)
    username = Column(String, nullable=True)

    devices = relationship(
        "Device",
        back_populates="mqtt_client"
    )

    def __repr__(self):
        return f"<MqttClient(id={self.id}, client_id={self.client_id})>"
