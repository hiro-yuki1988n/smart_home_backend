import json
import random
import time
from datetime import datetime

import paho.mqtt.client as mqtt

# ---------------- MQTT CONFIG ----------------
MQTT_BROKER = "localhost"   # badilisha kama broker iko remote
MQTT_PORT = 1883
MQTT_KEEPALIVE = 60

TENANT_ID = 1
DEVICE_ID = 12
PUBLISH_INTERVAL = 5  # seconds


# ---------------- SENSOR SIMULATION ----------------
def generate_temperature():
    return round(random.uniform(22.0, 35.0), 2)


def generate_humidity():
    return round(random.uniform(40.0, 80.0), 2)


def generate_motion():
    return random.choice([True, False])


def generate_light_level():
    return random.randint(100, 800)  # lux


SENSORS = {
    "TEMPERATURE": generate_temperature,
    "HUMIDITY": generate_humidity,
    "MOTION": generate_motion,
    "LIGHT_LEVEL": generate_light_level,
}


# ---------------- MQTT CALLBACKS ----------------
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connected to MQTT Broker")
    else:
        print(f"❌ Failed to connect, return code {rc}")


# ---------------- MAIN PUBLISHER ----------------
def main():
    client = mqtt.Client(client_id=f"fake-device-{DEVICE_ID}")
    client.on_connect = on_connect

    client.connect(MQTT_BROKER, MQTT_PORT, MQTT_KEEPALIVE)
    client.loop_start()

    try:
        while True:
            for sensor_type, generator in SENSORS.items():
                topic = (
                    f"smarthome/tenants/{TENANT_ID}/"
                    f"devices/{DEVICE_ID}/"
                    f"sensors/{sensor_type}"
                )

                payload = {
                    "sensor_type": sensor_type,
                    "value": generator(),
                    "timestamp": datetime.utcnow().isoformat()
                }

                client.publish(topic, json.dumps(payload))
                print(f"📡 Published → {topic}: {payload}")

            time.sleep(PUBLISH_INTERVAL)

    except KeyboardInterrupt:
        print("🛑 Stopping publisher...")
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
