import joblib
import numpy as np
from pathlib import Path
from .train import EVENT_TYPE_MAP

MODEL_PATH = Path("models") / "event_attendance_regressor.joblib"

class EventAttendancePredictor:
    _cached_model = None

    @classmethod
    def get_model(cls):
        if cls._cached_model is None and MODEL_PATH.exists():
            cls._cached_model = joblib.load(MODEL_PATH)
        return cls._cached_model

    @classmethod
    def predict_attendance(cls, event):
        """
        Forecasts expected attendance and no-show rate for an event instance.
        """
        model_data = cls.get_model()
        capacity = event.capacity
        event_type_idx = EVENT_TYPE_MAP.get(event.event_type, 3)
        is_weekend = 1 if event.start_time.weekday() >= 5 else 0
        hour = event.start_time.hour
        has_speaker = 1 if event.speaker else 0
        registrations = max(event.registration_count(), int(capacity * 0.75))

        if model_data:
            model = model_data['model']
            vector = [[capacity, event_type_idx, is_weekend, hour, has_speaker, registrations]]
            pred_attendance = int(np.clip(model.predict(vector)[0], 5, capacity))
        else:
            pred_attendance = int(registrations * 0.82)

        no_show_rate = round(max(0.0, ((registrations - pred_attendance) / max(registrations, 1)) * 100.0), 1)

        return {
            'predicted_attendance': pred_attendance,
            'predicted_no_show_rate': no_show_rate,
            'recommended_capacity': int(pred_attendance * 1.15)
        }
