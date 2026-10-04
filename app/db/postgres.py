# app/db/postgres.py
import importlib
import pkgutil

# from app.base_entity import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

from app.db.base import Base

POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "alhiro.com1988n")
POSTGRES_DB = os.getenv("POSTGRES_DB", "smarthome")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", 5432)

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"


engine = create_engine(DATABASE_URL, echo=True)  # echo=True kuonyesha SQL inayo-run
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    import app.models

    print("🔨 Creating all tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ All tables created successfully")