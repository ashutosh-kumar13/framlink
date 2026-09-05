import requests
import json
from config import API_KEY

def check():
    api_key = API_KEY
    rid = "35985678-0d79-46b4-9ed6-6f13308a1d24"
    url = f"https://api.data.gov.in/resource/{rid}"
    params = {"api-key": api_key, "format": "json", "limit": 1}

    print(f"Requesting: {url}")
    try:
        r = requests.get(url, params=params, timeout=10)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            print("API is ONLINE.")
            # print(json.dumps(r.json(), indent=2))
        else:
            print(f"API Error: {r.text}")
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    check()
