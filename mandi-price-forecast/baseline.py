import pandas as pd
import numpy as np
import os
from config import CLEAN_DATA_PATH, METRICS_PATH


def mean_absolute_error(actual, predicted):
    return float(np.mean(np.abs(np.asarray(actual) - np.asarray(predicted))))


def root_mean_squared_error(actual, predicted):
    difference = np.asarray(actual) - np.asarray(predicted)
    return float(np.sqrt(np.mean(difference ** 2)))

def evaluate_baseline():
    """
    Evaluates a simple baseline model: Tomorrow's price = Today's price.
    """
    if not os.path.exists(CLEAN_DATA_PATH):
        print(f"ERROR: Cleaned data not found at {CLEAN_DATA_PATH}. Run clean_data.py first.")
        return

    # Load data
    df = pd.read_csv(CLEAN_DATA_PATH)

    if len(df) < 2:
        print("Not enough data to evaluate a baseline (need at least 2 observations).")
        return

    # For a simple baseline, we shift the price by 1 to represent the "previous" price
    actual = df['modal_price'][1:].values
    predicted = df['modal_price'][:-1].values # Shifted by 1

    mae = mean_absolute_error(actual, predicted)
    rmse = root_mean_squared_error(actual, predicted)

    report = f"""
--- BASELINE MODEL EVALUATION (Persistence) ---
Model: Latest Known Price
Description: Predicts that tomorrow's price will be the same as today's.

Metrics:
MAE (Mean Absolute Error): ₹{mae:.2f}
RMSE (Root Mean Squared Error): ₹{rmse:.2f}

Note: The ML model must outperform these metrics to be considered useful.
"""
    print(report)

    # Save metrics to file
    os.makedirs(os.path.dirname(METRICS_PATH), exist_ok=True)
    with open(METRICS_PATH, "w") as f:
        f.write(report)

    print(f"Baseline metrics saved to: {METRICS_PATH}")
    return mae, rmse

if __name__ == "__main__":
    evaluate_baseline()
