import pandas as pd
import numpy as np
import os
from importlib import import_module
from features import create_features
from config import CLEAN_DATA_PATH


def mean_absolute_error(actual, predicted):
    return float(np.mean(np.abs(np.asarray(actual) - np.asarray(predicted))))

def walk_forward_backtest(df, horizon=30, min_train_size=15, step=10):
    """
    Simulates real-world deployment.
    Reduced min_train_size to 15 for the prototype to handle sparse mandi data.
    """
    if horizon < 1 or min_train_size < 2 or step < 1:
        raise ValueError("horizon, min_train_size, and step must be positive")

    try:
        XGBRegressor = import_module("xgboost").XGBRegressor
    except ImportError as error:
        raise RuntimeError(
            "Backtesting requires the optional xgboost package; install it from requirements-backtest.txt."
        ) from error

    df_feat = create_features(df)

    # If the feature creation removed too many rows (due to lags),
    # and we don't have enough left to even test one window, return fallback.
    if len(df_feat) < min_train_size + 5: # Need at least some test rows
        print(f"Dataset too small for backtesting (Count: {len(df_feat)}).")
        return None, None

    features = [col for col in df_feat.columns if col.startswith(('lag_', 'rolling_', 'price_', 'month', 'day_'))]
    target = 'modal_price'

    errors_xgb = []
    errors_base = []

    # Adjust horizon if dataset is small
    actual_horizon = min(horizon, len(df_feat) - min_train_size - 1)
    if actual_horizon < 1:
        return None, None

    # Walk forward
    for i in range(min_train_size, len(df_feat) - actual_horizon, step):
        train = df_feat.iloc[:i]
        test = df_feat.iloc[i:i+actual_horizon]

        X_train, y_train = train[features], train[target]
        X_test, y_test = test[features], test[target]

        # XGBoost
        model = XGBRegressor(n_estimators=50, learning_rate=0.1, max_depth=3, random_state=42)
        model.fit(X_train, y_train)
        y_pred_xgb = model.predict(X_test)

        # Baseline
        last_price = y_train.iloc[-1]
        y_pred_base = np.full(len(y_test), last_price)

        errors_xgb.append(mean_absolute_error(y_test, y_pred_xgb))
        errors_base.append(mean_absolute_error(y_test, y_pred_base))

    if not errors_xgb:
        return None, None

    avg_mae_xgb = np.mean(errors_xgb)
    avg_mae_base = np.mean(errors_base)

    print(f"Backtest: XGB MAE {avg_mae_xgb:.2f}, Base MAE {avg_mae_base:.2f}")

    return avg_mae_xgb, avg_mae_base

if __name__ == "__main__":
    if os.path.exists(CLEAN_DATA_PATH):
        df = pd.read_csv(CLEAN_DATA_PATH)
        walk_forward_backtest(df)
