# app/core/security.py

from datetime import datetime, timedelta
from functools import wraps

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from pymongo.asynchronous import settings
from sqlalchemy.orm import Session, joinedload
from starlette import status
from starlette.status import HTTP_403_FORBIDDEN

from app.dependencies.auth import get_db
from app.models.role import Role
from app.models.user import BlacklistedToken, User

# password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "SUPER_SECRET_KEY"  # 👉 badilisha na env variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# OAuth2PasswordBearer inarudisha moja kwa moja token string
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# def create_access_token(data: dict, expires_delta: timedelta = None):
#     to_encode = data.copy()
#
#     # Ensure sub is stored as integer
#     if "sub" in to_encode:
#         to_encode["sub"] = int(to_encode["sub"])
#
#     expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
#     to_encode.update({"exp": expire})
#
#     return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_user_from_token(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 1. Check blacklist
    if db.query(BlacklistedToken).filter(BlacklistedToken.token == token).first():
        raise HTTPException(status_code=401, detail="Token has been blacklisted")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception

        # Convert sub → int
        user_id = int(user_id)

    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    return user


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Blacklist check
    if db.query(BlacklistedToken).filter(BlacklistedToken.token == token).first():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked"
        )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception

        # user_id = int(user_id)

    except JWTError:
        raise credentials_exception

    user = (
        db.query(User)
        .options(joinedload(User.role).joinedload(Role.permissions))
        .filter(User.id == user_id, User.is_deleted == False)
        .first()
    )

    if user is None:
        raise credentials_exception

    return user


def get_current_tenant(current_user: User = Depends(get_current_user)):
    if not current_user.tenant_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tenant not assigned")
    return current_user.tenant_id


def permission_required(permission_name: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):

            current_user: User = kwargs.get("current_user")

            if not current_user:
                raise HTTPException(
                    status_code=401,
                    detail="Authentication needed"
                )

            # Admin override
            if getattr(current_user, "is_admin", False):
                return (
                    await func(*args, **kwargs)
                    if hasattr(func, "__await__")
                    else func(*args, **kwargs)
                )

            # Check role
            if not current_user.role:
                raise HTTPException(
                    status_code=403,
                    detail="No role assigned to this account"
                )

            perms = [p.name for p in current_user.role.permissions]

            if permission_name not in perms:
                raise HTTPException(
                    status_code=403,
                    detail=f"You do not have '{permission_name}' permission"
                )

            return (
                await func(*args, **kwargs)
                if hasattr(func, "__await__")
                else func(*args, **kwargs)
            )

        return wrapper

    return decorator

