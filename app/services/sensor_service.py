from fastapi import HTTPException, Request
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from app.models.sensor import Sensor
from app.models.device import Device
from app.models.user import User
from app.schemas.sensor import SensorCreate, SensorUpdate
from app.utils.audit_logger import log_activity


def create_sensor_service(
    payload: SensorCreate,
    db: Session,
    current_user: User,
    request: Request
):
    device = db.query(Device).filter(
        Device.id == payload.device_id,
        Device.is_deleted == False
    ).first()

    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    sensor = Sensor(
        device_id=payload.device_id,
        type=payload.type,
        unit=payload.unit,
    )
    sensor.pre_persist(current_user.username)

    db.add(sensor)
    db.commit()
    db.refresh(sensor)

    log_activity(
        db=db,
        user=current_user,
        action="CREATE SENSOR",
        description=f"Created sensor {sensor.type} for device {device.name}",
        request=request
    )

    return sensor


def update_sensor_service(
    sensor_id: int,
    payload: SensorUpdate,
    db: Session,
    current_user: User,
    request: Request
):
    sensor = db.query(Sensor).filter(
        Sensor.id == sensor_id,
        Sensor.is_deleted == False
    ).first()

    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")

    if payload.type is not None:
        sensor.type = payload.type
    if payload.unit is not None:
        sensor.unit = payload.unit

    sensor.update(current_user.username)
    db.commit()
    db.refresh(sensor)

    log_activity(
        db=db,
        user=current_user,
        action="UPDATE SENSOR",
        description=f"Updated sensor ID {sensor.id}",
        request=request
    )

    return sensor


def get_all_sensors_service(
    db: Session,
    current_user: User,
    request: Request
):
    sensors = db.query(Sensor).filter(
        Sensor.is_deleted == False
    ).all()

    log_activity(
        db=db,
        user=current_user,
        action="VIEW SENSORS",
        description="Viewed all sensors",
        request=request
    )

    return sensors


def get_sensor_by_id_service(
    sensor_id: int,
    db: Session,
    current_user: User,
    request: Request
):
    sensor = db.query(Sensor).filter(
        Sensor.id == sensor_id,
        Sensor.is_deleted == False
    ).first()

    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")

    log_activity(
        db=db,
        user=current_user,
        action="VIEW SENSOR",
        description=f"Viewed sensor ID {sensor_id}",
        request=request
    )

    return sensor


def get_sensors_by_device_service(
    device_id: int,
    db: Session,
    current_user: User,
    request: Request
):
    sensors = db.query(Sensor).filter(
        Sensor.device_id == device_id,
        Sensor.is_deleted == False
    ).all()

    log_activity(
        db=db,
        user=current_user,
        action="VIEW DEVICE SENSORS",
        description=f"Viewed sensors for device ID {device_id}",
        request=request
    )

    return sensors


def deactivate_sensor_service(
    sensor_id: int,
    db: Session,
    current_user: User,
    request: Request
):
    sensor = db.query(Sensor).filter(
        Sensor.id == sensor_id,
        Sensor.is_deleted == False
    ).first()

    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")

    sensor.is_active = False
    sensor.update(current_user.username)
    db.commit()

    log_activity(
        db=db,
        user=current_user,
        action="DEACTIVATE SENSOR",
        description=f"Deactivated sensor ID {sensor_id}",
        request=request
    )

    return {"message": "Sensor deactivated successfully"}


def activate_sensor_service(
    sensor_id: int,
    db: Session,
    current_user: User,
    request: Request
):
    sensor = db.query(Sensor).filter(
        Sensor.id == sensor_id,
        Sensor.is_deleted == False
    ).first()

    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")

    sensor.is_active = True
    sensor.update(current_user.username)
    db.commit()

    log_activity(
        db=db,
        user=current_user,
        action="ACTIVATE SENSOR",
        description=f"Activated sensor ID {sensor_id}",
        request=request
    )

    return {"message": "Sensor activated successfully"}
