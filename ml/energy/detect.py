import time
import json
import joblib
import numpy as np
from pathlib import Path
from django.conf import settings
from ml.utils.validation import validate_energy_features

MODEL_PATH = Path("models") / "energy_isolation_forest.joblib"

class EnergyAnomalyDetector:
    _cached_model = None

    @classmethod
    def get_model(cls):
        if cls._cached_model is None and MODEL_PATH.exists():
            cls._cached_model = joblib.load(MODEL_PATH)
        return cls._cached_model

    @classmethod
    def inspect_reading(cls, hour: int, is_weekend: bool, occupancy: int, kwh: float, baseline: float = 45.0, user=None):
        """
        Inspects real-time energy telemetry using Isolation Forest model.
        Returns: is_anomaly, anomaly_score, expected_kwh, severity, explanation.
        Persists anomaly telemetry to MLPredictionLog.
        """
        start_time = time.time()
        validated = validate_energy_features({
            'hour': hour,
            'is_weekend': is_weekend,
            'occupancy': occupancy,
            'kwh_consumed': kwh
        })

        model_data = cls.get_model()
        is_night = (validated['hour'] < 6 or validated['hour'] > 20)
        expected_kwh = (baseline * 0.25) if is_night else baseline

        if not model_data:
            return {
                'success': False,
                'is_anomaly': False,
                'anomaly_score': 0.0,
                'kwh_observed': round(validated['kwh_consumed'], 1),
                'kwh_expected': round(expected_kwh, 1),
                'message': "Prediction unavailable — energy anomaly model requires training.",
                'model': "Energy_Anomaly_Detector",
                'version': "1.0.0"
            }

        model = model_data['model']
        vector = [[validated['hour'], validated['is_weekend'], validated['occupancy'], validated['kwh_consumed']]]
        pred = model.predict(vector)[0]  # -1 = Anomaly, 1 = Normal
        raw_score = float(model.decision_function(vector)[0])
        is_anomaly = bool(pred == -1 or (is_night and validated['kwh_consumed'] > expected_kwh * 2.2))

        excess = max(0.0, validated['kwh_consumed'] - expected_kwh)
        if excess > 40.0:
            severity = 'CRITICAL'
        elif excess > 20.0:
            severity = 'MODERATE'
        else:
            severity = 'MILD'

        if is_night:
            atype = 'NIGHT_LEAK'
            explanation = f"Off-hours load anomaly ({validated['kwh_consumed']:.1f} kWh vs baseline ~{expected_kwh:.1f} kWh). Unattended HVAC or laboratory machinery detected."
        else:
            atype = 'POWER_SURGE'
            explanation = f"Daytime load surge ({validated['kwh_consumed']:.1f} kWh) exceeds expected threshold by {excess:.1f} kWh."

        latency_ms = round((time.time() - start_time) * 1000.0, 2)
        data_mode = getattr(settings, 'DATA_MODE', 'DEMO')

        # Persist to MLPredictionLog
        try:
            from apps.analytics.models import MLPredictionLog
            MLPredictionLog.objects.create(
                model_name="Energy_Anomaly_Detector",
                model_version=model_data.get('version', '1.0.0'),
                task="ANOMALY_DETECTION",
                input_summary=json.dumps({
                    'hour': validated['hour'],
                    'occupancy': validated['occupancy'],
                    'kwh': validated['kwh_consumed']
                }),
                prediction="ANOMALY" if is_anomaly else "NORMAL",
                confidence=round(abs(raw_score), 3),
                factors_json=json.dumps([f"Severity: {severity}", f"Excess: {excess:.1f} kWh", explanation]),
                latency_ms=latency_ms,
                status=MLPredictionLog.Status.SUCCESS,
                data_mode=data_mode,
                user=user
            )
        except Exception:
            pass

        return {
            'success': True,
            'is_anomaly': is_anomaly,
            'anomaly_score': round(raw_score, 3),
            'kwh_observed': round(validated['kwh_consumed'], 1),
            'kwh_expected': round(expected_kwh, 1),
            'severity': severity if is_anomaly else 'NORMAL',
            'anomaly_type': atype if is_anomaly else 'NONE',
            'explanation': explanation if is_anomaly else 'Consumption operates within learned seasonal baselines.',
            'latency_ms': latency_ms,
            'model': "Energy_Anomaly_Detector",
            'version': model_data.get('version', '1.0.0')
        }
