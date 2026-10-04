from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.sensor_reading import SensorReading
from app.models.sensor import Sensor
from fastapi import HTTPException, status


class SensorReadingService:

    @staticmethod
    def create(
        db: Session,
        sensor_id: int,
        value: dict
    ) -> SensorReading:

        sensor = db.query(Sensor).filter(Sensor.id == sensor_id).first()
        if not sensor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sensor not found"
            )

        reading = SensorReading(
            sensor_id=sensor_id,
            value=value
        )

        # update sensor last value
        sensor.last_value = value
        sensor.last_updated = reading.recorded_at

        db.add(reading)
        db.commit()
        db.refresh(reading)

        return reading

    @staticmethod
    def update(
        db: Session,
        reading_id: int,
        value: dict
    ) -> SensorReading:

        reading = db.query(SensorReading).filter(
            SensorReading.id == reading_id
        ).first()

        if not reading:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sensor reading not found"
            )

        reading.value = value
        db.commit()
        db.refresh(reading)

        return reading

    @staticmethod
    def get_all(
        db: Session,
        active_only: bool = True
    ) -> List[SensorReading]:

        query = db.query(SensorReading)

        if active_only:
            query = query.filter(SensorReading.is_active.is_(True))

        return query.order_by(SensorReading.recorded_at.desc()).all()

    @staticmethod
    def get_by_id(
        db: Session,
        reading_id: int
    ) -> SensorReading:

        reading = db.query(SensorReading).filter(
            SensorReading.id == reading_id
        ).first()

        if not reading:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sensor reading not found"
            )

        return reading

    @staticmethod
    def get_by_device(
        db: Session,
        device_id: int,
        active_only: bool = True
    ) -> List[SensorReading]:

        query = db.query(SensorReading).join(Sensor).filter(
            Sensor.device_id == device_id
        )

        if active_only:
            query = query.filter(SensorReading.is_active.is_(True))

        return query.order_by(SensorReading.recorded_at.desc()).all()

    @staticmethod
    def set_active(
        db: Session,
        reading_id: int,
        active: bool
    ) -> SensorReading:

        reading = db.query(SensorReading).filter(
            SensorReading.id == reading_id
        ).first()

        if not reading:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sensor reading not found"
            )

        reading.is_active = active
        db.commit()
        db.refresh(reading)

        return reading
