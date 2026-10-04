# app/models/base_entity.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from app.db.base import Base  # 👈 tumia Base moja tu hapa


class BaseEntity(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    created_by = Column(String, nullable=False, default="system")
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.utcnow)
    updated_by = Column(String, nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    deleted_by = Column(String, nullable=True)

    is_active = Column(Boolean, default=True, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)

    def pre_persist(self, current_user: str = "system", tenant_id: int = None):
        self.created_at = datetime.utcnow()
        self.created_by = current_user
        self.updated_at = datetime.utcnow()
        self.updated_by = current_user
        if tenant_id:
            self.tenant_id = tenant_id

    def update(self, current_user: str = "system"):
        self.updated_at = datetime.utcnow()
        self.updated_by = current_user

    def delete(self, current_user: str = "system"):
        self.deleted_at = datetime.utcnow()
        self.deleted_by = current_user
        self.is_active = False
        self.is_deleted = True

    def activate(self):
        self.is_active = True
        self.is_deleted = False

    def deactivate(self):
        self.is_active = False
        self.is_deleted = True
