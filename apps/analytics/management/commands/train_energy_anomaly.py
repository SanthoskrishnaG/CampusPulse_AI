import time
import json
from django.core.management.base import BaseCommand
from ml.energy.train import train_energy_anomaly_model
from apps.analytics.models import MLTrainingRun

class Command(BaseCommand):
    help = "Trains, evaluates, and registers Unsupervised Energy Anomaly Detection model."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Initiating Energy Anomaly Detection Model Training..."))
        start_time = time.time()
        try:
            model, metrics = train_energy_anomaly_model()
            duration = round(time.time() - start_time, 2)
            MLTrainingRun.objects.create(
                model_name="Energy_Anomaly_Detector",
                model_version="1.0.0",
                algorithm="IsolationForest",
                dataset_size=metrics.get('samples_trained', 1000),
                test_metrics_json=json.dumps(metrics),
                duration_seconds=duration,
                status=MLTrainingRun.Status.SUCCESS,
                notes=f"Trained IsolationForest with contamination: {metrics.get('contamination', 0.06)}"
            )
            self.stdout.write(self.style.SUCCESS(f"Successfully trained Energy Anomaly model in {duration}s! Samples: {metrics.get('samples_trained')}"))
        except Exception as e:
            duration = round(time.time() - start_time, 2)
            MLTrainingRun.objects.create(
                model_name="Energy_Anomaly_Detector",
                model_version="1.0.0",
                algorithm="IsolationForest",
                duration_seconds=duration,
                status=MLTrainingRun.Status.FAILED,
                notes=str(e)
            )
            self.stderr.write(self.style.ERROR(f"Training failed: {e}"))
