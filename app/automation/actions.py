from app.enum.action_type import ActionType
from app.services.mqtt_publisher import publish_device_action


def execute_action(rule):
    payload = {}

    if rule.action_type == ActionType.TURN_ON:
        payload = {"action": "TURN_ON"}

    elif rule.action_type == ActionType.TURN_OFF:
        payload = {"action": "TURN_OFF"}

    elif rule.action_type == ActionType.SET_LEVEL:
        payload = {
            "action": "SET_LEVEL",
            "value": rule.action_payload.get("level"),
        }

    elif rule.action_type == ActionType.SET_TEMPERATURE:
        payload = {
            "action": "SET_TEMPERATURE",
            "value": rule.action_payload.get("temperature"),
        }

    publish_device_action(
        tenant_id=rule.tenant_id,
        device_id=rule.target_device_id,
        payload=payload,
    )
