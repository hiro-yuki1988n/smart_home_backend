from sqlalchemy import String, Column, Enum, Boolean, JSON
from sqlalchemy.orm import relationship

from app.enum.device_category import DeviceCategory
from app.models.base_entity import BaseEntity


class DeviceType(BaseEntity):
    __tablename__ = "device_types"

    name = Column(String, nullable=False, unique=True, index=True)
    category = Column(Enum(DeviceCategory, name="device_category_enum"), nullable=False)

    capabilities = Column(JSON, nullable=False)

    devices = relationship("Device", back_populates="device_type")

    def __repr__(self):
        return f"<DeviceType(id={self.id}, name='{self.name}', category={self.category})>"
