import time
import json
from django.core.management.base import BaseCommand
from ml.academic.train import train_academic_risk_models
from ml.academic.sequential_model import SequentialStudentTrajectoryModel
from apps.analytics.models import MLTrainingRun

class Command(BaseCommand):
    help = "Trains, evaluates, and registers Academic Risk classification and trajectory models."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Initiating Academic Risk Model Training..."))
        start_time = time.time()
        try:
            name, metrics = train_academic_risk_models()
            seq_model = SequentialStudentTrajectoryModel()
            seq_model.train_and_save()

            duration = round(time.time() - start_time, 2)
            MLTrainingRun.objects.create(
                model_name="Academic_Risk_Classifier",
                model_version="1.0.0",
                algorithm=name,
                dataset_size=1200,
                test_metrics_json=json.dumps(metrics),
                duration_seconds=duration,
                status=MLTrainingRun.Status.SUCCESS,
                notes=f"Trained champion {name} with F1 score {metrics.get('f1_score', 0)}"
            )
            self.stdout.write(self.style.SUCCESS(f"Successfully trained Academic Risk models in {duration}s! Champion: {name} (F1: {metrics.get('f1_score')})"))
        except Exception as e:
            duration = round(time.time() - start_time, 2)
            MLTrainingRun.objects.create(
                model_name="Academic_Risk_Classifier",
                model_version="1.0.0",
                algorithm="Unknown",
                duration_seconds=duration,
                status=MLTrainingRun.Status.FAILED,
                notes=str(e)
            )
            self.stderr.write(self.style.ERROR(f"Training failed: {e}"))
