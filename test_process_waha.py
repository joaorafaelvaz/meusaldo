import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.database import SessionLocal
from backend.main import process_waha_message

payload = {
    "payload": {
        "body": "Gastei 50 no mercado hoje",
        "from": "5511999999999@c.us",
        "fromMe": False
    }
}

db = SessionLocal()
try:
    process_waha_message(payload, db)
finally:
    db.close()
