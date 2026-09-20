"""
Smart Transport ETA & Delay Prediction Pipeline for CIT Campus Shuttle Fleet (Section 19).
"""

import numpy as np
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score
from ml.registry.registry import ModelRegistry

def generate_transport_telemetry_dataset(n_samples=1200, random_state=42):
    """
    Simulates CIT bus route telemetry:
    Features:
      - distance_km (3.0 to 25.0 km)
      - stop_sequence (1 to 12)
      - is_peak_hour (0/1: 8-10 AM or 4-6 PM)
      - hour (6 to 21)
      - passenger_count (5 to 60)
      - occupancy_pct (10 to 100%)
    Target:
      - travel_time_mins (Elapsed transit time to campus terminal)
      - delay_mins (Deviation from timetable)
    """
    np.random.seed(random_state)
    distance_km = np.random.uniform(3.5, 22.0, size=n_samples)
    stop_sequence = np.random.randint(1, 10, size=n_samples)
    hour = np.random.randint(6, 21, size=n_samples)
    is_peak = np.where(((hour >= 8) & (hour <= 10)) | ((hour >= 16) & (hour <= 18)), 1, 0)

    capacity = 52
    passenger_count = np.random.randint(10, 56, size=n_samples)
    occupancy_pct = np.clip((passenger_count / capacity) * 100.0, 15.0, 105.0)

    # Base travel speed in Coimbatore city corridor: ~22-26 km/h non-peak, ~14-18 km/h peak
    base_speed = np.where(is_peak == 1, 16.5, 24.0)
    stop_delay = stop_sequence * 1.8  # boarding/alighting time per stop

    # Travel time formula + noise
    travel_time = (distance_km / base_speed) * 60.0 + stop_delay + (occupancy_pct > 85.0) * 4.0
    travel_time += np.random.normal(0, 2.5, size=n_samples)
    travel_time = np.clip(travel_time, 8.0, 95.0)

    scheduled_time = (distance_km / 22.0) * 60.0 + stop_sequence * 1.5
    delay = np.maximum(0, travel_time - scheduled_time)

    X = np.column_stack([distance_km, stop_sequence, is_peak, hour, passenger_count, occupancy_pct])
    y_travel = np.round(travel_time, 1)
    y_delay = np.round(delay, 1)

    return X, y_travel, y_delay

def train_transport_models():
    """
    Trains and serializes Random Forest Regressor for ETA travel time and route delay.
    """
    X, y_travel, y_delay = generate_transport_telemetry_dataset()
    X_train, X_test, y_train, y_test = train_test_split(X, y_travel, test_size=0.25, random_state=42)

    model = RandomForestRegressor(n_estimators=120, max_depth=8, min_samples_leaf=3, random_state=42)
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
    model_path = models_dir / "transport_eta_model.joblib"
    joblib.dump({
        'model': model,
        'metrics': metrics,
        'features': ['distance_km', 'stop_sequence', 'is_peak_hour', 'hour', 'passenger_count', 'occupancy_pct'],
        'version': '1.0.0'
    }, model_path)

    ModelRegistry.register_model(
        model_name="Smart_Transport_ETA_Predictor",
        version="1.0.0",
        task="REGRESSION",
        algorithm="RandomForestRegressor",
        metrics=metrics,
        feature_list=['distance_km', 'stop_sequence', 'is_peak_hour', 'hour', 'passenger_count', 'occupancy_pct'],
        model_path=model_path,
        description="Forecasts actual transit arrival duration and peak traffic delays along CIT bus routes."
    )
    print(f"Transport ETA Model Trained: R2={r2:.4f}, MAE={mae:.2f} mins, RMSE={rmse:.2f} mins")
    return model, metrics

if __name__ == '__main__':
    train_transport_models()
