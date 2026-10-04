import os
import africastalking
from dotenv import load_dotenv

load_dotenv()

AT_USERNAME = os.getenv("AT_USERNAME")
AT_API_KEY = os.getenv("AT_API_KEY")

africastalking.initialize(AT_USERNAME, AT_API_KEY)
sms = africastalking.SMS


def send_sms(phone_number: str, message: str):
    """Tuma SMS kupitia Africa's Talking"""
    try:
        response = sms.send(message, [phone_number])
        print(f"✅ SMS sent to {phone_number}: {response}")
    except Exception as e:
        print(f"❌ SMS send failed: {e}")
