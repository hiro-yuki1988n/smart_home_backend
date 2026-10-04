# app/utils/initializer.py
from contextlib import contextmanager

from sqlalchemy.orm import Session
from app.core.security import hash_password
from app.db.mongo import db
from app.db.postgres import SessionLocal
from app.models.role import Permission, Role
from app.models.tenant import Tenant
from app.models.user import User


PERMISSION_NAMES = [
    "CREATE_DEVICE",
    "DELETE_DEVICE",
    "UPDATE_DEVICE",
    "VIEW_DEVICE",
    "CREATE_USER",
    "UPDATE_USER",
    "DELETE_USER",
    "VIEW_USER",
    "VIEW_USERS",
    "VIEW_MY_USERS",
    "RESET_DEVICE",
    "MANAGE_TENANTS",
    "VIEW_TENANTS",
    "SAVE_ROLE",
    "VIEW_ROLES",
    "VIEW_ROLE",
    "DELETE_ROLE",
    "MANAGE_ROLES",
    "VIEW_USER_DETAILS",
    "VIEW_PERMISSIONS",
    "VIEW_AUDIT_LOGS",
    "CREATE_SENSOR",
    "UPDATE_SENSOR",
    "VIEW_SENSORS",
    "VIEW_SENSOR",
]


def seed_defaults(db: Session):
    try:
        # 1. Tenant
        tenant = db.query(Tenant).filter_by(name="Default Tenant").first()
        if not tenant:
            tenant = Tenant(name="Default Tenant", description="System default tenant", address="Dodoma")
            db.add(tenant)
            db.flush()

        # 2. Role
        role = db.query(Role).filter_by(name="Admin").first()
        if not role:
            role = Role(
                name="Admin",
                description="Administrator role with all permissions",
                created_by="system"
            )
            db.add(role)
            db.flush()

        # 3. User
        user = db.query(User).filter_by(username="admin").first()
        if not user:
            user = User(
                name="Super Admin",
                username="admin",
                email="admin@smarthome.local",
                phone_number="255700000000",
                hashed_password=hash_password("admin123"),
                tenant_id=tenant.id,
                role_id=role.id,
                created_by="system",
                failed_attempts=0
            )
            db.add(user)

        # 4. Permissions
        existing_perms = {p.name for p in db.query(Permission).all()}
        new_perms = [
            Permission(
                name=name,
                description=f"Permission to {name.replace('_', ' ').title()}",
                created_by="system"
            )
            for name in PERMISSION_NAMES if name not in existing_perms
        ]
        if new_perms:
            db.add_all(new_perms)
            print(f"✅ Seeded {len(new_perms)} new permissions")
        else:
            print("✅ All permissions already exist")

        db.flush()

        # Assign all permissions to the role
        role.permissions = db.query(Permission).all()

        db.commit()
        print("✅ Default Tenant, Role, and Admin User seeded successfully!")

    except Exception as e:
        db.rollback()
        print(f"❌ Seeding failed: {e}")


if __name__ == "__main__":
    seed_defaults(db)
