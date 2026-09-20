"""
Smart Parking Occupancy Forecasting Pipeline for CIT Campus (Section 21).
"""

import numpy as np
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score
from ml.registry.registry import ModelRegistry

def generate_parking_telemetry_dataset(n_samples=1000, random_state=42):
    """
    Simulates institutional parking bay turnover:
    Features:
      - total_slots (40 to 120)
      - hour (6 to 22)
      - day_of_week (0 to 6)
      - is_event (0/1)
      - is_weekend (0/1)
    Target:
      - occupied_slots (Integer count of occupied slots)
    """
    np.random.seed(random_state)
    total_slots = np.random.choice([50, 60, 80, 100, 120], size=n_samples)
    hour = np.random.randint(6, 23, size=n_samples)
    day_of_week = np.random.randint(0, 7, size=n_samples)
    is_weekend = np.where(day_of_week >= 5, 1, 0)
    is_event = np.random.choice([0, 1], p=[0.88, 0.12], size=n_samples)

    # Base occupancy curve throughout college day:
    # 6-8 AM: low (10-25%)
    # 9 AM - 1 PM: peak academic hours (75-95%)
    # 2 PM - 4 PM: steady afternoon (65-85%)
    # 5 PM - 7 PM: evening departure (40-60%)
    # 8 PM+: night drop (<20%)
    hour_factor = np.where((hour >= 9) & (hour <= 13), 0.88,
                  np.where((hour >= 14) & (hour <= 16), 0.76,
                  np.where((hour >= 17) & (hour <= 19), 0.50,
                  np.where((hour >= 7) & (hour <= 8), 0.35, 0.15))))

    occ_ratio = hour_factor * np.where(is_weekend == 1, 0.30, 1.0) * (1.0 + is_event * 0.20)
    occ_ratio += np.random.normal(0, 0.05, size=n_samples)
    occ_ratio = np.clip(occ_ratio, 0.05, 0.98)

    occupied = np.round(total_slots * occ_ratio).astype(int)

    X = np.column_stack([total_slots, hour, day_of_week, is_event, is_weekend])
    y = occupied
    return X, y

def train_parking_model():
    """
    Trains and serializes Random Forest Regressor for parking bay occupancy.
    """
    X, y = generate_parking_telemetry_dataset()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

    model = RandomForestRegressor(n_estimators=100, max_depth=7, min_samples_leaf=3, random_state=42)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    rmse = root_mean_squared_error(y_test, preds)
    r2 = r2_score(y_test, preds)

    metrics = {
        'mae': round(float(mae), 2),
        'rmse': round(float(rmse), 2),
        'r2_score': round(float(r2), 4),
        'test_samples': len(y_test)
    }

    models_dir = Path("models")
    models_dir.mkdir(parents=True, exist_ok=True)
    model_path = models_dir / "parking_occupancy_model.joblib"
    joblib.dump({
        'model': model,
        'metrics': metrics,
        'features': ['total_slots', 'hour', 'day_of_week', 'is_event', 'is_weekend'],
        'version': '1.0.0'
    }, model_path)

    ModelRegistry.register_model(
        model_name="Smart_Parking_Occupancy_Forecaster",
        version="1.0.0",
        task="REGRESSION",
        algorithm="RandomForestRegressor",
        metrics=metrics,
        feature_list=['total_slots', 'hour', 'day_of_week', 'is_event', 'is_weekend'],
        model_path=model_path,
        description="Forecasts hourly parking bay vacancy and congestion levels across CIT parking zones."
    )
    print(f"Parking Occupancy Model Trained: R2={r2:.4f}, MAE={mae:.2f} slots, RMSE={rmse:.2f} slots")
    return model, metrics

if __name__ == '__main__':
    train_parking_model()
