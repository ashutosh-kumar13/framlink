import requests
import time
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))
api_key = os.getenv("DATA_GOV_API_KEY", "")

def test_api(url, params, label):
    print(f"Testing {label}...")
    start = time.time()
    try:
        resp = requests.get(url, params=params, timeout=30)
        end = time.time()
        print(f"  Status: {resp.status_code}")
        print(f"  Time: {end - start:.2f}s")
        if resp.status_code == 200:
            print(f"  Success! Records: {len(resp.json().get('records', []))}")
        else:
            print(f"  Error: {resp.text[:200]}")
    except Exception as e:
        print(f"  Exception: {e}")

# Mandi API
test_api(
    f"https://api.data.gov.in/resource/35985678-0d79-46b4-9ed6-6f13308a1d24",
    {"api-key": api_key, "format": "json", "limit": 1},
    "Mandi API (Historical)"
)

# Postal API
test_api(
    "https://api.data.gov.in/resource/709e9d78-bf11-487d-93fd-d547d24cc0ef",
    {"api-key": api_key, "format": "json", "limit": 1, "filters[pincode]": "226001"},
    "Postal API"
)

# Weather API
test_api(
    "https://api.open-meteo.com/v1/forecast",
    {"latitude": 26.8, "longitude": 80.9, "current_weather": "true"},
    "Weather API"
)
