from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from .models import Canteen, MenuItem, MealRecord
from ml.canteen.predict import CanteenDemandPredictor

def canteen_dashboard(request):
    """
    Canteen Management & Demand Forecast Portal:
    Preparation recommendations, sales telemetry, and food waste reduction trackers.
    """
    canteen = Canteen.objects.first()
    menu_items = MenuItem.objects.filter(is_available=True)
    recent_records = MealRecord.objects.all()[:10]

    # Forecast for today's meals
    today = timezone.now().date()
    day_of_week = today.weekday()

    forecasts = {
        'BREAKFAST': CanteenDemandPredictor.predict_meal_demand(day_of_week, 'BREAKFAST'),
        'LUNCH': CanteenDemandPredictor.predict_meal_demand(day_of_week, 'LUNCH'),
        'SNACKS': CanteenDemandPredictor.predict_meal_demand(day_of_week, 'SNACKS'),
        'DINNER': CanteenDemandPredictor.predict_meal_demand(day_of_week, 'DINNER'),
    }

    return render(request, 'canteen/dashboard.html', {
        'canteen': canteen,
        'menu_items': menu_items,
        'recent_records': recent_records,
        'forecasts': forecasts,
        'today': today,
    })

def record_meal_sales(request):
    """
    Allows canteen staff to log actual prepared vs sold counts to close the ML feedback loop!
    """
    if request.method == 'POST':
        canteen = Canteen.objects.first()
        meal_type = request.POST.get('meal_type', 'LUNCH')
        prep = int(request.POST.get('meals_prepared', 300))
        sold = int(request.POST.get('meals_sold', 285))
        leftover = float(request.POST.get('leftover_waste_kg', max(0.5, (prep - sold) * 0.3)))

        MealRecord.objects.create(
            canteen=canteen,
            date=timezone.now().date(),
            meal_type=meal_type,
            meals_prepared=prep,
            meals_sold=sold,
            leftover_waste_kg=leftover
        )

        messages.success(request, f"Logged {meal_type} actual sales ({sold}/{prep} sold, leftover: {leftover} kg). Fed into model evaluation pipeline.")
        return redirect('canteen:dashboard')

    return redirect('canteen:dashboard')
