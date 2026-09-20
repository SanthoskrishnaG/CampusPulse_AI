import time
import json
import joblib
from pathlib import Path
from django.conf import settings
from .train import MEAL_TYPE_MAP
from ml.utils.validation import validate_canteen_features

MODEL_PATH = Path("models") / "canteen_demand_model.joblib"

class CanteenDemandPredictor:
    _cached_model = None

    @classmethod
    def get_model(cls):
        if cls._cached_model is None and MODEL_PATH.exists():
            cls._cached_model = joblib.load(MODEL_PATH)
        return cls._cached_model

    @classmethod
    def predict_meal_demand(cls, day_of_week: int, meal_type: str, is_event_day: bool = False, student_base: int = 520, user=None):
        """
        Predicts expected food demand and recommended preparation count for a given meal.
        Logs prediction to MLPredictionLog.
        """
        start_time = time.time()
        validated = validate_canteen_features({
            'day_of_week': day_of_week,
            'meal_type': meal_type,
            'is_event': is_event_day,
            'is_weekend': (1 if day_of_week >= 5 else 0),
            'student_base': student_base
        })

        model_data = cls.get_model()
        if not model_data:
            return {
                'success': False,
                'predicted_demand': None,
                'recommended_prep': None,
                'message': "Prediction unavailable — canteen demand model requires training.",
                'model': "Canteen_Food_Demand_Forecaster",
                'version': "1.1.0"
            }

        meal_idx = MEAL_TYPE_MAP.get(validated['meal_type'], 1)
        vector = [[
            validated['day_of_week'],
            meal_idx,
            validated['is_event'],
            validated['is_weekend'],
            validated['student_base']
        ]]

        model = model_data['model']
        pred_demand = int(round(float(model.predict(vector)[0])))
        pred_demand = max(20, pred_demand)

        # 5% safety margin over predicted demand for prep
        recommended_prep = int(round(pred_demand * 1.05))

        latency_ms = round((time.time() - start_time) * 1000.0, 2)
        data_mode = getattr(settings, 'DATA_MODE', 'DEMO')

        # Log prediction to DB
        try:
            from apps.analytics.models import MLPredictionLog
            MLPredictionLog.objects.create(
                model_name="Canteen_Food_Demand_Forecaster",
                model_version=model_data.get('version', '1.1.0'),
                task="REGRESSION",
                input_summary=json.dumps({
                    'day_of_week': day_of_week,
                    'meal_type': meal_type,
                    'is_event': is_event_day,
                    'student_base': student_base
                }),
                prediction=str(pred_demand),
                latency_ms=latency_ms,
                status=MLPredictionLog.Status.SUCCESS,
                data_mode=data_mode,
                user=user
            )
        except Exception:
            pass

        return {
            'success': True,
            'predicted_demand': pred_demand,
            'recommended_prep': recommended_prep,
            'advice': f"Prepare ~{recommended_prep} meal portions for {validated['meal_type']}. Anticipated dining demand: {pred_demand}.",
            'latency_ms': latency_ms,
            'model': "Canteen_Food_Demand_Forecaster",
            'version': model_data.get('version', '1.1.0')
        }
