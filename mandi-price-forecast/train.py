import pandas as pd
import numpy as np
import joblib
import os
import json
from features import create_features
from config import CLEAN_DATA_PATH, MODEL_PATH

def train_final_model():
    """
    Trains a stable Linear + Seasonal model using Numpy.
    Avoids XGBoost/Sklearn to prevent system hangs.
    """
    if not os.path.exists(CLEAN_DATA_PATH):
        return False, "Clean data not found."

    df = pd.read_csv(CLEAN_DATA_PATH)
    if len(df) < 5:
        return False, f"Insufficient data: {len(df)} records. Need at least 5."

    df['arrival_date'] = pd.to_datetime(df['arrival_date'])

    # 1. Feature Engineering (Custom for this model)
    # We use 'day_of_year' and 'day_of_week' for seasonality
    # And 'days_from_start' for the trend
    start_date = df['arrival_date'].min()
    df['days_from_start'] = (df['arrival_date'] - start_date).dt.days

    # 2. Train Linear Trend
    # y = mx + c
    X_trend = df['days_from_start'].values
    y = df['modal_price'].values
    slope, intercept = np.polyfit(X_trend, y, 1)

    # 3. Calculate Seasonality (Average deviation by Day of Week)
    df['detrended'] = y - (slope * X_trend + intercept)
    seasonality_dow = df.groupby(df['arrival_date'].dt.dayofweek)['detrended'].mean().to_dict()

    # 4. Save Model
    # A simple dict is our "model" now
    model_data = {
        "slope": float(slope),
        "intercept": float(intercept),
        "seasonality_dow": {int(k): float(v) for k, v in seasonality_dow.items()},
        "start_date": start_date.strftime('%Y-%m-%d'),
        "last_price": float(y[-1]),
        "last_date": df['arrival_date'].max().strftime('%Y-%m-%d')
    }

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(model_data, MODEL_PATH)

    # Metadata for UI
    feature_meta_path = MODEL_PATH.replace(".pkl", "_features.json")
    meta = {
        "features": ["trend", "day_of_week"],
        "best_model": "Linear+Seasonal (Stable)",
        "mae_xgb": 0.0, # Placeholder
        "data_rows": len(df)
    }
    with open(feature_meta_path, "w") as f:
        json.dump(meta, f)

    return True, f"Model trained (Stable Linear) using {len(df)} records."

if __name__ == "__main__":
    success, msg = train_final_model()
    print(msg)
