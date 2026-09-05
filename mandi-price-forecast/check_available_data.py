import pandas as pd
import os

def check():
    path = "mandi-price-forecast/data/raw_market_data.csv"
    if not os.path.exists(path):
        print("No raw data file.")
        return

    df = pd.read_csv(path)
    df.columns = [c.lower().replace(" ", "_") for c in df.columns]

    print("Available Data Summary:")
    summary = df.groupby(['state', 'commodity']).size().reset_index(name='count')
    print(summary)

if __name__ == "__main__":
    check()
