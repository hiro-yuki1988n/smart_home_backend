from sqlalchemy.orm import Session
from fastapi import HTTPException, Request
from datetime import datetime, timedelta
import random

from app.core.security import verify_password, create_access_token, get_user_from_token
from app.models.user import User, BlacklistedToken, PasswordResetToken, PasswordResetOTP
from app.schemas.user import LoginAttemptRequest, ResetRequest
from app.utils.audit_logger import log_activity
from app.utils.mailer import send_email
from app.utils.sms import send_sms
from app.dependencies.auth import generate_token

MAX_ATTEMPTS = 5
LOCKOUT_MINUTES = 15


def login_user(username: str, password: str, db: Session, request: Request):
    user = db.query(User).filter(User.username == username).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials supplied")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="User is inactive")

    if user.lockout_until and user.lockout_until > datetime.utcnow():
        raise HTTPException(
            status_code=403,
            detail="Account is temporarily locked. Try again later."
        )

    if not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials supplied")

    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "tenant_id": user.tenant_id,
            "role": user.role.name if user.role else None
        }
    )

    log_activity(
        db=db,
        user=user,
        action="LOGIN",
        description=f"User {user.username} logged in successfully",
        request=request
    )

    return access_token


def record_failed_attempt(data: LoginAttemptRequest, db: Session):
    user = db.query(User).filter(User.username == data.username).first()
    if not user:
        return {"message": "User not found"}

    user.failed_attempts = (user.failed_attempts or 0) + 1

    if user.failed_attempts >= 5:
        user.lockout_until = datetime.utcnow() + timedelta(minutes=1)
        db.commit()
        return {"message": "Account locked for 1 minute due to too many failed attempts"}

    db.commit()
    return {"message": "Failed attempt recorded"}


def reset_failed_attempts(data: LoginAttemptRequest, db: Session):
    user = db.query(User).filter(User.username == data.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.failed_attempts = 0
    user.lockout_until = None
    db.commit()

    return {"message": "Failed attempts reset successfully"}


def logout_user(token: str, db: Session):
    user = get_user_from_token(token, db)
    if not user:
        return {"message": "Invalid token or user not found"}

    existing = db.query(BlacklistedToken).filter(
        BlacklistedToken.token == token
    ).first()

    if not existing:
        db.add(BlacklistedToken(token=token, user_id=user.id))
        db.commit()

    return {"message": "Successfully logged out"}


def request_password_reset_service(data: ResetRequest, db: Session, request: Request):
    identifier = data.identifier
    user = db.query(User).filter(
        (User.email == identifier) | (User.phone_number == identifier)
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    now = datetime.utcnow()

    if (user.failed_attempts or 0) >= MAX_ATTEMPTS:
        if user.lockout_until and user.lockout_until > now:
            remaining = (user.lockout_until - now).seconds // 60
            raise HTTPException(
                status_code=403,
                detail=f"Too many attempts. Try again in {remaining} minutes"
            )
        else:
            user.failed_attempts = 0
            user.lockout_until = None
            db.commit()

    if "@" in identifier:
        reset_token = generate_token()
        db.add(PasswordResetToken(
            user_id=user.id,
            token=reset_token,
            expires_at=now + timedelta(hours=1)
        ))
        db.commit()

        send_email(
            user.email,
            "Password Reset Request",
            f"Reset link token: {reset_token}"
        )

        log_activity(
            db=db,
            user=user,
            action="PASSWORD RESET REQUEST",
            description="Password reset via email",
            request=request
        )

        return {"message": "Password reset link sent"}

    otp = "".join(str(random.randint(0, 9)) for _ in range(6))
    db.add(PasswordResetOTP(
        user_id=user.id,
        otp_code=otp,
        expires_at=now + timedelta(minutes=10)
    ))
    db.commit()

    send_sms(user.phone_number, f"Your OTP code is {otp}")

    return {"message": "OTP sent to phone"}
