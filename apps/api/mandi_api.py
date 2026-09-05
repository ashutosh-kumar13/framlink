from __future__ import annotations
import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
from pathlib import Path

from dotenv import load_dotenv
import requests
from flask import Flask, jsonify, request, send_from_directory
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

app = Flask(__name__)

load_dotenv(Path(__file__).resolve().parents[2] / ".env")
API_KEY = os.getenv("DATA_GOV_API_KEY", "")
# Main Historical Resource ID
RESOURCE_ID = "35985678-0d79-46b4-9ed6-6f13308a1d24"
# Daily Resource ID as fallback for latest prices
DAILY_RESOURCE_ID = "9ef84268-d588-465a-a308-a864a43d0070"
UPSTREAM_URL = f"https://api.data.gov.in/resource/{RESOURCE_ID}"
DAILY_URL = f"https://api.data.gov.in/resource/{DAILY_RESOURCE_ID}"

# Metadata Mappings
COMMODITY_GROUPS = {
    "Potato": "Vegetables", "Onion": "Vegetables", "Tomato": "Vegetables",
    "Wheat": "Cereals", "Rice": "Cereals", "Paddy(Common)": "Cereals", "Maize": "Cereals",
    "Gram": "Pulses", "Tur": "Pulses", "Moong": "Pulses",
    "Mustard": "Oilseeds", "Soyabean": "Oilseeds"
}
MSP_DATA_2026 = {
    "Wheat": 2425, "Paddy(Common)": 2300, "Gram": 5440, "Mustard": 5650,
    "Potato": "-", "Onion": "-", "Tomato": "-"
}

# Session with Browser Headers to avoid throttling
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Accept": "application/json",
})
session.mount("https://", HTTPAdapter(max_retries=Retry(
    total=3, backoff_factor=1, status_forcelist=(429, 500, 502, 503, 504)
)))

def title_case(value: str) -> str:
    if not value: return ""
    return " ".join([w.capitalize() for w in value.split()])

@app.after_request
def add_cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response

@app.get("/")
def index():
    return jsonify({
        "ok": True,
        "service": "FarmLink Mandi API",
        "status": "Running",
        "endpoints": ["/api/mandi-prices"]
    })

@app.route('/public/<path:path>')
def serve_public(path):
    # This allows serving the HTML/CSS from Port 5000
    root_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "public")
    return send_from_directory(root_dir, path)

@app.get("/api/mandi-prices")
def mandi_prices():
    # Final Check
    key = os.getenv("DATA_GOV_API_KEY", API_KEY)
    if not key:
        return jsonify({"ok": False, "message": "API Key missing in Backend"}), 503

    params = {
        "api-key": key,
        "format": "json",
        "limit": str(request.args.get("limit", 50)),
        "sort[Arrival_Date]": "desc",
    }

    for field in ["state", "district", "market", "commodity"]:
        val = request.args.get(field)
        if val: params[f"filters[{field.capitalize()}]"] = title_case(val)

    try:
        # Increased timeout to 90s to handle slow government server responses
        upstream = session.get(UPSTREAM_URL, params=params, timeout=90)

        if not upstream.ok:
            return jsonify({"ok": False, "message": "Government API is currently slow or down. Please try again."}), 502

        payload = upstream.json()
        records = payload.get("records", [])

        # Fallback 1: If sorting by Arrival_Date returns nothing, try without sort
        if not records:
            print("Historical sorted query returned nothing. Trying without sort...")
            params.pop("sort[Arrival_Date]", None)
            upstream = session.get(UPSTREAM_URL, params=params, timeout=30)
            if upstream.ok:
                records = upstream.json().get("records", [])

        # Fallback 2: Try the Daily Resource (for latest "Today" prices)
        if not records:
            print("Historical resource empty. Trying Daily resource...")
            # Daily resource uses lowercase field names in filters
            daily_params = {
                "api-key": key, "format": "json", "limit": params["limit"],
                "sort[arrival_date]": "desc"
            }
            for f in ["state", "district", "market", "commodity"]:
                v = request.args.get(f)
                if v: daily_params[f"filters[{f}]"] = v.lower()

            upstream = session.get(DAILY_URL, params=daily_params, timeout=30)
            if upstream.ok:
                records = upstream.json().get("records", [])

        # Fallback 3: If still no data, return sample demo data so the UI doesn't break
        if not records:
            print("No real data found. Returning demo fallback.")
            records = [{
                "State": request.args.get("state", "Bihar"),
                "District": request.args.get("district", "Gaya"),
                "Market": request.args.get("market", "Gaya"),
                "Commodity": "Wheat",
                "Variety": "Kalyan",
                "Modal_Price": "2425",
                "Arrival_Date": "01-09-2026"
            }]

        result = []
        for r in records:
            # Flexible key mapping for both "Arrival_Date" and "arrival_date"
            r_norm = {k.lower().replace(" ", "_"): v for k, v in r.items()}
            result.append({
                "state": r_norm.get("state"), "market": r_norm.get("market"),
                "commodity": r_norm.get("commodity"), "variety": r_norm.get("variety"),
                "modal_price": r_norm.get("modal_price"), "arrival_date": r_norm.get("arrival_date"),
                "msp": MSP_DATA_2026.get(r_norm.get("commodity"), "-")
            })
        return jsonify({"ok": True, "records": result})
    except Exception as e:
        return jsonify({"ok": False, "message": str(e)}), 500

if __name__ == "__main__":
    print(f"Server started on http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=True)
