from fastapi import HTTPException, Request
from sqlalchemy.orm import Session
from typing import List

from app.models.role import Role, Permission
from app.models.user import User
from app.schemas.user import RoleCreate, RoleUpdate
from app.utils.audit_logger import log_activity


def get_all_roles(db: Session, current_user: User, request: Request):
    roles = db.query(Role).filter(Role.is_deleted == False).all()

    log_activity(
        db=db,
        user=current_user,
        action="VIEW ROLES",
        description=f"User with username: {current_user.username} requested a list of roles",
        request=request
    )
    return roles


def create_role_service(
    role_in: RoleCreate,
    db: Session,
    current_user: User,
    request: Request
):
    existing = db.query(Role).filter(
        Role.name == role_in.name,
        Role.is_deleted == False
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Role with this name already exists")

    role = Role(
        name=role_in.name,
        description=role_in.description,
        created_by=current_user.username
    )
    db.add(role)
    db.commit()
    db.refresh(role)

    if role_in.permission_ids:
        permissions = db.query(Permission).filter(
            Permission.id.in_(role_in.permission_ids)
        ).all()
        role.permissions = permissions
        db.commit()
        db.refresh(role)

    log_activity(
        db=db,
        user=current_user,
        action="SAVE ROLE",
        description=f"User with username: {current_user.username} created a role {role.name}",
        request=request
    )

    return role


def update_role_service(
    role_id: int,
    role_in: RoleUpdate,
    db: Session,
    current_user: User,
    request: Request
):
    role = db.query(Role).filter(
        Role.id == role_id,
        Role.tenant_id == current_user.tenant_id,
        Role.is_deleted == False
    ).first()

    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    if role_in.name is not None:
        role.name = role_in.name
    if role_in.description is not None:
        role.description = role_in.description

    if role_in.permission_ids:
        permissions = db.query(Permission).filter(
            Permission.id.in_(role_in.permission_ids)
        ).all()
        role.permissions = permissions

    role.update(current_user.username)
    db.commit()
    db.refresh(role)

    log_activity(
        db=db,
        user=current_user,
        action="UPDATE ROLE",
        description=f"User with username: {current_user.username} updated role {role.name}",
        request=request
    )

    return role


def delete_role_service(
    role_id: int,
    db: Session,
    current_user: User,
    request: Request
):
    role = db.query(Role).filter(
        Role.id == role_id,
        Role.is_deleted == False
    ).first()

    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    role.delete(current_user=current_user.username)
    db.add(role)
    db.commit()
    db.refresh(role)

    log_activity(
        db=db,
        user=current_user,
        action="DELETE ROLE",
        description=f"User with username: {current_user.username} deleted role {role.name}",
        request=request
    )

    return {"message": f"Role '{role.name}' soft deleted successfully"}


def get_all_permissions(db: Session, current_user: User, request: Request):
    permissions = db.query(Permission).filter(
        Permission.is_deleted == False
    ).all()

    log_activity(
        db=db,
        user=current_user,
        action="VIEW PERMISSIONS",
        description=f"User with username: {current_user.username} requested permissions",
        request=request
    )

    return permissions


def get_roles_by_user_service(
    user_id: int,
    db: Session,
    current_user: User,
    request: Request
):
    user = db.query(User).filter(
        User.id == user_id,
        User.is_deleted == False
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    log_activity(
        db=db,
        user=current_user,
        action="VIEW USER ROLES",
        description="Viewed roles by user",
        request=request
    )

    return [user.role] if user.role else []


def assign_permission_service(
    role_id: int,
    perm_id: int,
    db: Session,
    current_user: User,
    request: Request
):
    role = db.query(Role).filter(Role.id == role_id).first()
    perm = db.query(Permission).filter(Permission.id == perm_id).first()

    if not role or not perm:
        raise HTTPException(status_code=404, detail="Role or Permission not found")

    if perm not in role.permissions:
        role.permissions.append(perm)
        db.commit()
        db.refresh(role)

        log_activity(
            db=db,
            user=current_user,
            action="ASSIGN PERMISSION",
            description="Assigned permission to role",
            request=request
        )

    return {"message": f"Permission '{perm.name}' assigned to role '{role.name}'"}


def remove_permission_service(
    role_id: int,
    perm_id: int,
    db: Session,
    current_user: User,
    request: Request
):
    role = db.query(Role).filter(Role.id == role_id).first()
    perm = db.query(Permission).filter(Permission.id == perm_id).first()

    if not role or not perm:
        raise HTTPException(status_code=404, detail="Role or Permission not found")

    if perm in role.permissions:
        role.permissions.remove(perm)
        db.commit()
        db.refresh(role)

        log_activity(
            db=db,
            user=current_user,
            action="REMOVE PERMISSION",
            description="Removed permission from role",
            request=request
        )

    return {"message": f"Permission '{perm.name}' removed from role '{role.name}'"}
