from sqlalchemy.orm import Session
from fastapi import HTTPException
from starlette import status

from app.models.tenant import Tenant
from app.models.user import User
from app.schemas.tenant import TenantCreate, TenantUpdate
from app.utils.audit_logger import log_activity


class TenantService:

    @staticmethod
    def create_tenant(
        db: Session,
        payload: TenantCreate,
        current_user: User,
        request
    ) -> Tenant:
        existing = db.query(Tenant).filter(Tenant.name == payload.name).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tenant already exists"
            )

        tenant = Tenant(
            name=payload.name,
            description=payload.description
        )
        tenant.pre_persist(current_user=current_user.id)

        db.add(tenant)
        db.commit()
        db.refresh(tenant)

        log_activity(
            db=db,
            user=current_user,
            action="SAVE TENANT",
            description=f"User with username: {current_user.username} created a tenant {tenant.name}",
            request=request
        )

        return tenant

    @staticmethod
    def get_all_tenants(
        db: Session,
        current_user: User,
        request
    ):
        tenants = (
            db.query(Tenant)
            .filter(
                Tenant.is_deleted == False,
                User.tenant_id == current_user.tenant_id
            )
            .all()
        )

        log_activity(
            db=db,
            user=current_user,
            action="VIEW TENANTS",
            description=f"User with username: {current_user.username} listed all tenants",
            request=request
        )

        return tenants

    @staticmethod
    def get_by_id(
        db: Session,
        tenant_id: int,
        current_user: User,
        request
    ) -> Tenant:
        tenant = (
            db.query(Tenant)
            .filter(Tenant.id == tenant_id, Tenant.is_deleted == False)
            .first()
        )

        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )

        log_activity(
            db=db,
            user=current_user,
            action="VIEW TENANT",
            description=f"User with username: {current_user.username} viewed tenant {tenant.name}",
            request=request
        )

        return tenant

    @staticmethod
    def update_tenant(
        db: Session,
        tenant_id: int,
        payload: TenantUpdate,
        current_user: User,
        request
    ) -> Tenant:
        tenant = (
            db.query(Tenant)
            .filter(Tenant.id == tenant_id, Tenant.is_deleted == False)
            .first()
        )

        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )

        if payload.name:
            tenant.name = payload.name
        if payload.description:
            tenant.description = payload.description

        tenant.update(current_user=current_user.id)
        db.commit()
        db.refresh(tenant)

        log_activity(
            db=db,
            user=current_user,
            action="UPDATE TENANT",
            description=f"User with username: {current_user.username} updated tenant {tenant.name}",
            request=request
        )

        return tenant

    @staticmethod
    def delete_tenant(
        db: Session,
        tenant_id: int,
        current_user: User,
        request
    ):
        tenant = (
            db.query(Tenant)
            .filter(Tenant.id == tenant_id, Tenant.is_deleted == False)
            .first()
        )

        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )

        tenant.delete(current_user=current_user.id)
        db.commit()

        log_activity(
            db=db,
            user=current_user,
            action="DELETE TENANT",
            description=f"User with username: {current_user.username} deleted tenant {tenant.name}",
            request=request
        )

    @staticmethod
    def set_active_status(
        db: Session,
        tenant_id: int,
        is_active: bool,
        current_user: User,
        request
    ) -> Tenant:
        tenant = (
            db.query(Tenant)
            .filter(Tenant.id == tenant_id, Tenant.is_deleted == False)
            .first()
        )

        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )

        if tenant.is_active == is_active:
            state = "active" if is_active else "inactive"
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tenant is already {state}"
            )

        tenant.is_active = is_active
        tenant.update(current_user=current_user.id)

        db.commit()
        db.refresh(tenant)

        action = "activated" if is_active else "deactivated"

        log_activity(
            db=db,
            user=current_user,
            action="MANAGE TENANT",
            description=f"User with username: {current_user.username} {action} tenant {tenant.name}",
            request=request
        )

        return tenant
