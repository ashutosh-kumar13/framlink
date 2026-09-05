import pandas as pd
import matplotlib.pyplot as plt
import os
from config import CLEAN_DATA_PATH, HISTORICAL_PLOT_PATH, MANDI, COMMODITY

def plot_historical_prices():
    """
    Generates a simple chart of historical modal prices.
    """
    if not os.path.exists(CLEAN_DATA_PATH):
        print(f"ERROR: Cleaned data not found at {CLEAN_DATA_PATH}. Run clean_data.py first.")
        return

    # Load data
    df = pd.read_csv(CLEAN_DATA_PATH)
    df['arrival_date'] = pd.to_datetime(df['arrival_date'])

    if len(df) == 0:
        print("Empty dataset. Cannot plot.")
        return

    plt.figure(figsize=(12, 6))
    plt.plot(df['arrival_date'], df['modal_price'], marker='o', linestyle='-', color='green', markersize=2)

    plt.title(f"Historical Mandi Price Trend: {COMMODITY} at {MANDI}")
    plt.xlabel("Date")
    plt.ylabel("Modal Price (₹/Quintal)")
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save plot
    os.makedirs(os.path.dirname(HISTORICAL_PLOT_PATH), exist_ok=True)
    plt.savefig(HISTORICAL_PLOT_PATH)
    print(f"Historical price chart saved to: {HISTORICAL_PLOT_PATH}")

    # Also show the plot if in an interactive environment (optional)
    # plt.show()

if __name__ == "__main__":
    plot_historical_prices()
