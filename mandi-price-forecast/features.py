import pandas as pd
import numpy as np

def create_features(df, target_col='modal_price'):
    """
    Creates time-series features. Adaptive to dataset size.
    """
    df = df.copy()
    df['arrival_date'] = pd.to_datetime(df['arrival_date'])
    df = df.sort_values('arrival_date')

    n_rows = len(df)

    # 1. Lag Features
    # We only add lags that make sense for the current data size
    lags = [1, 3, 7, 14, 30]
    for lag in lags:
        if n_rows > lag:
            df[f'lag_{lag}'] = df[target_col].shift(lag)

    # 2. Rolling Features
    windows = [7, 14, 30]
    for window in windows:
        if n_rows > window:
            df[f'rolling_mean_{window}'] = df[target_col].shift(1).rolling(window=window).mean()

    # 3. Price Changes
    if n_rows > 8:
        df['price_change_7'] = df[target_col].shift(1) - df[target_col].shift(8)
    if n_rows > 31:
        df['price_change_30'] = df[target_col].shift(1) - df[target_col].shift(31)

    # 4. Calendar Features (Always available)
    df['month'] = df['arrival_date'].dt.month
    df['day_of_year'] = df['arrival_date'].dt.dayofyear
    df['day_of_week'] = df['arrival_date'].dt.dayofweek

    # 5. Drop rows with NaN values
    # For very small datasets, we'll have at least lag_1 if n_rows > 1
    df = df.dropna().reset_index(drop=True)

    return df
