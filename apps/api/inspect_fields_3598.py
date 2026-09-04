import requests
import json
import os

API_KEY = os.getenv("DATA_GOV_API_KEY", "")
RESOURCE_ID = "35985678-0d79-46b4-9ed6-6f13308a1d24"

url = f"https://api.data.gov.in/resource/{RESOURCE_ID}"
params = {
    "api-key": API_KEY,
    "format": "json",
    "limit": 1
}
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
}

try:
    r = requests.get(url, params=params, headers=headers, timeout=60)
    if r.status_code == 200:
        data = r.json()
        if 'records' in data and len(data['records']) > 0:
            print(f"Fields in {RESOURCE_ID}:")
            for k in data['records'][0].keys():
                print(f" - {k}")
            print("\nSample Record:")
            print(json.dumps(data['records'][0], indent=2))
        else:
            print("No records found.")
    else:
        print(f"Error: {r.status_code}")
except Exception as e:
    print(f"Failed: {e}")
