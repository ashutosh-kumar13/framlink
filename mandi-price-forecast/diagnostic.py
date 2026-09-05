import requests
import os
import sys
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

def test_mandi_api():
    api_key = os.getenv("DATA_GOV_API_KEY", "")
    resource_id = "35985678-0d79-46b4-9ed6-6f13308a1d24"
    url = f"https://api.data.gov.in/resource/{resource_id}"
    params = {"api-key": api_key, "format": "json", "limit": 1}

    print(f"Testing Mandi API: {url}")
    try:
        resp = requests.get(url, params=params, timeout=15)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"Success! Records found: {len(data.get('records', []))}")
        else:
            print(f"Failed: {resp.text}")
    except Exception as e:
        print(f"Error: {e}")

def test_weather_api():
    url = "https://api.open-meteo.com/v1/forecast"
    params = {"latitude": 26.83928, "longitude": 80.92313, "current_weather": "true"}
    print(f"\nTesting Weather API: {url}")
    try:
        resp = requests.get(url, params=params, timeout=15)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            print(f"Success! Current temp: {resp.json().get('current_weather', {}).get('temperature')}°C")
        else:
            print(f"Failed: {resp.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_mandi_api()
    test_weather_api()
