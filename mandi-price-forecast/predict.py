import pandas as pd
import joblib
import os
import json
from datetime import timedelta
from config import CLEAN_DATA_PATH, MODEL_PATH, FORECAST_DATA_PATH
from weather_api import get_coordinates, get_weather_forecast, analyze_weather_impact

def generate_forecast(days=30, state=None, district=None, mandi=None, commodity=None):
    """
    Generates a 30-day forecast and integrates real-time weather data.
    """
    if not isinstance(days, int) or not 1 <= days <= 90:
        return None, "days must be an integer between 1 and 90."
    if not os.path.exists(MODEL_PATH) or not os.path.exists(CLEAN_DATA_PATH):
        return None, "Model or data missing."

    model_data = joblib.load(MODEL_PATH)

    df = pd.read_csv(CLEAN_DATA_PATH)
    if df.empty or not {'arrival_date', 'modal_price'}.issubset(df.columns):
        return None, "Clean data is empty or invalid."
    df['arrival_date'] = pd.to_datetime(df['arrival_date'])

    last_date = df['arrival_date'].max()
    start_date = pd.to_datetime(model_data["start_date"])

    # --- Weather Integration ---
    weather_desc = "Fetching weather..."
    weather_impacts = [1.0] * days
    weather_raw = {}

    if state and district and mandi:
        print(f"DEBUG: Fetching weather for {mandi}, {district}, {state}")
        lat, lon = get_coordinates(mandi, district, state)
        if lat and lon:
            print(f"DEBUG: Coords found: {lat}, {lon}")
            weather_raw = get_weather_forecast(lat, lon)
            impacts, desc = analyze_weather_impact(weather_raw, commodity)
            weather_desc = desc
            # Apply impacts to the first 7 days (forecast period of weather API)
            for i in range(min(len(impacts), days)):
                weather_impacts[i] = impacts[i]
        else:
            print(f"DEBUG: Geocoding failed for {mandi}, {district}, {state}")
            weather_desc = "Location not found for weather data."
    else:
        weather_desc = "Weather data not requested."
    # ---------------------------

    forecast_results = []

    for i in range(1, days + 1):
        next_date = last_date + timedelta(days=i)

        # 1. Trend component
        days_from_start = (next_date - start_date).days
        price_trend = (model_data["slope"] * days_from_start) + model_data["intercept"]

        # 2. Seasonality component
        dow = next_date.dayofweek
        price_seasonal = model_data["seasonality_dow"].get(dow, 0)

        # 3. Combine & Apply Weather Impact
        base_predicted = max(0, price_trend + price_seasonal)
        final_predicted = base_predicted * weather_impacts[i-1]

        forecast_results.append({
            'date': next_date.strftime('%Y-%m-%d'),
            'predicted_price': round(float(final_predicted), 2),
            'weather_factor': round(weather_impacts[i-1], 2)
        })

    forecast_df = pd.DataFrame(forecast_results)
    os.makedirs(os.path.dirname(FORECAST_DATA_PATH), exist_ok=True)
    forecast_df.to_csv(FORECAST_DATA_PATH, index=False)

    # Trend calculation
    latest_actual = float(df['modal_price'].iloc[-1])
    avg_forecast = forecast_df['predicted_price'].mean()
    diff = avg_forecast - latest_actual

    if diff > (latest_actual * 0.02): trend = "Upward"
    elif diff < -(latest_actual * 0.02): trend = "Downward"
    else: trend = "Stable"

    # Meta for UI
    meta_path = MODEL_PATH.replace(".pkl", "_features.json")
    with open(meta_path, "r") as f:
        meta = json.load(f)

    return {
        "forecast": forecast_results,
        "trend": trend,
        "latest_actual_price": latest_actual,
        "meta": meta,
        "weather": {
            "description": weather_desc,
            "data": weather_raw
        },
        "history": [
            {"date": date.strftime('%Y-%m-%d'), "price": float(price)}
            for date, price in zip(df['arrival_date'], df['modal_price'])
        ]
    }, "Success"

if __name__ == "__main__":
    res, msg = generate_forecast()
    if res:
        print(f"Forecast success: {len(res['forecast'])} days")
    else:
        print(f"Error: {msg}")
