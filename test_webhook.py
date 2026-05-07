import json
import requests

payload = {
    "payload": {
        "body": "Gastei 50 no mercado hoje",
        "from": "5511999999999@c.us",
        "fromMe": False
    }
}

try:
    res = requests.post("http://127.0.0.1:8015/api/webhooks/waha", json=payload)
    print(res.status_code)
    print(res.text)
except Exception as e:
    print(f"Error calling api: {e}")
