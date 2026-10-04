from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = "mongodb://mongodb:27017"
client = AsyncIOMotorClient(MONGO_URL)
db = client.smarthome

# Collection: sensor_readings
# Example doc:
# { "sensor": "temperature", "value": 28.4, "timestamp": "2025-09-14T10:00:00Z" }
