from django.contrib import admin
from .models import MLModelRecord, MLPredictionLog, MLTrainingRun, ModelFeedback, ModelDriftRecord

@admin.register(MLModelRecord)
class MLModelRecordAdmin(admin.ModelAdmin):
    list_display = ('name', 'version', 'task', 'algorithm', 'status', 'is_active', 'trained_at')
    list_filter = ('task', 'status', 'is_active')
    search_fields = ('name', 'algorithm')

@admin.register(MLPredictionLog)
class MLPredictionLogAdmin(admin.ModelAdmin):
    list_display = ('model_name', 'model_version', 'prediction', 'confidence', 'latency_ms', 'status', 'data_mode', 'created_at')
    list_filter = ('model_name', 'status', 'data_mode')
    search_fields = ('model_name', 'prediction', 'input_summary')

@admin.register(MLTrainingRun)
class MLTrainingRunAdmin(admin.ModelAdmin):
    list_display = ('model_name', 'model_version', 'algorithm', 'dataset_size', 'duration_seconds', 'status', 'created_at')
    list_filter = ('model_name', 'status')

@admin.register(ModelFeedback)
class ModelFeedbackAdmin(admin.ModelAdmin):
    list_display = ('model_name', 'actual_outcome', 'error_delta', 'reported_by', 'created_at')
    list_filter = ('model_name',)

@admin.register(ModelDriftRecord)
class ModelDriftRecordAdmin(admin.ModelAdmin):
    list_display = ('model_name', 'metric_name', 'drift_score', 'threshold', 'is_drift_detected', 'detected_at')
    list_filter = ('model_name', 'is_drift_detected')
