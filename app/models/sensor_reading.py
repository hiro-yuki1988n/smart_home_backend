from sqlalchemy import Column, Integer, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base_entity import BaseEntity


class SensorReading(BaseEntity):
    __tablename__ = "sensor_readings"

    sensor_id = Column(Integer, ForeignKey("sensors.id"), nullable=False, index=True)
    sensor = relationship("Sensor", back_populates="readings")

    value = Column(JSON, nullable=False)

    recorded_at = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<SensorReading(sensor_id={self.sensor_id}, value={self.value})>"
