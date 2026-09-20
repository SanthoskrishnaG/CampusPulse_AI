import time
import json
from django.core.management.base import BaseCommand
from ml.transport.train import train_transport_models
from apps.analytics.models import MLTrainingRun

class Command(BaseCommand):
    help = "Trains, evaluates, and registers Smart Transport Route ETA and Delay model."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Initiating Transport ETA Model Training..."))
        start_time = time.time()
        try:
            model, metrics = train_transport_models()
            duration = round(time.time() - start_time, 2)
            MLTrainingRun.objects.create(
                model_name="Smart_Transport_ETA_Predictor",
                model_version="1.0.0",
                algorithm="RandomForestRegressor",
                dataset_size=1200,
                test_metrics_json=json.dumps(metrics),
                duration_seconds=duration,
                status=MLTrainingRun.Status.SUCCESS,
                notes=f"Trained RandomForestRegressor with R2: {metrics.get('r2_score', 0)}, MAE: {metrics.get('mae', 0)} mins"
            )
            self.stdout.write(self.style.SUCCESS(f"Successfully trained Transport ETA model in {duration}s! R2: {metrics.get('r2_score')}, MAE: {metrics.get('mae')} mins"))
        except Exception as e:
            duration = round(time.time() - start_time, 2)
            MLTrainingRun.objects.create(
                model_name="Smart_Transport_ETA_Predictor",
                model_version="1.0.0",
                algorithm="RandomForestRegressor",
                duration_seconds=duration,
                status=MLTrainingRun.Status.FAILED,
                notes=str(e)
            )
            self.stderr.write(self.style.ERROR(f"Training failed: {e}"))
