import json
import threading
from datetime import datetime

import paho.mqtt.client as mqtt
from sqlalchemy.orm import Session

from app.automation.engine import process_sensor_event
from app.core.mqtt_config import (
    MQTT_BROKER,
    MQTT_PORT,
    MQTT_KEEPALIVE,
    MQTT_TOPIC,
)
from app.db.postgres import SessionLocal
from app.models.sensor import Sensor
from app.models.sensor_reading import SensorReading


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class MQTTConsumer:
    def __init__(self):
        self.client = mqtt.Client(client_id="fastapi-mqtt-consumer")

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("✅ MQTT connected")
            client.subscribe(MQTT_TOPIC)
            print(f"📡 Subscribed to {MQTT_TOPIC}")
        else:
            print(f"❌ MQTT connection failed: {rc}")

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        payload = json.loads(msg.payload.decode())

        print(f"📥 Received: {topic} → {payload}")

        self.process_message(topic, payload)

    def process_message(self, topic: str, payload: dict):
        """
        Topic example:
        smarthome/tenants/1/devices/12/sensors/TEMPERATURE
        """
        parts = topic.split("/")

        tenant_id = int(parts[2])
        device_id = int(parts[4])
        sensor_type = parts[6]

        db: Session = SessionLocal()

        try:
            sensor = (
                db.query(Sensor)
                .filter(
                    Sensor.device_id == device_id,
                    Sensor.type == sensor_type
                )
                .first()
            )

            if not sensor:
                print("⚠️ Sensor not found, skipping")
                return

            # Update sensor last state
            sensor.last_value = payload.get("value")
            sensor.last_updated = datetime.utcnow()

            # Save reading
            reading = SensorReading(
                sensor_id=sensor.id,
                value=payload.get("value"),
            )

            db.add(reading)
            db.commit()

            print(f"💾 SensorReading saved for sensor {sensor.id}")

            # 🔥 Trigger automation engine here
            process_sensor_event(sensor, payload.get("value"))

        except Exception as e:
            db.rollback()
            print("❌ Error processing MQTT message:", e)
        finally:
            db.close()

    def start(self):
        self.client.connect(MQTT_BROKER, MQTT_PORT, MQTT_KEEPALIVE)
        self.client.loop_forever()


def start_mqtt_consumer():
    consumer = MQTTConsumer()
    thread = threading.Thread(target=consumer.start, daemon=True)
    thread.start()
