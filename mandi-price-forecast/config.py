import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

# Base directory
BASE_DIR = Path(__file__).resolve().parent
if load_dotenv:
    load_dotenv(BASE_DIR / ".env")

# API Settings (Switching to the main Historical Resource ID)
API_KEY = os.getenv("DATA_GOV_API_KEY", "")
RESOURCE_ID = os.getenv("DATA_GOV_RESOURCE_ID", "35985678-0d79-46b4-9ed6-6f13308a1d24")
DAILY_RESOURCE_ID = os.getenv("DATA_GOV_DAILY_RESOURCE_ID", "9ef84268-d588-465a-a308-a864a43d0070")
PINCODE_RESOURCE_ID = os.getenv("DATA_GOV_PINCODE_RESOURCE_ID", "709e9d78-bf11-487d-93fd-d547d24cc0ef")

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
STATE = os.getenv("DEFAULT_STATE", "Bihar")
DISTRICT = os.getenv("DEFAULT_DISTRICT", "Gaya")
MANDI = os.getenv("DEFAULT_MANDI", "Gaya")
COMMODITY = os.getenv("DEFAULT_COMMODITY", "Wheat")
VARIETY = os.getenv("DEFAULT_VARIETY") or None

# Data Fetching Settings
MAX_RECORDS = int(os.getenv("MAX_RECORDS", "5000"))
HISTORY_YEARS = int(os.getenv("HISTORY_YEARS", "3"))
FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
FLASK_PORT = int(os.getenv("FLASK_PORT", "5000"))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "false").lower() in {"1", "true", "yes"}

# File Paths
RAW_DATA_PATH = str(BASE_DIR / "data" / "raw_market_data.csv")
CLEAN_DATA_PATH = str(BASE_DIR / "data" / "clean_market_data.csv")
FORECAST_DATA_PATH = str(BASE_DIR / "data" / "forecast.csv")
MODEL_PATH = str(BASE_DIR / "model" / "model.pkl")
METRICS_PATH = str(BASE_DIR / "reports" / "metrics.txt")
HISTORICAL_PLOT_PATH = str(BASE_DIR / "reports" / "historical_price.png")
BACKTEST_PLOT_PATH = str(BASE_DIR / "reports" / "backtest.png")
