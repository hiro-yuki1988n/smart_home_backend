# app/services/user_service.py
import os
import shutil
import uuid
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, UploadFile

from app.core.security import hash_password, verify_password
from app.models.user import User, PasswordResetToken, PasswordResetOTP
from app.models.role import Role, Permission, role_permissions
from app.schemas.user import UserCreate, UserUpdate, PasswordChange, EmailResetModel, OTPResetModel


class UserService:

    @staticmethod
    def register_user(db: Session, user: UserCreate, current_user):
        tenant_id = user.tenant_id or current_user.tenant_id

        existing = db.query(User).filter(
            User.username == user.username,
            User.tenant_id == tenant_id
        ).first()

        if existing:
            raise HTTPException(400, "Username already registered for this tenant")

        role = db.query(Role).filter(Role.id == user.role_id).first()
        if not role:
            raise HTTPException(400, f"Role with id {user.role_id} not found")

        new_user = User(
            username=user.username,
            name=user.name,
            hashed_password=hash_password(user.password),
            is_active=True,
            email=user.email,
            phone_number=user.phone_number,
            tenant_id=tenant_id,
            role_id=user.role_id
        )

        new_user.pre_persist(
            current_user=current_user.username,
            tenant_id=tenant_id
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return new_user

    @staticmethod
    def update_user(db: Session, user_id: int, payload: UserUpdate, current_user):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(404, "User not found")

        if user.tenant_id != current_user.tenant_id:
            raise HTTPException(403, "Permission denied")

        for field, value in payload.dict(exclude_unset=True).items():
            if field != "password":
                setattr(user, field, value)

        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def list_users(db: Session, tenant_id: int):
        return db.query(User).filter(
            User.tenant_id == tenant_id,
            User.is_deleted == False
        ).all()


    @staticmethod
    def get_user(db: Session, user_id: int, tenant_id: int):
        user = db.query(User).filter(
            User.id == user_id,
            User.tenant_id == tenant_id,
            User.is_deleted == False
        ).first()

        if not user:
            raise HTTPException(404, "User not found")

        return user


    @staticmethod
    def change_password(db: Session, payload: PasswordChange, current_user):
        db_user = db.query(User).filter(User.id == current_user.id).first()
        if not db_user:
            raise HTTPException(404, "User not found")

        if payload.user_id and getattr(db_user, "is_admin", False):
            target = db.query(User).filter(User.id == payload.user_id).first()
            if not target:
                raise HTTPException(404, "Target user not found")

            target.hashed_password = hash_password(payload.new_password)
            db.commit()
            return

        if not verify_password(payload.old_password, db_user.hashed_password):
            raise HTTPException(400, "Old password incorrect")

        db_user.hashed_password = hash_password(payload.new_password)
        db.commit()

    @staticmethod
    def reset_password_email(db: Session, payload: EmailResetModel):
        token_entry = db.query(PasswordResetToken).filter(
            PasswordResetToken.token == payload.token,
            PasswordResetToken.used == False,
            PasswordResetToken.expires_at > datetime.utcnow()
        ).first()

        if not token_entry:
            raise HTTPException(400, "Invalid or expired token")

        user = db.query(User).filter(User.id == token_entry.user_id).first()
        user.hashed_password = hash_password(payload.new_password)
        token_entry.used = True
        db.commit()

    @staticmethod
    def reset_password_otp(db: Session, payload: OTPResetModel):
        user = db.query(User).filter(User.phone_number == payload.phone).first()
        if not user:
            raise HTTPException(404, "User not found")

        otp = db.query(PasswordResetOTP).filter(
            PasswordResetOTP.user_id == user.id,
            PasswordResetOTP.otp_code == payload.otp_code,
            PasswordResetOTP.is_used == False,
            PasswordResetOTP.expires_at > datetime.utcnow()
        ).first()

        if not otp:
            raise HTTPException(400, "Invalid or expired OTP")

        user.hashed_password = hash_password(payload.new_password)
        otp.is_used = True
        db.commit()

    @staticmethod
    def upload_profile_pic(db: Session, current_user, file: UploadFile):
        folder = "media/users"
        os.makedirs(folder, exist_ok=True)

        ext = file.filename.split(".")[-1].lower()
        filename = f"{uuid.uuid4()}.{ext}"
        path = f"{folder}/{filename}"

        with open(path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        current_user.profile_pic = path
        db.commit()
        db.refresh(current_user)

        return path

    # @staticmethod
    # def get_user(db: Session, user_id: int, tenant_id: int):
    #     """Basic fetch — unaitumia kwenye update_user na sehemu nyingine."""
    #     user = db.query(User).filter(
    #         User.id == user_id,
    #         User.tenant_id == tenant_id,
    #         User.is_deleted == False
    #     ).first()
    #
    #     if not user:
    #         raise HTTPException(404, "User not found")
    #
    #     return user

    @staticmethod
    def get_user_with_permissions(db: Session, user_id: int, tenant_id: int):
        """Fetch ikiwa na role + permissions zilizoload mapema (avoid N+1 queries)."""
        user = db.query(User).options(
            joinedload(User.role).joinedload(Role.permissions)
        ).filter(
            User.id == user_id,
            User.tenant_id == tenant_id,
            User.is_deleted == False
        ).first()

        if not user:
            raise HTTPException(404, "User not found")

        return user

    @staticmethod
    def serialize_user(user: User) -> dict:
        """Badilisha User object kuwa dict inayoendana na UserOut schema."""
        return {
            "id": user.id,
            "name": user.name,
            "username": user.username,
            "email": user.email,
            "phone_number": user.phone_number,
            "profile_pic": user.profile_pic,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "deleted_at": user.deleted_at,
            "role_name": user.role.name if user.role else None,
            "role_id": user.role.id if user.role else None,
            "permissions": [
                {"id": p.id, "name": p.name} for p in user.role.permissions
            ] if user.role else [],
        }
