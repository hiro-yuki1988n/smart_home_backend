# app/routes/users.py
from fastapi import APIRouter, Depends, Request, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_user, permission_required
from app.db.postgres import SessionLocal
from app.models.user import User
from app.schemas.user import *
from app.services.user_service import UserService
from app.utils.audit_logger import log_activity

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/register", response_model=UserOut)
@permission_required("CREATE_USER")
def register_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    user = UserService.register_user(db, payload, current_user)

    log_activity(
        db=db,
        user=current_user,
        action="REGISTER USER",
        description=f"Created user {user.username}",
        request=request
    )
    return user


@router.get("/me", response_model=UserOut)
def get_my_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    log_activity(
        db=db,
        user=current_user,
        action="VIEW OWN PROFILE",
        description="Viewed own profile",
        request=request
    )
    return current_user


@router.get("/user_info", response_model=UserOut)
@permission_required("VIEW_USERS")
def get_current_user_info(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    log_activity(
        db=db,
        user=current_user,
        action="VIEW OWN INFO",
        description="Viewed own user info",
        request=request
    )
    return current_user


@router.put("/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    user = UserService.update_user(db, user_id, payload, current_user)

    log_activity(
        db=db,
        user=current_user,
        action="UPDATE USER",
        description=f"Updated user {user.username}",
        request=request
    )
    return user


@router.get("/{user_id}", response_model=UserOut)
@permission_required("VIEW_USERS")
def get_user_info(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    user = UserService.get_user(db, user_id, current_user.tenant_id)

    log_activity(
        db=db,
        user=current_user,
        action="VIEW USER INFO",
        description=f"Viewed user info for user_id={user_id}",
        request=request
    )
    return user


@router.get("/", response_model=list[UserOut])
@permission_required("VIEW_USERS")
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    users = UserService.list_users(db, current_user.tenant_id)

    log_activity(
        db=db,
        user=current_user,
        action="VIEW USERS",
        description="Viewed user list",
        request=request
    )
    return users


@router.post("/change-password")
@permission_required("UPDATE_USER")
def change_password(
    payload: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    UserService.change_password(db, payload, current_user)
    return {"message": "Password updated successfully"}


@router.post("/upload-profile-pic")
async def upload_profile_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    path = UserService.upload_profile_pic(db, current_user, file)
    base_url = str(request.base_url).rstrip("/")

    return {
        "profile_pic": path,
        "profile_pic_url": f"{base_url}/{path}"
    }
