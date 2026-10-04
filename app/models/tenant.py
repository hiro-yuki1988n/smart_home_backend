from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship

from app.models.base_entity import BaseEntity


class Tenant(BaseEntity):
    __tablename__ = "tenants"

    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    address = Column(String, nullable=True)

    rooms = relationship("Room", back_populates="tenant",  cascade="all, delete-orphan")
    # devices = relationship("Device", back_populates="tenant",  cascade="all, delete-orphan")
    users = relationship('User', back_populates='tenant',  cascade="all, delete-orphan")
    automation_rules = relationship('AutomationRule', back_populates='tenant',  cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Tenant(id={self.id}, name='{self.name}')>"
