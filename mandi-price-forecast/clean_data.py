import pandas as pd
import os
from config import RAW_DATA_PATH, CLEAN_DATA_PATH

def clean_mandi_data(state, district, market, commodity):
    """
    Cleans raw data and merges varieties to create a continuous history.
    """
    if not os.path.exists(RAW_DATA_PATH):
        return False, "Raw data file not found.", None

    df = pd.read_csv(RAW_DATA_PATH)
    df.columns = [c.lower() for c in df.columns]
    required_columns = {"arrival_date", "state", "commodity", "modal_price"}
    if not required_columns.issubset(df.columns):
        missing = ", ".join(sorted(required_columns - set(df.columns)))
        return False, f"Raw data is missing columns: {missing}", None

    # 1. Date Formatting
    df['arrival_date'] = pd.to_datetime(df['arrival_date'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['arrival_date'])

    # Auto-Shift Logic: Only shift if we have NO recent data (pre-2015)
    max_year = df['arrival_date'].dt.year.max()
    if max_year < 2015:
        print(f"Old data detected (Max year: {max_year}). Shifting +20 years for simulation...")
        df['arrival_date'] = df['arrival_date'] + pd.DateOffset(years=20)
    else:
        print(f"Recent data found (Max year: {max_year}). Skipping date shift.")

    # 2. Strict Filter (State/Commodity)
    # Market filter is flexible to handle variant merges (e.g. Lucknow and Lucknow APMC)
    df = df[
        (df['state'].fillna('').str.lower() == state.lower()) &
        (df['commodity'].fillna('').str.lower() == commodity.lower())
    ]

    if len(df) == 0:
        return False, "No data matching State/Commodity filters.", None

    # 3. Variety Merging Logic
    # We want to capture the full 2023-2026 timeline.
    # We take all records and aggregate by date to handle variety shifts over years.
    df['modal_price'] = pd.to_numeric(df['modal_price'], errors='coerce')
    df = df.dropna(subset=['modal_price'])
    df = df[df['modal_price'] > 0]

    # Group by date to get a single price point per day (merging varieties if they overlap)
    aggregations = {
        'state': 'first',
        'district': 'first',
        'market': 'first', # Usually picking the first variant found
        'commodity': 'first',
        'modal_price': 'mean'
    }
    if 'variety' in df.columns:
        aggregations['variety'] = lambda values: '/'.join(values.dropna().astype(str).unique()[:2])
    df_clean = df.groupby('arrival_date').agg(aggregations).reset_index()

    df_clean = df_clean.sort_values(by='arrival_date').reset_index(drop=True)

    if len(df_clean) > 0:
        start_date = df_clean['arrival_date'].min().strftime('%Y-%m-%d')
        end_date = df_clean['arrival_date'].max().strftime('%Y-%m-%d')
        msg = f"SUCCESS: History spans from {start_date} to {end_date} ({len(df_clean)} records)."
        print(msg)

        os.makedirs(os.path.dirname(CLEAN_DATA_PATH), exist_ok=True)
        df_clean.to_csv(CLEAN_DATA_PATH, index=False)
        return True, msg, "Merged"

    return False, "Cleaning resulted in zero records.", None

if __name__ == "__main__":
    from config import STATE, DISTRICT, MANDI, COMMODITY
    success, msg, var = clean_mandi_data(STATE, DISTRICT, MANDI, COMMODITY)
    print(msg)
