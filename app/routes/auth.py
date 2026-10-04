from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.dependencies.auth import get_db, oauth2_scheme
from app.schemas.user import Token, LoginAttemptRequest, ResetRequest
from app.services.auth_service import (
    login_user,
    record_failed_attempt,
    reset_failed_attempts,
    logout_user,
    request_password_reset_service
)

router = APIRouter()


@router.post("/login", response_model=Token)
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    request: Request = None
):
    token = login_user(form.username, form.password, db, request)
    return {"access_token": token, "token_type": "bearer"}


@router.post("/failed-attempt")
def failed_attempt(data: LoginAttemptRequest, db: Session = Depends(get_db)):
    return record_failed_attempt(data, db)


@router.post("/reset-failed-attempts")
def reset_attempts(data: LoginAttemptRequest, db: Session = Depends(get_db)):
    return reset_failed_attempts(data, db)


@router.post("/logout")
def logout(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    return logout_user(token, db)


@router.post("/request-password-reset")
def request_password_reset(
    data: ResetRequest,
    db: Session = Depends(get_db),
    request: Request = None
):
    return request_password_reset_service(data, db, request)
