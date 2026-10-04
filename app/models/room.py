from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base_entity import BaseEntity


class Room(BaseEntity):
    __tablename__ = "rooms"

    name = Column(String, nullable=False)

    devices = relationship("Device", back_populates="room", cascade="all, delete-orphan")

    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    tenant = relationship("Tenant", back_populates="rooms")

    def __repr__(self):
        return f"<Room(id={self.id}, name='{self.name}')>"