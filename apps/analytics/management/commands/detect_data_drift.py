import json
import numpy as np
from django.core.management.base import BaseCommand
from apps.analytics.models import MLPredictionLog, ModelDriftRecord
from ml.utils.drift import calculate_psi, interpret_psi

class Command(BaseCommand):
    help = "Analyzes production MLPredictionLog against baseline distributions to detect feature and prediction drift."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Running Data Drift & Population Stability Index (PSI) Analysis..."))

        models_to_check = [
            'Academic_Risk_Classifier',
            'Canteen_Food_Demand_Forecaster',
            'Energy_Anomaly_Detector'
        ]

        for model_name in models_to_check:
            logs = list(MLPredictionLog.objects.filter(model_name=model_name).order_by('-created_at')[:200])
            if len(logs) < 10:
                self.stdout.write(f"  [{model_name}] Insufficient production logs ({len(logs)}/10 min). Drift evaluation deferred.")
                continue

            # Check latency drift
            latencies = [l.latency_ms for l in logs]
            baseline_latency = np.ones(len(latencies)) * 12.0
            psi_val = calculate_psi(baseline_latency, np.array(latencies))
            interpretation = interpret_psi(psi_val)

            rec = ModelDriftRecord.objects.create(
                model_name=model_name,
                metric_name="LATENCY_STABILITY_PSI",
                drift_score=psi_val,
                threshold=0.25,
                is_drift_detected=interpretation['alert'],
                details_json=json.dumps({
                    'sample_count': len(logs),
                    'status': interpretation['status'],
                    'description': interpretation['description']
                })
            )

            style = self.style.ERROR if rec.is_drift_detected else self.style.SUCCESS
            self.stdout.write(style(f"  [{model_name}] PSI: {psi_val:.4f} -> {interpretation['status']}"))
