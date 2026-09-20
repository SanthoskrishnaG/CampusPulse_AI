import joblib
from pathlib import Path
from .waste_train import MEAL_TYPE_MAP
from ml.utils.validation import validate_food_waste_features

MODEL_PATH = Path("models") / "food_waste_model.joblib"

class FoodWastePredictor:
    _cached_model = None

    @classmethod
    def get_model(cls):
        if cls._cached_model is None and MODEL_PATH.exists():
            cls._cached_model = joblib.load(MODEL_PATH)
        return cls._cached_model

    @classmethod
    def predict_waste(cls, meals_prepared: int, predicted_demand: int, meal_type: str, day_of_week: int, is_event: bool = False):
        """
        Runs real ML inference predicting leftover kitchen food waste (kg).
        """
        validated = validate_food_waste_features({
            'meals_prepared': meals_prepared,
            'predicted_demand': predicted_demand,
            'meal_type': meal_type,
            'day_of_week': day_of_week,
            'is_event': is_event
        })

        model_data = cls.get_model()
        if not model_data:
            return {
                'success': False,
                'predicted_waste_kg': None,
                'message': "Prediction unavailable — model requires training.",
                'model': "Food_Waste_Forecaster",
                'version': "1.0.0"
            }

        meal_idx = MEAL_TYPE_MAP.get(validated['meal_type'], 1)
        vector = [[
            validated['meals_prepared'],
            validated['predicted_demand'],
            meal_idx,
            validated['day_of_week'],
            validated['is_event']
        ]]

        model = model_data['model']
        pred_kg = float(round(float(model.predict(vector)[0]), 1))
        pred_kg = max(0.5, pred_kg)

        surplus_portions = max(0, meals_prepared - predicted_demand)
        advice = (
            f"Overproduction buffer is {surplus_portions} portions. "
            f"Estimated waste: {pred_kg} kg. "
            f"{'Recommend reducing batch by 15 portions to prevent excessive surplus.' if pred_kg > 10.0 else 'Waste is within acceptable institutional threshold.'}"
        )

        return {
            'success': True,
            'predicted_waste_kg': pred_kg,
            'surplus_portions': surplus_portions,
            'advice': advice,
            'model': "Food_Waste_Forecaster",
            'version': model_data.get('version', '1.0.0')
        }
