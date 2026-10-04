import json
import paho.mqtt.client as mqtt

from app.core.mqtt_config import MQTT_BROKER, MQTT_PORT

mqtt_client = mqtt.Client(client_id="automation-engine")
mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
mqtt_client.loop_start()


def publish_device_action(tenant_id: int, device_id: int, payload: dict):
    topic = f"smarthome/tenants/{tenant_id}/devices/{device_id}/commands"
    mqtt_client.publish(topic, json.dumps(payload))
