from sqlalchemy import Column, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.models.base_entity import BaseEntity


class DeviceState(BaseEntity):
    __tablename__ = "device_states"

    device_id = Column(
        Integer,
        ForeignKey("devices.id"),
        nullable=False,
        index=True
    )

    device = relationship(
        "Device",
        back_populates="device_states"
    )

    state = Column(JSON, nullable=False)

    def __repr__(self):
        return f"<DeviceState(id={self.id}, device_id={self.device_id}, state={self.state})>"
