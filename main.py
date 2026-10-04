# app/main.py
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy.orm import Session
from fastapi.staticfiles import StaticFiles
from app.db.auto_migrate import run_auto_migration
from app.db.postgres import init_db, SessionLocal
from app.routes import auth, users, devices, sensors, admin_roles, tenants, audit_logs
from app.services.mqtt_client import start_mqtt_consumer
from app.utils.initializer import seed_defaults


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    This block runs automatically when FastAPI starts and stops.
    Perfect place for DB init, migrations, and seeding.
    """
    db: Session = SessionLocal()

    try:
        print("🚀 Starting Smart Home Backend...")

        # 1️⃣ Run migrations automatically (only in dev)
        try:
            if os.getenv("AUTO_MIGRATE", "false").lower() == "true":
                run_auto_migration()
        except Exception as e:
            print(f"⚠️ Auto migration failed: {e}")

        # 2️⃣ Ensure tables exist (in case of fresh DB)
        init_db()

        # 3️⃣ Seed default data (roles, admin, etc.)
        seed_defaults(db)

        print("🚀 Starting MQTT consumer...")
        start_mqtt_consumer()

        print("✅ Application startup completed.")
        yield

    except Exception as e:
        print(f"❌ Lifespan startup failed: {e}")

    finally:
        # Clean up resources
        db.close()
        print("🛑 Application shutdown. Database session closed.")


# FastAPI instance
app = FastAPI(
    title="Smart Home Backend",
    lifespan=lifespan
)


# app.mount("/media", StaticFiles(directory="media"), name="media")


# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(devices.router, prefix="/devices", tags=["devices"])
app.include_router(sensors.router, prefix="/sensors", tags=["sensors"])
app.include_router(admin_roles.router, prefix="/admin", tags=["admin"])
app.include_router(tenants.router, prefix="/tenants", tags=["tenants"])
app.include_router(audit_logs.router, prefix="/audit", tags=["Audit Logs"])
app.include_router(sensors.router, prefix="/sensors", tags=["Sensors"])


@app.get("/")
def root():
    return {"message": "Smart Home Backend is running 🚀"}