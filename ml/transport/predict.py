import joblib
from pathlib import Path
from django.utils import timezone
from ml.utils.validation import validate_transport_features

MODEL_PATH = Path("models") / "transport_eta_model.joblib"

class TransportETAPredictor:
    _cached_model = None

    @classmethod
    def get_model(cls):
        if cls._cached_model is None and MODEL_PATH.exists():
            cls._cached_model = joblib.load(MODEL_PATH)
        return cls._cached_model

    @classmethod
    def predict_eta(cls, distance_km: float, stop_sequence: int, passenger_count: int, capacity: int = 52):
        """
        Runs real-time ML inference predicting transit travel time (minutes) and schedule status.
        """
        now = timezone.now()
        hour = now.hour
        is_peak = 1 if ((8 <= hour <= 10) or (16 <= hour <= 18)) else 0

        validated = validate_transport_features({
            'distance_km': distance_km,
            'stop_sequence': stop_sequence,
            'is_peak_hour': is_peak,
            'passenger_count': passenger_count
        })

        occupancy_pct = min(100.0, (validated['passenger_count'] / max(capacity, 1)) * 100.0)

        model_data = cls.get_model()
        if not model_data:
            return {
                'success': False,
                'eta_mins': None,
                'message': "Prediction unavailable — transport ETA model requires training.",
                'model': "Smart_Transport_ETA_Predictor",
                'version': "1.0.0"
            }

        vector = [[
            validated['distance_km'],
            validated['stop_sequence'],
            validated['is_peak_hour'],
            hour,
            validated['passenger_count'],
            occupancy_pct
        ]]

        model = model_data['model']
        pred_eta = float(round(float(model.predict(vector)[0]), 1))
        pred_eta = max(2.0, pred_eta)

        scheduled_time = (distance_km / 22.0) * 60.0 + stop_sequence * 1.5
        delay = max(0.0, round(pred_eta - scheduled_time, 1))
        status = 'DELAYED' if delay >= 5.0 else 'ON_TIME'

        return {
            'success': True,
            'eta_mins': int(round(pred_eta)),
            'predicted_delay_mins': int(round(delay)),
            'status': status,
            'is_peak_hour': bool(is_peak),
            'occupancy_pct': round(occupancy_pct, 1),
            'model': "Smart_Transport_ETA_Predictor",
            'version': model_data.get('version', '1.0.0')
        }
