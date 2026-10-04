from sqlalchemy import Column, Integer, ForeignKey, Double, DateTime, String, JSON, Enum
from sqlalchemy.orm import relationship

from app.enum.sensor_type import SensorType
from app.models.base_entity import BaseEntity


class Sensor(BaseEntity):
    __tablename__ = "sensors"

    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False, index=True)
    device = relationship("Device", back_populates="sensors")

    type = Column(Enum(SensorType, name="sensor_type_enum"), nullable=False)

    unit = Column(String, nullable=True)  # °C, %, ppm, lux

    last_value = Column(JSON, nullable=True)
    last_updated = Column(DateTime)

    readings = relationship("SensorReading", back_populates="sensor", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Sensor(id={self.id}, type={self.type})>"

