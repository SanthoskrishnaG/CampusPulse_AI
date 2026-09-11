from django.core.management.base import BaseCommand
from ml.academic.train import train_academic_risk_models
from ml.academic.sequential_model import SequentialStudentTrajectoryModel
from ml.complaints.train import train_complaint_classifier
from ml.events.train import train_event_attendance_model
from ml.canteen.train import train_canteen_demand_model
from ml.energy.train import train_energy_anomaly_model

class Command(BaseCommand):
    help = 'Trains and calibrates all CampusPulse AI machine learning and deep learning models.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Starting CampusPulse AI Model Training & Calibration Suite..."))

        self.stdout.write("1/6 Training Academic Risk Ensemble Classifier...")
        name, metrics = train_academic_risk_models()
        self.stdout.write(self.style.SUCCESS(f"[OK] Champion Academic Model: {name} (F1: {metrics['f1_score']})"))

        self.stdout.write("2/6 Training Academic Sequential Deep Learning Trajectory Network...")
        seq_acc = SequentialStudentTrajectoryModel().train_and_save()
        self.stdout.write(self.style.SUCCESS(f"[OK] Sequential Trajectory DL Model: (Accuracy: {seq_acc:.4f})"))

        self.stdout.write("3/6 Training Campus Complaint NLP Triage Classifier...")
        _, comp_metrics = train_complaint_classifier()
        self.stdout.write(self.style.SUCCESS(f"[OK] Complaint Classifier: (Accuracy: {comp_metrics['accuracy']})"))

        self.stdout.write("4/6 Training Event Attendance Regressor...")
        _, ev_metrics = train_event_attendance_model()
        self.stdout.write(self.style.SUCCESS(f"[OK] Event Attendance Forecaster: (R2: {ev_metrics['r2_score']})"))

        self.stdout.write("5/6 Training Canteen Food Demand & Waste Forecaster...")
        _, cant_metrics = train_canteen_demand_model()
        self.stdout.write(self.style.SUCCESS(f"[OK] Canteen Demand Forecaster: (R2: {cant_metrics['r2_score']})"))

        self.stdout.write("6/6 Training Campus Energy Anomaly Isolation Forest...")
        train_energy_anomaly_model()
        self.stdout.write(self.style.SUCCESS("[OK] Energy Isolation Forest Anomaly Detector Ready"))

        self.stdout.write(self.style.SUCCESS("\n[SUCCESS] All 6 ML & Deep Learning models successfully trained and registered in Model Registry!"))
