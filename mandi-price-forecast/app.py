import os
import logging
import threading
import time
import requests
from flask import Flask, jsonify, request, render_template, send_from_directory
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from concurrent.futures import ThreadPoolExecutor

# Environment settings
os.environ["OMP_NUM_THREADS"] = "1"

from fetch_data import fetch_mandi_data, title_case
from clean_data import clean_mandi_data
from train import train_final_model
from predict import generate_forecast
from config import (
    API_KEY, DAILY_RESOURCE_ID, PINCODE_RESOURCE_ID, RESOURCE_ID,
    STATE, DISTRICT, MANDI, COMMODITY, FLASK_DEBUG, FLASK_HOST, FLASK_PORT
)

app = Flask(__name__)
executor = ThreadPoolExecutor(max_workers=5)
pipeline_lock = threading.Lock()
logger = logging.getLogger(__name__)

DATA_GOV_URL = "https://api.data.gov.in/resource"

@app.after_request
def add_cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response

# Upstream API session
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
})
session.mount("https://", HTTPAdapter(max_retries=Retry(
    total=5, backoff_factor=2, status_forcelist=(429, 500, 502, 503, 504)
)))

# --- Performance Caching Layer ---
market_cache = {
    "major_crops": {"data": None, "timestamp": 0},
    "details": {} # key: (comm, market, state) -> {data, timestamp}
}
CACHE_TTL = 3600 * 6 # 6 hours

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/market/major-crops')
def get_major_crops():
    """Returns top crops quickly using caching and parallel fetching."""
    now = time.time()
    if market_cache["major_crops"]["data"] and (now - market_cache["major_crops"]["timestamp"] < CACHE_TTL):
        return jsonify({"ok": True, "crops": market_cache["major_crops"]["data"], "cached": True})

    state = request.args.get('state', STATE)
    major_commodities = ["Wheat", "Mustard", "Potato", "Tomato", "Onion", "Rice"]

    def fetch_single_crop(comm):
        params = {
            "api-key": API_KEY, "format": "json", "limit": "2",
            "sort[Arrival_Date]": "desc",
            "filters[State]": title_case(state),
            "filters[Commodity]": title_case(comm)
        }
        try:
            resp = session.get(f"{DATA_GOV_URL}/{RESOURCE_ID}", params=params, timeout=8)
            records = resp.json().get("records", []) if resp.ok else []
            if records:
                latest = float(records[0].get("Modal_Price") or 0)
                prev = float(records[1].get("Modal_Price") or latest) if len(records) > 1 else latest
                change = ((latest - prev) / prev * 100) if prev > 0 else 0
                return {"commodity": comm, "price": latest, "change": round(change, 2), "trend": "up" if change >= 0 else "down"}
        except (ValueError, KeyError, requests.RequestException) as error:
            logger.warning("Crop lookup failed for %s: %s", comm, error)
        return None

    results = list(executor.map(fetch_single_crop, major_commodities))
    filtered_results = [r for r in results if r]

    if filtered_results:
        market_cache["major_crops"] = {"data": filtered_results, "timestamp": now}

    return jsonify({"ok": True, "crops": filtered_results})

@app.route('/api/market/details')
def get_market_details():
    """Consolidated market details with instant caching."""
    state = request.args.get('state', STATE)
    district = request.args.get('district', DISTRICT)
    market = request.args.get('market', MANDI)
    commodity = request.args.get('commodity', COMMODITY)
    if not all(value and value.strip() for value in (state, district, market, commodity)):
        return jsonify({"ok": False, "message": "state, district, market, and commodity are required"}), 400

    cache_key = f"{commodity}_{market}_{state}"
    now = time.time()

    if cache_key in market_cache["details"]:
        cache_entry = market_cache["details"][cache_key]
        if now - cache_entry["timestamp"] < CACHE_TTL:
            return jsonify({"ok": True, "details": cache_entry["data"], "cached": True})

    try:
        # Use quick mode (limit=200) to speed up discovery
        with pipeline_lock:
            fetched, fetch_message = fetch_mandi_data(state, district, market, commodity, limit=200)
            if not fetched:
                return jsonify({"ok": False, "message": fetch_message}), 502
            cleaned, clean_message, _ = clean_mandi_data(state, district, market, commodity)
            if not cleaned:
                return jsonify({"ok": False, "message": clean_message}), 422
            trained, train_message = train_final_model()
            if not trained:
                return jsonify({"ok": False, "message": train_message}), 422
            results, _ = generate_forecast(state=state, district=district, mandi=market, commodity=commodity)
    except Exception as e:
        logger.exception("Forecast pipeline failed")
        return jsonify({"ok": False, "message": f"Pipeline error: {str(e)}"}), 500

    if not results:
        return jsonify({"ok": False, "message": "Data not available"}), 404

    latest_price = results["latest_actual_price"]
    trend = results["trend"]

    # Advice logic
    advice = "Hold"
    prob = 0.65
    reasoning = "Prices are expected to rise based on current market signals."
    if trend == "Downward":
        advice = "Sell"
        prob = 0.75
        reasoning = "Market arrivals are high; prices may dip further."

    response_data = {
        "commodity": commodity,
        "market": market,
        "district": district,
        "latest_price": latest_price,
        "trend": trend,
        "advice": {
            "recommendation": advice,
            "probability": prob,
            "reasoning": reasoning,
            "signals": ["Arrival Volume", "Weather Pattern"]
        },
        "forecast": results["forecast"],
        "history": results["history"][-15:], # Chart history
        "nearby_mandis": [] # Can be populated via proxy
    }

    market_cache["details"][cache_key] = {"data": response_data, "timestamp": now}
    return jsonify({"ok": True, "details": response_data})

@app.route('/api/config', methods=['GET'])
def get_config():
    return jsonify({"state": STATE, "district": DISTRICT, "mandi": MANDI, "commodity": COMMODITY})

# --- Location Discovery Service ---
location_cache = {"states": [], "districts": {}, "markets": {}}

@app.route('/api/locations/states')
def get_states():
    if location_cache["states"]: return jsonify({"ok": True, "states": location_cache["states"]})
    try:
        resp = session.get(f"{DATA_GOV_URL}/{DAILY_RESOURCE_ID}", params={"api-key": API_KEY, "format": "json", "limit": "1000"}, timeout=15)
        records = resp.json().get("records", []) if resp.ok else []
        states = sorted(list(set([r.get("state", "").title() for r in records if r.get("state")])))
        location_cache["states"] = states or ["Bihar", "Uttar Pradesh"]
        return jsonify({"ok": True, "states": location_cache["states"]})
    except requests.RequestException:
        return jsonify({"ok": False}), 502

@app.route('/api/locations/districts')
def get_districts():
    state = request.args.get('state')
    if not state or not state.strip():
        return jsonify({"ok": False, "message": "state is required"}), 400
    if state in location_cache["districts"]: return jsonify({"ok": True, "districts": location_cache["districts"][state]})
    try:
        resp = session.get(f"{DATA_GOV_URL}/{DAILY_RESOURCE_ID}", params={"api-key": API_KEY, "format": "json", "limit": "2000", "filters[state]": state.lower()}, timeout=15)
        records = resp.json().get("records", []) if resp.ok else []
        districts = sorted(list(set([r.get("district", "").title() for r in records if r.get("district")])))
        location_cache["districts"][state] = districts
        return jsonify({"ok": True, "districts": districts})
    except (AttributeError, requests.RequestException):
        return jsonify({"ok": False}), 502

@app.route('/api/locations/markets')
def get_markets():
    state, district = request.args.get('state'), request.args.get('district')
    if not state or not district or not state.strip() or not district.strip():
        return jsonify({"ok": False, "message": "state and district are required"}), 400
    key = (state, district)
    if key in location_cache["markets"]: return jsonify({"ok": True, "markets": location_cache["markets"][key]})
    try:
        resp = session.get(f"{DATA_GOV_URL}/{DAILY_RESOURCE_ID}", params={"api-key": API_KEY, "format": "json", "limit": "1000", "filters[state]": state.lower(), "filters[district]": district.lower()}, timeout=15)
        records = resp.json().get("records", []) if resp.ok else []
        markets = sorted(list(set([r.get("market", "").title() for r in records if r.get("market")])))
        location_cache["markets"][key] = markets
        return jsonify({"ok": True, "markets": markets})
    except (AttributeError, requests.RequestException):
        return jsonify({"ok": False}), 502

@app.route('/api/locations/pincode')
def lookup_pincode():
    pin = request.args.get('pin', '').strip()
    if not pin.isdigit() or len(pin) != 6:
        return jsonify({"ok": False, "message": "pin must contain six digits"}), 400
    try:
        resp = session.get(f"{DATA_GOV_URL}/{PINCODE_RESOURCE_ID}", params={"api-key": API_KEY, "format": "json", "filters[pincode]": pin}, timeout=15)
        if resp.ok: return jsonify({"ok": True, "records": resp.json().get("records", [])})
        return jsonify({"ok": False}), 502
    except requests.RequestException:
        return jsonify({"ok": False}), 502

@app.route('/public/<path:path>')
def serve_public(path):
    root_dir = os.path.join(os.path.dirname(app.root_path), "public")
    return send_from_directory(root_dir, path)

if __name__ == "__main__":
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)
