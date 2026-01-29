import requests
from datetime import datetime, timedelta

url = "http://127.0.0.1:8000/api/app/"

# base timestamp
base_time = datetime(2026, 1, 15, 10, 0, 0)

# sample events
events = [
    {"worker_id": "W1", "workstation_id": "S1", "event_type": "working", "confidence": 0.95, "count": 2}, 
    {"worker_id": "W2", "workstation_id": "S2", "event_type": "idle", "confidence": 0.9, "count": 0},
    {"worker_id": "W3", "workstation_id": "S3", "event_type": "product_count", "confidence": 0.98, "count": 5},
    {"worker_id": "W4", "workstation_id": "S4", "event_type": "working", "confidence": 0.92, "count": 0},
    {"worker_id": "W5", "workstation_id": "S5", "event_type": "absent", "confidence": 1.0, "count": 0},
    {"worker_id": "W6", "workstation_id": "S6", "event_type": "product_count", "confidence": 0.97, "count": 8},
    {"worker_id": "W1", "workstation_id": "S1", "event_type": "product_count", "confidence": 0.95, "count": 3},
]


for i, event in enumerate(events):
    # increment timestamp for each event
    event["timestamp"] = (base_time + timedelta(minutes=i*5)).isoformat() + "Z"
    
    response = requests.post(url, json=event)
    
    try:
        print(response.json())
    except Exception as e:
        print("Error decoding JSON:", response.text)
