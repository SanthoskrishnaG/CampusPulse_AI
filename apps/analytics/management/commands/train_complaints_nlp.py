import time
import json
from django.core.management.base import BaseCommand
from ml.complaints.train import train_complaint_classifier
from apps.analytics.models import MLTrainingRun

class Command(BaseCommand):
    help = "Trains, evaluates, and registers Campus Complaint NLP classification model."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Initiating Complaint NLP Classifier Training..."))
        start_time = time.time()
        try:
            pipeline, metrics = train_complaint_classifier()
            duration = round(time.time() - start_time, 2)
            MLTrainingRun.objects.create(
                model_name="Campus_Complaint_Classifier",
                model_version="1.0.0",
                algorithm="TF-IDF + Logistic Regression",
                dataset_size=metrics.get('num_samples', 136),
                test_metrics_json=json.dumps(metrics),
                duration_seconds=duration,
                status=MLTrainingRun.Status.SUCCESS,
                notes=f"Trained TF-IDF + Logistic Regression with F1: {metrics.get('f1_score', 0)}"
            )
            self.stdout.write(self.style.SUCCESS(f"Successfully trained Complaint NLP classifier in {duration}s! F1: {metrics.get('f1_score')}"))
        except Exception as e:
            duration = round(time.time() - start_time, 2)
            MLTrainingRun.objects.create(
                model_name="Campus_Complaint_Classifier",
                model_version="1.0.0",
                algorithm="TF-IDF + Logistic Regression",
                duration_seconds=duration,
                status=MLTrainingRun.Status.FAILED,
                notes=str(e)
            )
            self.stderr.write(self.style.ERROR(f"Training failed: {e}"))
