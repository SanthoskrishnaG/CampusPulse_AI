import time
import json
from django.core.management.base import BaseCommand
from ml.canteen.waste_train import train_food_waste_model
from apps.analytics.models import MLTrainingRun

class Command(BaseCommand):
    help = "Trains, evaluates, and registers Kitchen Food Waste regression model."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Initiating Food Waste Model Training..."))
        start_time = time.time()
        try:
            model, metrics = train_food_waste_model()
            duration = round(time.time() - start_time, 2)
            MLTrainingRun.objects.create(
                model_name="Food_Waste_Forecaster",
                model_version="1.0.0",
                algorithm="GradientBoostingRegressor",
                dataset_size=900,
                test_metrics_json=json.dumps(metrics),
                duration_seconds=duration,
                status=MLTrainingRun.Status.SUCCESS,
                notes=f"Trained GradientBoostingRegressor with R2: {metrics.get('r2_score', 0)}, MAE: {metrics.get('mae', 0)} kg"
            )
            self.stdout.write(self.style.SUCCESS(f"Successfully trained Food Waste model in {duration}s! R2: {metrics.get('r2_score')}, MAE: {metrics.get('mae')} kg"))
        except Exception as e:
            duration = round(time.time() - start_time, 2)
            MLTrainingRun.objects.create(
                model_name="Food_Waste_Forecaster",
                model_version="1.0.0",
                algorithm="GradientBoostingRegressor",
                duration_seconds=duration,
                status=MLTrainingRun.Status.FAILED,
                notes=str(e)
            )
            self.stderr.write(self.style.ERROR(f"Training failed: {e}"))
