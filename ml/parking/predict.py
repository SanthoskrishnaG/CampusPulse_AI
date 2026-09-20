import joblib
from pathlib import Path
from django.utils import timezone
from ml.utils.validation import validate_parking_features

MODEL_PATH = Path("models") / "parking_occupancy_model.joblib"

class ParkingOccupancyPredictor:
    _cached_model = None

    @classmethod
    def get_model(cls):
        if cls._cached_model is None and MODEL_PATH.exists():
            cls._cached_model = joblib.load(MODEL_PATH)
        return cls._cached_model

    @classmethod
    def predict_occupancy(cls, total_slots: int, hour: int = None, day_of_week: int = None, is_event: bool = False):
        """
        Runs real-time ML inference predicting occupied slots, vacancy count, and congestion status.
        """
        now = timezone.now()
        if hour is None:
            hour = now.hour
        if day_of_week is None:
            day_of_week = now.weekday()

        validated = validate_parking_features({
            'total_slots': total_slots,
            'hour': hour,
            'day_of_week': day_of_week,
            'is_event': is_event
        })

        model_data = cls.get_model()
        if not model_data:
            return {
                'success': False,
                'predicted_occupied': None,
                'message': "Prediction unavailable — parking model requires training.",
                'model': "Smart_Parking_Occupancy_Forecaster",
                'version': "1.0.0"
            }

        is_weekend = 1 if validated['day_of_week'] >= 5 else 0
        vector = [[
            validated['total_slots'],
            validated['hour'],
            validated['day_of_week'],
            validated['is_event'],
            is_weekend
        ]]

        model = model_data['model']
        pred_occupied = int(round(float(model.predict(vector)[0])))
        pred_occupied = max(0, min(total_slots, pred_occupied))
        pred_available = max(0, total_slots - pred_occupied)
        occupancy_pct = round((pred_occupied / max(total_slots, 1)) * 100.0, 1)

        if occupancy_pct >= 88.0:
            status = "CRITICAL_CONGESTION"
            trend = "Parking bays nearly full. Recommend redirecting to South Overflow Zone."
        elif occupancy_pct >= 65.0:
            status = "MODERATE_OCCUPANCY"
            trend = "Normal academic flow. Vacancies available on upper perimeter."
        else:
            status = "SURPLUS_VACANCY"
            trend = "Ample parking spaces available across all bays."

        return {
            'success': True,
            'total_slots': total_slots,
            'predicted_occupied': pred_occupied,
            'predicted_available': pred_available,
            'occupancy_percentage': occupancy_pct,
            'status': status,
            'trend_summary': trend,
            'model': "Smart_Parking_Occupancy_Forecaster",
            'version': model_data.get('version', '1.0.0')
        }
