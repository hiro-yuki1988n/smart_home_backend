from fastapi import APIRouter, Depends

from app.core.security import get_current_user, permission_required
from app.dependencies.auth import get_db
from app.schemas.sensor import SensorOut
from app.services.sensor_service import *

router = APIRouter()


@router.post("/", response_model=SensorOut)
@permission_required("CREATE_SENSOR")
def create_sensor(
    payload: SensorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    return create_sensor_service(payload, db, current_user, request)


@router.put("/{sensor_id}", response_model=SensorOut)
@permission_required("UPDATE_SENSOR")
def update_sensor(
    sensor_id: int,
    payload: SensorUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    return update_sensor_service(sensor_id, payload, db, current_user, request)


@router.get("/", response_model=List[SensorOut])
@permission_required("VIEW_SENSORS")
def get_sensors(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    return get_all_sensors_service(db, current_user, request)


@router.get("/{sensor_id}", response_model=SensorOut)
@permission_required("VIEW_SENSOR")
def get_sensor(
    sensor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    return get_sensor_by_id_service(sensor_id, db, current_user, request)


@router.get("/device/{device_id}", response_model=List[SensorOut])
@permission_required("VIEW_SENSOR")
def get_device_sensors(
    device_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    return get_sensors_by_device_service(device_id, db, current_user, request)


@router.patch("/{sensor_id}/deactivate")
@permission_required("UPDATE_SENSOR")
def deactivate_sensor(
    sensor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    return deactivate_sensor_service(sensor_id, db, current_user, request)


@router.patch("/{sensor_id}/activate")
@permission_required("UPDATE_SENSOR")
def activate_sensor(
    sensor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    return activate_sensor_service(sensor_id, db, current_user, request)



# @router.get("/")
# async def get_mock_sensors():
#     return {
#         "temperature": round(random.uniform(25, 30), 2),
#         "humidity": round(random.uniform(40, 60), 2),
#         "timestamp": datetime.utcnow()
#     }
