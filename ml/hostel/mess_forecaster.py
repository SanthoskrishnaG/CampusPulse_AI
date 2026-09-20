"""
Hostel Residential Mess Demand Forecaster (Sections 59 & 60).
Maintains strict separation between Campus Public Canteen and the 4 CIT Residential Hostels:
- Boys Hostel 1 (BH-1)
- Boys Hostel 2 (BH-2)
- Girls Hostel 1 (GH-1)
- Girls Hostel 2 (GH-2)
"""

from ml.canteen.predict import CanteenDemandPredictor
from ml.canteen.waste_predict import FoodWastePredictor

HOSTEL_RESIDENT_BASE = {
    'BH-1': 380,
    'BH-2': 340,
    'GH-1': 360,
    'GH-2': 320
}

class HostelMessDemandForecaster:
    @classmethod
    def forecast_hostel_mess(cls, hostel_code: str, day_of_week: int, meal_type: str, is_event: bool = False):
        """
        Forecasts residential hostel mess attendance based on assigned resident roll-call base.
        """
        resident_base = HOSTEL_RESIDENT_BASE.get(hostel_code.upper(), 350)
        
        # In residential hostels, weekend demand behaves differently:
        # Weekend lunch/dinner attendance drops ~25% as students visit local homes/outings
        canteen_pred = CanteenDemandPredictor.predict_meal_demand(
            day_of_week=day_of_week,
            meal_type=meal_type,
            is_event_day=is_event,
            student_base=resident_base
        )

        if not canteen_pred.get('success'):
            return canteen_pred

        raw_demand = canteen_pred['predicted_demand']
        # Calibrate demand scaled specifically to hostel resident capacity
        resident_demand = int(round(raw_demand * (resident_base / 520.0)))
        resident_demand = max(40, min(resident_base, resident_demand))

        recommended_prep = int(round(resident_demand * 1.04))

        waste_pred = FoodWastePredictor.predict_waste(
            meals_prepared=recommended_prep,
            predicted_demand=resident_demand,
            meal_type=meal_type,
            day_of_week=day_of_week,
            is_event=is_event
        )

        return {
            'success': True,
            'hostel_code': hostel_code.upper(),
            'resident_base': resident_base,
            'meal_type': meal_type,
            'predicted_demand': resident_demand,
            'recommended_prep': recommended_prep,
            'expected_waste_kg': waste_pred.get('predicted_waste_kg', 3.5),
            'advice': f"Hostel {hostel_code}: Prepare {recommended_prep} portions for {meal_type}. Expected diner turnout: {resident_demand} residents.",
            'model': "Hostel_Mess_Demand_Pipeline",
            'version': "1.1.0"
        }
