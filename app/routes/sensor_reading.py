from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database.session import get_db
from app.services.sensor_reading_service import SensorReadingService
from app.schemas.sensor_reading_schema import (
    SensorReadingCreate,
    SensorReadingUpdate,
    SensorReadingResponse
)

router = APIRouter(
    prefix="/sensor-readings",
    tags=["Sensor Readings"]
)


@router.post("/", response_model=SensorReadingResponse)
def create_reading(
    payload: SensorReadingCreate,
    db: Session = Depends(get_db)
):
    return SensorReadingService.create(
        db=db,
        sensor_id=payload.sensor_id,
        value=payload.value
    )


@router.put("/{reading_id}", response_model=SensorReadingResponse)
def update_reading(
    reading_id: int,
    payload: SensorReadingUpdate,
    db: Session = Depends(get_db)
):
    return SensorReadingService.update(
        db=db,
        reading_id=reading_id,
        value=payload.value
    )


@router.get("/", response_model=List[SensorReadingResponse])
def get_all_readings(
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    return SensorReadingService.get_all(db, active_only)


@router.get("/{reading_id}", response_model=SensorReadingResponse)
def get_reading_by_id(
    reading_id: int,
    db: Session = Depends(get_db)
):
    return SensorReadingService.get_by_id(db, reading_id)


@router.get("/device/{device_id}", response_model=List[SensorReadingResponse])
def get_readings_by_device(
    device_id: int,
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    return SensorReadingService.get_by_device(
        db, device_id, active_only
    )


@router.patch("/{reading_id}/activate", response_model=SensorReadingResponse)
def activate_reading(
    reading_id: int,
    db: Session = Depends(get_db)
):
    return SensorReadingService.set_active(
        db, reading_id, True
    )


@router.patch("/{reading_id}/deactivate", response_model=SensorReadingResponse)
def deactivate_reading(
    reading_id: int,
    db: Session = Depends(get_db)
):
    return SensorReadingService.set_active(
        db, reading_id, False
    )
