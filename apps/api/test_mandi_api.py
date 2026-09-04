import requests
import json
import os

# Using the key from your reference project which is known to work
TEST_API_KEY = "579b464db66ec23bdd0000015655d20116c7455865b99496afb21bf1"
RESOURCE_ID = "9ef84268-d588-465a-a308-a864a43d0070"

def verify_fix():
    url = f"https://api.data.gov.in/resource/{RESOURCE_ID}"
    params = {
        "api-key": TEST_API_KEY,
        "format": "json",
        "limit": 5,
        "filters[state]": "Uttar Pradesh",
        "filters[commodity]": "Wheat"
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    }

    print(f"--- 📡 Testing Connection to Stable 2026 Resource ---")
    print(f"Target: Wheat in Uttar Pradesh")

    try:
        response = requests.get(url, params=params, headers=headers, timeout=60)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            records = data.get('records', [])
            if records:
                print(f"✅ SUCCESS! Found {len(records)} records.")
                for r in records[:3]:
                    market = r.get('market') or r.get('Market')
                    price = r.get('modal_price') or r.get('Modal_Price')
                    date = r.get('arrival_date') or r.get('Arrival_Date')
                    print(f"   - {market}: ₹{price} ({date})")
                return True
            else:
                print("⚠️ Connected, but no records found. Check if filters are correct.")
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
    return False

if __name__ == "__main__":
    verify_fix()
