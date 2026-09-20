import time
import json
from django.core.management.base import BaseCommand
from ml.canteen.train import train_canteen_demand_model
from apps.analytics.models import MLTrainingRun

class Command(BaseCommand):
    help = "Trains, evaluates, and registers Canteen Food Demand forecasting model."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Initiating Canteen Demand Model Training..."))
        start_time = time.time()
        try:
            model, metrics = train_canteen_demand_model()
            duration = round(time.time() - start_time, 2)
            MLTrainingRun.objects.create(
                model_name="Canteen_Food_Demand_Forecaster",
                model_version="1.1.0",
                algorithm="RandomForestRegressor",
                dataset_size=1000,
                test_metrics_json=json.dumps(metrics),
                duration_seconds=duration,
                status=MLTrainingRun.Status.SUCCESS,
                notes=f"Trained RandomForestRegressor with R2: {metrics.get('r2_score', 0)}, MAE: {metrics.get('mae', 0)}"
            )
            self.stdout.write(self.style.SUCCESS(f"Successfully trained Canteen Demand model in {duration}s! R2: {metrics.get('r2_score')}, MAE: {metrics.get('mae')}"))
        except Exception as e:
            duration = round(time.time() - start_time, 2)
            MLTrainingRun.objects.create(
                model_name="Canteen_Food_Demand_Forecaster",
                model_version="1.1.0",
                algorithm="RandomForestRegressor",
                duration_seconds=duration,
                status=MLTrainingRun.Status.FAILED,
                notes=str(e)
            )
            self.stderr.write(self.style.ERROR(f"Training failed: {e}"))
