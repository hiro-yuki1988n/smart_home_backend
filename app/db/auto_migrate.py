# app/db/auto_migrate.py
from alembic import command
from alembic.config import Config

def run_auto_migration():
    alembic_cfg = Config("alembic.ini")
    msg = "Auto migration"
    command.revision(alembic_cfg, message=msg, autogenerate=True)
    command.upgrade(alembic_cfg, "head")
    print("✅ Database schema updated automatically")
