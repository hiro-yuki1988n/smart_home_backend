from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_tenant
from app.dependencies.auth import get_db
from app.models.device import Device

router = APIRouter()

# Mock devices
mock_devices = [
    {"id": 1, "name": "Living Room Light", "status": False},
    {"id": 2, "name": "Bedroom Fan", "status": True},
]


@router.get("/")
async def get_devices():
    return mock_devices


@router.post("/{device_id}/toggle")
async def toggle_device(device_id: int):
    for device in mock_devices:
        if device["id"] == device_id:
            device["status"] = not device["status"]
            return device
    return {"error": "Device not found"}


@router.get("/")
def list_devices(db: Session = Depends(get_db), tenant_id: int = Depends(get_current_tenant)):
    devices = db.query(Device).filter(Device.tenant_id == tenant_id, Device.is_deleted == False).all()
    return devices
