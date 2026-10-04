from sqlalchemy.orm import Session

from app.automation.evaluators import evaluate_condition
from app.automation.actions import execute_action
from app.db.postgres import SessionLocal
from app.enum.TriggerType import TriggerType
from app.models.automation_rule import AutomationRule


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def process_sensor_event(sensor, value):
    db: Session = SessionLocal()

    try:
        rules = (
            db.query(AutomationRule)
            .filter(
                AutomationRule.enabled == True,
                AutomationRule.trigger_type == TriggerType.SENSOR,
                AutomationRule.trigger_sensor_id == sensor.id,
            )
            .all()
        )

        for rule in rules:
            if evaluate_condition(
                rule.condition_operator,
                value,
                rule.trigger_value,
            ):
                execute_action(rule)

    except Exception as e:
        print("❌ Automation engine error:", e)

    finally:
        db.close()
