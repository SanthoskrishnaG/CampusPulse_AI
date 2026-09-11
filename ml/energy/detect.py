import joblib
import numpy as np
from pathlib import Path

MODEL_PATH = Path("models") / "energy_isolation_forest.joblib"

class EnergyAnomalyDetector:
    _cached_model = None

    @classmethod
    def get_model(cls):
        if cls._cached_model is None and MODEL_PATH.exists():
            cls._cached_model = joblib.load(MODEL_PATH)
        return cls._cached_model

    @classmethod
    def inspect_reading(cls, hour, is_weekend, occupancy, kwh, baseline=45.0):
        """
        Inspects an energy reading. Returns: is_anomaly, anomaly_score, expected_kwh, severity, explanation
        """
        model_data = cls.get_model()
        is_night = (hour < 6 or hour > 20)
        expected_kwh = (baseline * 0.25) if is_night else baseline

        if model_data:
            model = model_data['model']
            vector = [[hour, int(is_weekend), occupancy, kwh]]
            pred = model.predict(vector)[0] # -1 = anomaly, 1 = normal
            raw_score = float(model.decision_function(vector)[0])
            is_anomaly = (pred == -1) or (is_night and kwh > expected_kwh * 2.2)
        else:
            is_anomaly = (is_night and kwh > expected_kwh * 2.0) or (kwh > baseline * 2.4)
            raw_score = -0.15 if is_anomaly else 0.25

        if is_anomaly:
            excess = kwh - expected_kwh
            if excess > 40.0:
                severity = 'CRITICAL'
            elif excess > 20.0:
                severity = 'MODERATE'
            else:
                severity = 'MILD'

            if is_night:
                atype = 'NIGHT_LEAK'
                explanation = f"Unexpected high load ({kwh:.1f} kWh) during off-hours (expected ~{expected_kwh:.1f} kWh). Likely HVAC or lab computers left operational overnight."
            else:
                atype = 'POWER_SURGE'
                explanation = f"Current consumption ({kwh:.1f} kWh) exceeds daytime baseline ({baseline:.1f} kWh) by {excess:.1f} kWh."

            return {
                'is_anomaly': True,
                'anomaly_score': round(raw_score, 3),
                'kwh_observed': round(kwh, 1),
                'kwh_expected': round(expected_kwh, 1),
                'severity': severity,
                'anomaly_type': atype,
                'explanation': explanation
            }

        return {'is_anomaly': False, 'kwh_observed': round(kwh, 1), 'kwh_expected': round(expected_kwh, 1)}
