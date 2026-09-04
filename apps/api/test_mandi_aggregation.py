import requests
import json
import os

API_KEY = "579b464db66ec23bdd0000015655d20116c7455865b99496afb21bf1"

def test_aggregation():
    # Calling our local API proxy
    url = "http://127.0.0.1:5000/api/mandi-prices"
    params = {
        "state": "Uttar Pradesh",
        "commodity": "Potato",
        "limit": 50
    }

    print(f"--- 📡 Testing Aggregated Mandi Proxy ---")
    try:
        response = requests.get(url, params=params, timeout=60)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            records = data.get('records', [])
            if records:
                print(f"✅ SUCCESS! Found {len(records)} aggregated records.")
                for r in records[:2]:
                    print(f"\nCommodity: {r['commodity']} ({r['group']})")
                    print(f"Market:    {r['market']}")
                    print(f"MSP:       {r['msp']}")
                    print(f"Latest:    {r['modal_price']} on {r['arrival_date']}")
                    print(f"Trends:    {r['trends']}")
            else:
                print("⚠️ No records found.")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Failed: {e} (Make sure mandi_api.py is running)")

if __name__ == "__main__":
    test_aggregation()
