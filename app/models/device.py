from sqlalchemy import Enum as SQLEnum

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.enum.protocol import Protocol
from app.models.base_entity import BaseEntity


class Device(BaseEntity):
    __tablename__ = "devices"

    name = Column(String, nullable=False)
    serial_no = Column(String, nullable=False, unique=True, index=True)
    ip_address = Column(String, nullable=True)
    protocol = Column(SQLEnum(Protocol, name="protocol_enum"), nullable=False)
    is_online = Column(Boolean, default=False)
    device_mode = Column(String, nullable=False)
    last_seen_at = Column(DateTime)

    device_type_id = Column(Integer, ForeignKey("device_types.id"), index=True)
    device_type = relationship("DeviceType", back_populates="devices")

    device_states = relationship("DeviceState", back_populates="device", cascade="all, delete-orphan")
    sensors = relationship("Sensor", back_populates="device", cascade="all, delete-orphan")

    triggered_automation_rules = relationship(
        "AutomationRule",
        foreign_keys="AutomationRule.trigger_device_id",
        cascade="all, delete-orphan"
    )

    targeted_automation_rules = relationship(
        "AutomationRule",
        foreign_keys="AutomationRule.target_device_id",
        cascade="all, delete-orphan"
    )

    room_id = Column(Integer, ForeignKey("rooms.id"), index=True)
    room = relationship("Room", back_populates="devices")

    mqtt_client_id = Column(Integer, ForeignKey("mqtt_clients.id"), nullable=True, index=True)
    mqtt_client = relationship("MqttClient", back_populates="devices")

    def __repr__(self):
        return f"<Device(id={self.id}, name='{self.name}', online={self.is_online})>"