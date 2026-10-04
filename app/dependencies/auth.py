import random
import string

from fastapi.security import OAuth2PasswordBearer

from app.db.postgres import SessionLocal

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def generate_token(length=32):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

