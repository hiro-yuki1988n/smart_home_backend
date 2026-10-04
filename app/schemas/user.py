from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter
from pydantic import BaseModel, EmailStr

router = APIRouter()


# ----------------------
# User related schemas
# ----------------------

class UserBase(BaseModel):
    username: str
    name: str
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    tenant_id: Optional[int] = None
    role_id: Optional[int] = None


class UserCreate(UserBase):
    password: str  # only required on create


class UserUpdate(BaseModel):
    username: Optional[str] = None
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    role_id: Optional[int] = None


class PermissionOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        orm_mode = True


class UserOut(UserBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    role_name: Optional[str] = None  # useful to include role name in response
    role_id: Optional[int] = None  # id ya role (tunahitaji kwa delete permission)
    permissions: list[PermissionOut] = []
    is_active: bool  # ← ADD THIS

    class Config:
        orm_mode = True


# ----------------------
# Auth / Token schemas
# ----------------------

class Login(BaseModel):
    username: str
    password: str


class LoginAttemptRequest(BaseModel):
    username: str


class Token(BaseModel):
    access_token: str
    token_type: str


class PasswordChange(BaseModel):
    user_id: Optional[int] = None
    old_password: Optional[str] = None
    new_password: str


class ForgotPasswordRequest(BaseModel):
    email_or_phone: str  # now can handle email or phone for OTP


class EmailResetModel(BaseModel):
    token: str
    new_password: str


class OTPResetModel(BaseModel):
    phone: str
    otp_code: str
    new_password: str


class ResetRequest(BaseModel):
    identifier: str


# ----------------------
# Role / Permission schemas
# ----------------------




class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None


class RoleCreate(RoleBase):
    permission_ids: Optional[List[int]] = []


class RoleUpdate(RoleBase):
    permission_ids: Optional[List[int]] = []


class RoleOut(RoleBase):
    id: int
    permissions: Optional[List[PermissionOut]] = []

    class Config:
        orm_mode = True


class UserDetailsOut(BaseModel):
    id: int
    name: str
    username: str
    email: Optional[str]
    phone_number: Optional[str]
    role: Optional[str]
    permissions: List[str]  # <-- simple list of names
    created_at: datetime

    class Config:
        orm_mode = True
