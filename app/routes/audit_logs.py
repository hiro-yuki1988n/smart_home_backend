from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.routes.users import get_db
from app.models.AuditLog import AuditLog
from app.models.user import User
from app.core.security import get_current_user
from app.core.security import permission_required

router = APIRouter()


@router.get("/activities")
@permission_required("VIEW_AUDIT_LOGS")
def get_activities(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    logs = (
        db.query(AuditLog)
        .order_by(AuditLog.created_at.desc())
        .limit(50)
        .all()
    )
    return [
        {
            "id": log.id,
            "user_id": log.user_id,
            "username": log.username,
            "action": log.action,
            "description": log.description,
            "os": log.os,
            "browser": log.browser,
            "user_agent": log.user_agent,
            "ip_address": log.ip_address,
            "created_at": log.created_at
        }
        for log in logs
    ]
