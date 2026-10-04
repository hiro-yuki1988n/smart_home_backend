from pydantic import BaseModel
from typing import Any
from datetime import datetime


class SensorReadingCreate(BaseModel):
    sensor_id: int
    value: Any


class SensorReadingUpdate(BaseModel):
    value: Any


class SensorReadingResponse(BaseModel):
    id: int
    sensor_id: int
    value: Any
    recorded_at: datetime
    is_active: bool

    class Config:
        from_attributes = True
