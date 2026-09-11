import numpy as np
import joblib
from pathlib import Path
from sklearn.ensemble import IsolationForest
from ml.registry.registry import ModelRegistry

def generate_energy_telemetry_data(n_samples=1000):
    np.random.seed(42)
    # Features: [hour (0-23), is_weekend (0/1), occupancy (0-300), kwh_consumed]
    hours = np.random.randint(0, 24, size=n_samples)
    is_weekend = np.random.choice([0, 1], p=[0.75, 0.25], size=n_samples)
    
    occupancy = []
    kwh = []
    for h, w in zip(hours, is_weekend):
        if w == 1:
            occ = np.random.randint(5, 30)
            power = 12.0 + occ * 0.05 + np.random.normal(0, 2.0)
        elif 8 <= h <= 17:
            occ = np.random.randint(100, 350)
            power = 45.0 + occ * 0.15 + np.random.normal(0, 5.0)
        else:
            occ = np.random.randint(0, 15)
            power = 15.0 + occ * 0.08 + np.random.normal(0, 2.5)
        occupancy.append(occ)
        kwh.append(max(5.0, power))

    # Inject 5% anomalies (e.g. night ACs running full blast = 70 kWh at 2 AM)
    for idx in np.random.choice(n_samples, size=int(n_samples * 0.05), replace=False):
        if hours[idx] < 6 or hours[idx] > 20:
            kwh[idx] = np.random.uniform(65.0, 95.0) # Night leak anomaly
        else:
            kwh[idx] = np.random.uniform(110.0, 150.0) # Midday surge overload

    X = np.column_stack([hours, is_weekend, occupancy, kwh])
    return X

def train_energy_anomaly_model():
    X = generate_energy_telemetry_data()
    model = IsolationForest(contamination=0.06, random_state=42)
    model.fit(X)

    models_dir = Path("models")
    models_dir.mkdir(parents=True, exist_ok=True)
    model_path = models_dir / "energy_isolation_forest.joblib"
    joblib.dump({
        'model': model,
        'features': ['hour', 'is_weekend', 'occupancy', 'kwh_consumed']
    }, model_path)

    metrics = {
        'contamination': 0.06,
        'samples_trained': len(X),
        'algorithm': 'IsolationForest'
    }

    ModelRegistry.register_model(
        model_name="Energy_Anomaly_Detector",
        version="1.0.0",
        algorithm="IsolationForest",
        metrics=metrics,
        feature_list=['hour', 'is_weekend', 'occupancy', 'kwh_consumed'],
        model_path=model_path,
        description="Unsupervised anomaly detection identifying nocturnal energy leaks and midday load spikes."
    )
    print("Trained Energy Isolation Forest Anomaly Detector")
    return model

if __name__ == '__main__':
    train_energy_anomaly_model()
