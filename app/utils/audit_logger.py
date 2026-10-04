from app.models.AuditLog import AuditLog
from datetime import datetime
from user_agents import parse as parse_user_agent
from fastapi import Request


def log_activity(db, user=None, action="", description="", request: Request = None):
    """
    Rekodi shughuli yoyote ya user kwenye database
    """
    ip_address = None
    user_agent_str = None
    os_name = None
    browser_name = None

    if request:
        ip_address = request.client.host if request.client else None
        user_agent_str = request.headers.get("user-agent", "")
        user_agent = parse_user_agent(user_agent_str)
        os_name = user_agent.os.family
        browser_name = user_agent.browser.family

    log = AuditLog(
        user_id=user.id if user else None,
        username=user.username if user else None,
        action=action,
        description=description,
        ip_address=ip_address,
        user_agent=user_agent_str,
        os=os_name,
        browser=browser_name,
        created_at=datetime.utcnow(),
    )

    db.add(log)
    db.commit()
