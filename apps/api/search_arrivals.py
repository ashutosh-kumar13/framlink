import requests
import json
import os

API_KEY = os.getenv("DATA_GOV_API_KEY", "")
RESOURCE_ID = "9ef84268-d588-465a-a308-a864a43d0070"

url = f"https://api.data.gov.in/resource/{RESOURCE_ID}"
params = {
    "api-key": API_KEY,
    "format": "json",
    "limit": 100
}
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
}

try:
    r = requests.get(url, params=params, headers=headers, timeout=60)
    if r.status_code == 200:
        records = r.json().get('records', [])
        if records:
            all_keys = set()
            for r in records:
                all_keys.update(r.keys())
            print(f"All keys found in 100 records: {all_keys}")
            # Check for any key that looks like arrival or quantity
            arrival_keys = [k for k in all_keys if 'arriv' in k.lower() or 'qty' in k.lower() or 'ton' in k.lower()]
            print(f"Arrival-like keys: {arrival_keys}")
        else:
            print("No records found.")
except Exception as e:
    print(f"Failed: {e}")
