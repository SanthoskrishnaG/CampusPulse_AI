import numpy as np
import joblib
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
from ml.registry.registry import ModelRegistry

EVENT_TYPE_MAP = {
    'DEPARTMENT_EVENT': 0, 'COLLEGE_EVENT': 1, 'CLUB_EVENT': 2,
    'WORKSHOP': 3, 'SEMINAR': 4, 'HACKATHON': 5, 'COMPETITION': 6,
    'CULTURAL': 7, 'TECHNICAL': 8, 'SPORTS': 9, 'PLACEMENT': 10
}

def generate_event_attendance_data(n_samples=800):
    np.random.seed(42)
    capacities = np.random.choice([50, 80, 100, 150, 200, 300, 500], size=n_samples)
    event_types = np.random.randint(0, 11, size=n_samples)
    is_weekend = np.random.choice([0, 1], p=[0.75, 0.25], size=n_samples)
    hour = np.random.choice([9, 10, 11, 14, 15, 16, 17], size=n_samples)
    has_speaker = np.random.choice([0, 1], p=[0.4, 0.6], size=n_samples)
    registrations = np.clip((capacities * np.random.uniform(0.7, 1.4, n_samples)).astype(int), 10, 600)

    # Actual attendance is typically 70-90% of registrations, influenced by speaker, weekend, workshop type
    conversion_rate = 0.78 + (has_speaker * 0.08) - (is_weekend * 0.05) + np.random.normal(0, 0.06, n_samples)
    conversion_rate = np.clip(conversion_rate, 0.45, 0.98)
    attendance = np.clip((registrations * conversion_rate).astype(int), 5, capacities)

    X = np.column_stack([capacities, event_types, is_weekend, hour, has_speaker, registrations])
    y = attendance
    return X, y

def train_event_attendance_model():
    X, y = generate_event_attendance_data()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor(n_estimators=100, max_depth=7, random_state=42)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    r2 = r2_score(y_test, preds)

    metrics = {
        'mae': round(float(mae), 2),
        'r2_score': round(float(r2), 4),
        'rmse': round(float(np.sqrt(np.mean((y_test - preds)**2))), 2)
    }

    models_dir = Path("models")
    models_dir.mkdir(parents=True, exist_ok=True)
    model_path = models_dir / "event_attendance_regressor.joblib"
    joblib.dump({
        'model': model,
        'metrics': metrics,
        'features': ['capacity', 'event_type', 'is_weekend', 'hour', 'has_speaker', 'registrations']
    }, model_path)

    ModelRegistry.register_model(
        model_name="Event_Attendance_Forecaster",
        version="1.0.0",
        algorithm="RandomForestRegressor",
        metrics=metrics,
        feature_list=['capacity', 'event_type', 'is_weekend', 'hour', 'has_speaker', 'registrations'],
        model_path=model_path,
        description="Forecasts actual student event turnout and expected no-show rates."
    )
    print(f"Trained Event Attendance Model (R2: {r2:.4f}, MAE: {mae:.2f})")
    return model, metrics

if __name__ == '__main__':
    train_event_attendance_model()
