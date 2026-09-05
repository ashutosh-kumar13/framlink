from fetch_data import fetch_mandi_data
from clean_data import clean_mandi_data
from train import train_final_model
from predict import generate_forecast
import os

def test():
    state, district, market, commodity = "Uttar Pradesh", "Lucknow", "Lucknow", "Wheat"
    print(f"Testing pipeline for {commodity} in {market}...")

    # 1. Fetch
    success, msg = fetch_mandi_data(state, district, market, commodity, target_records=50)
    print(f"Fetch: {success}, {msg}")

    if not success:
        print("Fetch failed, stopping.")
        return

    # 2. Clean
    success, msg, _ = clean_mandi_data(state, district, market, commodity)
    print(f"Clean: {success}, {msg}")

    if not success:
        print("Clean failed, stopping.")
        return

    # 3. Train
    success, msg = train_final_model()
    print(f"Train: {success}, {msg}")

    if not success:
        print("Train failed, stopping.")
        return

    # 4. Predict
    results, msg = generate_forecast(state=state, district=district, mandi=market, commodity=commodity)
    if results:
        print(f"Predict success: Latest price {results['latest_actual_price']}")
        print(f"First forecast point: {results['forecast'][0]}")
    else:
        print(f"Predict failed: {msg}")

if __name__ == "__main__":
    test()
