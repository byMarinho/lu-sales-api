import requests

from app.core.config import settings


def send_whatsapp_message(phone_number: str, message: str):
    url = f"{settings.WA_API_URL}/message/sendText/{settings.WA_INSTANCE_NAME}"

    headers = {
        "apikey": f"{settings.WA_AUTHENTICATION_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "number": phone_number,
        "textMessage": {"text": message},
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code not in (200, 201, 202):
        raise Exception(f"Failed to send message: {response.text}")
    data = response.json()
    if data.get("status") not in ("PENDING", "SENT", None):
        raise Exception(f"Failed to send message: {response.text}")
