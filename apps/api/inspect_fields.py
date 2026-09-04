import requests
import json

API_KEY = "579b464db66ec23bdd0000015655d20116c7455865b99496afb21bf1"
RESOURCE_ID = "9ef84268-d588-465a-a308-a864a43d0070"

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
            print("Fields in 9ef84268:")
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
