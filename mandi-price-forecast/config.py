import os
from dotenv import load_dotenv

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, "..", ".env"))

# API Settings (Switching to the main Historical Resource ID)
API_KEY = os.getenv("DATA_GOV_API_KEY", "")
RESOURCE_ID = "35985678-0d79-46b4-9ed6-6f13308a1d24"

# Metadata Mappings for UI
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

# Default Filters
STATE = "Uttar Pradesh"
DISTRICT = "Lucknow"
MANDI = "Lucknow"
COMMODITY = "Wheat"
VARIETY = None

# Data Fetching Settings
MAX_RECORDS = 3000 # Increased for 2023-2026 coverage
HISTORY_YEARS = 3
MIN_YEAR = 2023

# File Paths
RAW_DATA_PATH = os.path.join(BASE_DIR, "data", "raw_market_data.csv")
# Legacy support: default clean path (dynamic paths preferred via get_data_paths)
CLEAN_DATA_PATH = os.path.join(BASE_DIR, "data", "clean_market_data.csv")
FORECAST_DATA_PATH = os.path.join(BASE_DIR, "data", "forecast.csv")
MODEL_PATH = os.path.join(BASE_DIR, "model", "model.pkl")

def get_data_paths(state, district, market, commodity):
    tag = f"{state}_{district}_{market}_{commodity}".lower().replace(" ", "_")
    return {
        "raw": os.path.join(BASE_DIR, "data", f"raw_{tag}.csv"),
        "clean": os.path.join(BASE_DIR, "data", f"clean_{tag}.csv"),
        "model": os.path.join(BASE_DIR, "model", f"model_{tag}.pkl")
    }
METRICS_PATH = os.path.join(BASE_DIR, "reports", "metrics.txt")
HISTORICAL_PLOT_PATH = os.path.join(BASE_DIR, "reports", "historical_price.png")
BACKTEST_PLOT_PATH = os.path.join(BASE_DIR, "reports", "backtest.png")
