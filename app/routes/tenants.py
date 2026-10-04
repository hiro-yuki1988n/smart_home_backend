# app/routes/tenants.py
from typing import List
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from starlette import status

from app.core.security import permission_required, get_current_user
from app.db.postgres import SessionLocal
from app.models.user import User
from app.schemas.tenant import TenantOut, TenantCreate, TenantUpdate
from app.services.tenant_service import TenantService

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/new", response_model=TenantOut)
@permission_required("MANAGE_TENANTS")
def create_tenant(
    payload: TenantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    return TenantService.create_tenant(db, payload, current_user, request)


@router.get("/", response_model=List[TenantOut])
@permission_required("VIEW_TENANTS")
def get_all_tenants(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    return TenantService.get_all_tenants(db, current_user, request)


@router.get("/{tenant_id}", response_model=TenantOut)
@permission_required("VIEW_TENANTS")
def get_tenant_by_id(
    tenant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    return TenantService.get_by_id(db, tenant_id, current_user, request)


@router.put("/{tenant_id}", response_model=TenantOut)
@permission_required("MANAGE_TENANTS")
def update_tenant(
    tenant_id: int,
    payload: TenantUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    return TenantService.update_tenant(db, tenant_id, payload, current_user, request)


@router.delete("/{tenant_id}", status_code=status.HTTP_204_NO_CONTENT)
@permission_required("MANAGE_TENANTS")
def delete_tenant(
    tenant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    TenantService.delete_tenant(db, tenant_id, current_user, request)
    return None


@router.post("/{tenant_id}/deactivate", response_model=TenantOut)
@permission_required("MANAGE_TENANTS")
def deactivate_tenant(
    tenant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    return TenantService.set_active_status(
        db, tenant_id, False, current_user, request
    )


@router.post("/{tenant_id}/activate", response_model=TenantOut)
@permission_required("MANAGE_TENANTS")
def activate_tenant(
    tenant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    return TenantService.set_active_status(
        db, tenant_id, True, current_user, request
    )
