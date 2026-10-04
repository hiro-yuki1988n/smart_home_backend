from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


# ----------------------
# Tenant schemas
# ----------------------

class TenantBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: Optional[bool] = True
    is_deleted: Optional[bool] = False


class TenantCreate(TenantBase):
    pass  # kwa sasa hakuna additional fields


class TenantUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class TenantOut(TenantBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    users_count: Optional[int] = 0  # optional: kuonyesha idadi ya users
    roles_count: Optional[int] = 0  # optional: kuonyesha idadi ya roles

    class Config:
        orm_mode = True
