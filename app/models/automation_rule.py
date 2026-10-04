from sqlalchemy import Column, Integer, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship

from sqlalchemy import Enum as SQLEnum

from app.enum.TriggerType import TriggerType
from app.enum.action_type import ActionType
from app.enum.condition_operator import ConditionOperator
from app.models.base_entity import BaseEntity


class AutomationRule(BaseEntity):
    __tablename__ = "automation_rules"

    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    tenant = relationship("Tenant", back_populates="automation_rules")

    enabled = Column(Boolean, default=True)

    # ---------- TRIGGER ----------
    trigger_type = Column(SQLEnum(TriggerType, name="trigger_type_enum"), nullable=False)

    trigger_sensor_id = Column(
        Integer, ForeignKey("sensors.id"), nullable=True
    )
    trigger_device_id = Column(
        Integer, ForeignKey("devices.id"), nullable=True
    )

    condition_operator = Column(
        SQLEnum(ConditionOperator, name="condition_operator_enum"),
        nullable=True
    )

    trigger_value = Column(JSON, nullable=True)

    # ---------- ACTION ----------
    action_type = Column(SQLEnum(ActionType, name="action_type_enum"), nullable=False)

    target_device_id = Column(
        Integer, ForeignKey("devices.id"), nullable=False
    )

    action_payload = Column(JSON, nullable=True)

    # ---------- RELATIONSHIPS ----------
    trigger_sensor = relationship("Sensor", foreign_keys=[trigger_sensor_id])
    trigger_device = relationship("Device", foreign_keys=[trigger_device_id])
    target_device = relationship("Device", foreign_keys=[target_device_id])

    def __repr__(self):
        return f"<AutomationRule(id={self.id}, enabled={self.enabled})>"
