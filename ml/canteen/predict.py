import joblib
import numpy as np
from pathlib import Path
from .train import MEAL_TYPE_MAP

MODEL_PATH = Path("models") / "canteen_demand_model.joblib"

class CanteenDemandPredictor:
    _cached_model = None

    @classmethod
    def get_model(cls):
        if cls._cached_model is None and MODEL_PATH.exists():
            cls._cached_model = joblib.load(MODEL_PATH)
        return cls._cached_model

    @classmethod
    def predict_meal_demand(cls, day_of_week, meal_type, is_event_day=False, student_base=520):
        """
        Predicts expected food demand and recommended prep count for a given meal.
        """
        model_data = cls.get_model()
        meal_idx = MEAL_TYPE_MAP.get(meal_type, 1)
        is_weekend = 1 if day_of_week >= 5 else 0
        is_event = 1 if is_event_day else 0

        if model_data:
            model = model_data['model']
            vector = [[day_of_week, meal_idx, is_event, is_weekend, student_base]]
            pred_demand = int(model.predict(vector)[0])
        else:
            # Heuristic default
            base = 360 if meal_type == 'LUNCH' else (180 if meal_type == 'BREAKFAST' else 210)
            if is_weekend:
                base = int(base * 0.45)
            if is_event:
                base = int(base * 1.25)
            pred_demand = base

        # Recommended buffer: 6% safety margin over predicted demand
        recommended_prep = int(pred_demand * 1.06)
        expected_waste_kg = round(max(1.2, (recommended_prep - pred_demand) * 0.28), 1)

        return {
            'predicted_demand': pred_demand,
            'recommended_prep': recommended_prep,
            'expected_waste_kg': expected_waste_kg,
            'advice': f"Prepare approximately {recommended_prep} portions for {meal_type}. Expected surplus waste < {expected_waste_kg} kg."
        }
