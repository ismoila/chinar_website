import requests
from django.conf import settings

DEVSMS_TOKEN = settings.DEVSMS_TOKEN
BASE_URL = "https://devsms.uz/api"

headers = {
    "Authorization": f"Bearer {DEVSMS_TOKEN}",
    "Content-Type": "application/json"
}


def send_sms(phone: str, message: str) -> dict:
    phone = phone.replace('+', '')
    try:
        response = requests.post(
            f"{BASE_URL}/send_sms.php",
            headers=headers,
            json={
                "phone": phone,
                "message": message
            },
            timeout=15,
        )
        data = response.json()
        print("DEVSMS javob:", response.status_code, data)   # sinov uchun log
        return data
    except Exception as e:
        print(f"SMS xato: {e}")
        return {"success": False, "error": str(e)}

def get_balance() -> dict:
    """DevSMS hisobidagi balans va statistikani qaytaradi."""
    try:
        response = requests.get(
            f"{BASE_URL}/get_balance.php",
            headers=headers,
            timeout=15,
        )
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}
