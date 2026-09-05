import pandas as pd
import os
from clean_data import clean_mandi_data

def debug():
    path = "mandi-price-forecast/data/raw_market_data.csv"
    if not os.path.exists(path):
        print("Raw data missing")
        return

    df = pd.read_csv(path)
    print("Raw Data Columns:", df.columns.tolist())
    print("Raw Data Head:\n", df.head())
    print("Unique States:", df['state'].unique() if 'state' in df.columns else "N/A")
    print("Unique Commodities:", df['commodity'].unique() if 'commodity' in df.columns else "N/A")

    state, district, market, commodity = "Uttar Pradesh", "Lucknow", "Lucknow", "Wheat"
    print(f"\nAttempting clean for {commodity} in {state}...")
    success, msg, var = clean_mandi_data(state, district, market, commodity)
    print(f"Result: {success}, {msg}")

if __name__ == "__main__":
    debug()
