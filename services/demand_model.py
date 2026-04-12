import pandas as pd
import numpy as np
from xgboost import XGBRegressor
from datetime import datetime, timedelta

def prepare_features(df: pd.DataFrame) -> pd.DataFrame:
    """Extract time features from timestamp column."""
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["hour"]      = df["timestamp"].dt.hour
    df["dayofweek"] = df["timestamp"].dt.dayofweek   # 0=Mon, 6=Sun
    df["month"]     = df["timestamp"].dt.month
    df["is_weekend"]= (df["dayofweek"] >= 5).astype(int)
    return df

def train(df: pd.DataFrame) -> XGBRegressor:
    """Train demand prediction model on historical ridership."""
    df = prepare_features(df)
    feature_cols = ["route_id", "hour", "dayofweek", "month", "is_weekend"]
    X = df[feature_cols]
    y = df["passengers"]

    model = XGBRegressor(
        n_estimators=100,
        max_depth=4,
        learning_rate=0.1,
        random_state=42
    )
    model.fit(X, y)
    return model

def predict(model: XGBRegressor, route_id: int, horizon_hours: int) -> list:
    """Generate demand forecast for next N hours."""
    now = datetime.utcnow()
    future_times = [now + timedelta(hours=i) for i in range(horizon_hours)]

    df = pd.DataFrame({
        "route_id":   [route_id] * horizon_hours,
        "hour":       [t.hour for t in future_times],
        "dayofweek":  [t.weekday() for t in future_times],
        "month":      [t.month for t in future_times],
        "is_weekend": [int(t.weekday() >= 5) for t in future_times],
    })

    predictions = model.predict(df)

    return [
        {
            "hour_offset": i,
            "time": future_times[i].strftime("%H:%M"),
            "predicted_passengers": max(0, round(float(p)))
        }
        for i, p in enumerate(predictions)
    ]