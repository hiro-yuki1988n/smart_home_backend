# app/models/user.py
from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.models.base_entity import BaseEntity


class User(BaseEntity):
    __tablename__ = "users"

    name = Column(String, nullable=False)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=True)
    phone_number = Column(String, unique=True, nullable=True)
    hashed_password = Column(String, nullable=False)
    failed_attempts = Column(Integer, default=0, nullable=False)
    lockout_until = Column(DateTime)
    profile_pic = Column(String, nullable=True)

    role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)
    role = relationship("Role")

    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    tenant = relationship("Tenant", back_populates="users")

    blacklisted_tokens = relationship("BlacklistedToken", back_populates="user", cascade="all, delete-orphan")
    password_reset_tokens = relationship("PasswordResetToken", back_populates="user", cascade="all, delete-orphan")
    password_reset_otps = relationship("PasswordResetOTP", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")

    @property
    def role_name(self):
        return self.role.name if self.role else None

    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}')>"


class BlacklistedToken(BaseEntity):
    __tablename__ = "blacklisted_tokens"

    token = Column(String, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    user = relationship("User", back_populates="blacklisted_tokens")

    def __repr__(self):
        return f"<BlacklistedToken(id={self.id}, user_id={self.user_id})>"


class PasswordResetToken(BaseEntity):
    __tablename__ = "password_reset_tokens"

    token = Column(String, unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    user = relationship("User", back_populates="password_reset_tokens")

    def __repr__(self):
        return f"<PasswordResetToken(id={self.id}, user_id={self.user_id})>"


class PasswordResetOTP(BaseEntity):
    __tablename__ = "password_reset_otps"

    otp_code = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_used = Column(Boolean, default=False)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    user = relationship("User", back_populates="password_reset_otps")

    def __repr__(self):
        return f"<PasswordResetOTP(id={self.id}, user_id={self.user_id})>"