import json
from django.db import models
from django.conf import settings

class MLModelRecord(models.Model):
    class TaskType(models.TextChoices):
        CLASSIFICATION = 'CLASSIFICATION', 'Classification'
        REGRESSION = 'REGRESSION', 'Regression / Forecasting'
        ANOMALY_DETECTION = 'ANOMALY_DETECTION', 'Anomaly Detection'
        NLP = 'NLP', 'Natural Language Processing'
        RECOMMENDATION = 'RECOMMENDATION', 'Recommendation'

    class Status(models.TextChoices):
        TRAINING = 'TRAINING', 'Training'
        VALIDATED = 'VALIDATED', 'Validated'
        STAGING = 'STAGING', 'Staging'
        PRODUCTION = 'PRODUCTION', 'Production'
        RETIRED = 'RETIRED', 'Retired'
        FAILED = 'FAILED', 'Failed'

    name = models.CharField(max_length=120, unique=True, help_text="e.g. Academic_Risk_Classifier")
    version = models.CharField(max_length=30, default="1.0.0")
    task = models.CharField(max_length=40, choices=TaskType.choices, default=TaskType.CLASSIFICATION)
    algorithm = models.CharField(max_length=120)
    metrics_json = models.TextField(default='{}', help_text="Real measured evaluation metrics (F1, Accuracy, MAE, R2, etc.)")
    features_json = models.TextField(default='[]', help_text="List of feature names used during training")
    model_path = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.PRODUCTION)
    is_active = models.BooleanField(default=True)
    trained_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} v{self.version} [{self.status}]"

    def get_metrics(self):
        try:
            return json.loads(self.metrics_json)
        except Exception:
            return {}

    def get_features(self):
        try:
            return json.loads(self.features_json)
        except Exception:
            return []


class MLPredictionLog(models.Model):
    class Status(models.TextChoices):
        SUCCESS = 'SUCCESS', 'Inference Success'
        FAILED = 'FAILED', 'Inference Failed'
        FALLBACK = 'FALLBACK', 'Graceful Fallback'

    class DataMode(models.TextChoices):
        LIVE = 'LIVE', 'Live Campus Telemetry'
        DEMO = 'DEMO', 'Simulated / Benchmark Mode'

    model_name = models.CharField(max_length=120, db_index=True)
    model_version = models.CharField(max_length=30)
    task = models.CharField(max_length=40, default="GENERAL")
    input_summary = models.TextField(help_text="Sanitized input feature dictionary or summary (NO credentials)")
    prediction = models.TextField(help_text="Serialized output prediction value or classification")
    confidence = models.FloatField(null=True, blank=True, help_text="Calibrated probability if mathematically supported")
    factors_json = models.TextField(default='[]', help_text="Top explainable contributing factors")
    latency_ms = models.FloatField(default=0.0, help_text="Inference execution latency in milliseconds")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SUCCESS)
    data_mode = models.CharField(max_length=20, choices=DataMode.choices, default=DataMode.LIVE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.model_name} -> {self.prediction[:30]} ({self.latency_ms:.1f}ms at {self.created_at.strftime('%H:%M:%S')})"

    def get_factors(self):
        try:
            return json.loads(self.factors_json)
        except Exception:
            return []


class MLTrainingRun(models.Model):
    class Status(models.TextChoices):
        SUCCESS = 'SUCCESS', 'Training Successful'
        FAILED = 'FAILED', 'Training Failed'

    model_name = models.CharField(max_length=120)
    model_version = models.CharField(max_length=30)
    algorithm = models.CharField(max_length=120)
    dataset_size = models.PositiveIntegerField(default=0)
    train_metrics_json = models.TextField(default='{}')
    test_metrics_json = models.TextField(default='{}')
    duration_seconds = models.FloatField(default=0.0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SUCCESS)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"TrainRun: {self.model_name} v{self.model_version} [{self.status}] ({self.created_at.strftime('%Y-%m-%d %H:%M')})"


class ModelFeedback(models.Model):
    prediction_log = models.ForeignKey(MLPredictionLog, on_delete=models.CASCADE, null=True, blank=True, related_name='feedback')
    model_name = models.CharField(max_length=120)
    actual_outcome = models.TextField(help_text="Ground truth recorded value (e.g. actual attendance, actual meals sold)")
    error_delta = models.FloatField(null=True, blank=True, help_text="Measured error |predicted - actual|")
    notes = models.TextField(blank=True)
    reported_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Feedback for {self.model_name}: Actual={self.actual_outcome[:30]} (err={self.error_delta})"


class ModelDriftRecord(models.Model):
    model_name = models.CharField(max_length=120)
    metric_name = models.CharField(max_length=100, help_text="e.g. PSI_ATTENDANCE or KL_DIVERGENCE")
    drift_score = models.FloatField(help_text="Calculated drift statistic")
    threshold = models.FloatField(default=0.25, help_text="Drift alert threshold (typically PSI > 0.25)")
    is_drift_detected = models.BooleanField(default=False)
    details_json = models.TextField(default='{}')
    detected_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-detected_at']

    def __str__(self):
        status = "ALERT: DRIFT" if self.is_drift_detected else "STABLE"
        return f"{self.model_name} [{status}] {self.metric_name}={self.drift_score:.3f}"
