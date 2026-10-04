# app/models/role.py
from sqlalchemy import Column, Integer, String, Boolean, Table, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.base_entity import BaseEntity


class Role(BaseEntity):
    __tablename__ = "roles"

    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    permissions = relationship("Permission", secondary="role_permissions", back_populates="roles")

    def __repr__(self):
        return f"<Role(id={self.id}, name='{self.name}')>"


class Permission(BaseEntity):
    __tablename__ = "permissions"

    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    roles = relationship("Role", secondary="role_permissions", back_populates="permissions")

    def __repr__(self):
        return f"<Permission(id={self.id}, name='{self.name}')>"


# Association table
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", ForeignKey("roles.id"), primary_key=True),
    Column("permission_id", ForeignKey("permissions.id"), primary_key=True),
)
