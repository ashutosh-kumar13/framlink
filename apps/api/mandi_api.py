"""FarmLink Agmarknet proxy.

Run locally:
  set DATA_GOV_API_KEY=your-key
  python mandi_api.py
"""
from __future__ import annotations

import os
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from flask import Flask, jsonify, request
from urllib3.util.retry import Retry

app = Flask(__name__)

RESOURCE_ID = "9ef84268-d588-465a-a308-a864a43d0070"
UPSTREAM_URL = f"https://api.data.gov.in/resource/{RESOURCE_ID}"
API_KEY = os.getenv("DATA_GOV_API_KEY", "")
TIMEOUT_SECONDS = 60

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

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
})
session.mount("https://", HTTPAdapter(max_retries=Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=(429, 500, 502, 503, 504),
    allowed_methods=("GET",),
)))


def title_case(value: str) -> str:
    """Normalise data.gov.in's case-sensitive filter values."""
    return " ".join(word.capitalize() for word in value.strip().split())


def cors(response):
    response.headers["Access-Control-Allow-Origin"] = os.getenv("CORS_ORIGIN", "http://127.0.0.1:5500")
    response.headers["Vary"] = "Origin"
    return response


def api_error(message: str, status: int):
    return cors(jsonify({"ok": False, "message": message})), status


@app.after_request
def add_cors(response):
    return cors(response)


@app.get("/health")
def health():
    return jsonify({"ok": True, "service": "FarmLink mandi proxy"})


@app.get("/")
def index():
    """Useful landing response when the local Flask URL is opened directly."""
    return cors(jsonify({
        "ok": True,
        "service": "FarmLink Agmarknet proxy is running",
        "api": "/api/mandi-prices?state=Uttar%20Pradesh&commodity=Wheat",
        "frontend": "http://127.0.0.1:5500/farmlink-platform/apps/web/pages/seller/seller-mandi-prices.html",
    }))


@app.get("/api/mandi-prices")
def mandi_prices():
    if not API_KEY:
        return api_error("Server configuration missing: DATA_GOV_API_KEY", 503)

    params: dict[str, str] = {
        "api-key": API_KEY,
        "format": "json",
        "limit": str(min(max(request.args.get("limit", 50, type=int), 1), 100)),
    }
    # Current Daily Price resource (9ef84268) uses lowercase field names in filters.
    for source, field in (("state", "state"), ("district", "district"), ("market", "market"), ("commodity", "commodity")):
        value = request.args.get(source, "").strip()
        if value:
            params[f"filters[{field}]"] = title_case(value)

    try:
        upstream = session.get(UPSTREAM_URL, params=params, timeout=TIMEOUT_SECONDS)
    except requests.Timeout:
        return api_error("Server Busy — मंडी सर्वर ने समय पर जवाब नहीं दिया। कृपया फिर कोशिश करें।", 504)
    except requests.RequestException:
        return api_error("मंडी सेवा से कनेक्शन नहीं हो सका। कृपया फिर कोशिश करें।", 502)

    if upstream.status_code in (502, 503, 504):
        return api_error("Server Busy — सरकारी मंडी सर्वर अस्थायी रूप से व्यस्त है।", 503)
    if not upstream.ok:
        return api_error("मंडी डेटा अभी उपलब्ध नहीं है।", 502)

    try:
        payload: dict[str, Any] = upstream.json()
    except ValueError:
        return api_error("मंडी सेवा से अमान्य उत्तर मिला।", 502)

    records = payload.get("records", [])

    # Aggregation logic for 3-day trend (govt-peer style)
    # We group by (State, Market, Commodity, Variety)
    grouped = {}
    for row in records:
        key = (row.get("state"), row.get("market"), row.get("commodity"), row.get("variety"))
        if key not in grouped:
            grouped[key] = {
                "state": row.get("state"),
                "market": row.get("market"),
                "commodity": row.get("commodity"),
                "variety": row.get("variety"),
                "district": row.get("district"),
                "group": COMMODITY_GROUPS.get(row.get("commodity"), "Others"),
                "msp": MSP_DATA_2026.get(row.get("commodity"), "-"),
                "prices": {} # date -> price
            }

        date_str = row.get("arrival_date")
        price = row.get("modal_price")
        if date_str and price:
            grouped[key]["prices"][date_str] = price

    # Format the response to include the trend
    result = []
    for item in grouped.values():
        # Get last 3 dates available in the entire dataset for this commodity context
        sorted_dates = sorted(item["prices"].keys(), reverse=True)
        item["trends"] = [
            {"date": d, "price": item["prices"][d]} for d in sorted_dates[:3]
        ]
        # Current price is the latest one
        item["modal_price"] = item["prices"][sorted_dates[0]] if sorted_dates else "-"
        item["arrival_date"] = sorted_dates[0] if sorted_dates else "-"
        result.append(item)

    return jsonify({"ok": True, "records": result, "total": payload.get("total", len(result))})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
