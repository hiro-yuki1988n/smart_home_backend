from pydantic import BaseModel
from typing import Optional
from app.enum.sensor_type import SensorType


class SensorBase(BaseModel):
    device_id: int
    type: SensorType
    unit: Optional[str]


class SensorCreate(SensorBase):
    pass


class SensorUpdate(BaseModel):
    type: Optional[SensorType]
    unit: Optional[str]


class SensorOut(SensorBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True
