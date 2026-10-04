from typing import List
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.dependencies.auth import get_db
from app.core.security import get_current_user, permission_required
from app.models.user import User
from app.schemas.user import RoleCreate, RoleUpdate, RoleOut, PermissionOut
from app.services.role_service import *

router = APIRouter()


@router.get("/all_roles", response_model=List[RoleOut])
@permission_required("VIEW_ROLES")
def get_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    return get_all_roles(db, current_user, request)


@router.post("/create_role", response_model=RoleOut, status_code=201)
@permission_required("SAVE_ROLE")
def create_role(
    role_in: RoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    return create_role_service(role_in, db, current_user, request)


@router.put("/roles/{role_id}", response_model=RoleOut)
@permission_required("SAVE_ROLE")
def update_role(
    role_id: int,
    role_in: RoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    return update_role_service(role_id, role_in, db, current_user, request)


@router.delete("/roles/{role_id}")
@permission_required("DELETE_ROLE")
def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    return delete_role_service(role_id, db, current_user, request)


@router.get("/all_permissions", response_model=List[PermissionOut])
@permission_required("VIEW_PERMISSIONS")
def get_permissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    return get_all_permissions(db, current_user, request)


@router.get("/user/{user_id}", response_model=List[RoleOut])
@permission_required("VIEW_ROLES")
def get_roles_by_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    return get_roles_by_user_service(user_id, db, current_user, request)


@router.post("/roles/{role_id}/permissions/{perm_id}")
@permission_required("MANAGE_ROLES")
def assign_permission(
    role_id: int,
    perm_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    return assign_permission_service(role_id, perm_id, db, current_user, request)


@router.delete("/roles/{role_id}/permissions/{perm_id}")
@permission_required("MANAGE_ROLES")
def remove_permission(
    role_id: int,
    perm_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    return remove_permission_service(role_id, perm_id, db, current_user, request)
