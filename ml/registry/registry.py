import json
import os
from pathlib import Path
from django.conf import settings

REGISTRY_FILE = Path(settings.BASE_DIR) / 'models' / 'model_registry.json'

class ModelRegistry:
    """
    Central Model Registry for CampusPulse AI.
    Provides dual persistence:
    1. Local JSON artifact repository (models/model_registry.json) for fast offline access.
    2. Django Database (apps.analytics.models.MLModelRecord) for administrative auditability and queries.
    """

    @staticmethod
    def _load_registry():
        if REGISTRY_FILE.exists():
            try:
                with open(REGISTRY_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    @staticmethod
    def _save_registry(data):
        REGISTRY_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(REGISTRY_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    @classmethod
    def register_model(cls, model_name, version, algorithm, metrics, feature_list, model_path, description="", task="CLASSIFICATION", status="PRODUCTION"):
        data = cls._load_registry()
        data[model_name] = {
            'version': str(version),
            'task': str(task),
            'algorithm': str(algorithm),
            'metrics': metrics,
            'features': feature_list,
            'model_path': str(model_path),
            'description': description,
            'status': status,
            'is_active': True
        }
        cls._save_registry(data)

        # Sync with Django DB if DB is accessible
        try:
            from apps.analytics.models import MLModelRecord
            MLModelRecord.objects.update_or_create(
                name=model_name,
                defaults={
                    'version': str(version),
                    'task': task,
                    'algorithm': str(algorithm),
                    'metrics_json': json.dumps(metrics),
                    'features_json': json.dumps(feature_list),
                    'model_path': str(model_path),
                    'description': description,
                    'status': status,
                    'is_active': True,
                }
            )
        except Exception:
            pass

        return data[model_name]

    @classmethod
    def get_all_models(cls):
        registry_data = cls._load_registry()
        # Optionally enrich with DB records if available
        try:
            from apps.analytics.models import MLModelRecord
            db_records = {r.name: r for r in MLModelRecord.objects.all()}
            for name, rec in db_records.items():
                if name not in registry_data:
                    registry_data[name] = {
                        'version': rec.version,
                        'task': rec.task,
                        'algorithm': rec.algorithm,
                        'metrics': rec.get_metrics(),
                        'features': rec.get_features(),
                        'model_path': rec.model_path,
                        'description': rec.description,
                        'status': rec.status,
                        'is_active': rec.is_active
                    }
        except Exception:
            pass
        return registry_data

    @classmethod
    def get_model_info(cls, model_name):
        models = cls.get_all_models()
        return models.get(model_name, None)

    @classmethod
    def check_model_readiness(cls, model_name):
        """
        Reports comprehensive 5-stage model readiness status (Section 63):
        - data_available
        - model_trained
        - model_validated
        - model_deployed
        - real_time_inference_available
        """
        info = cls.get_model_info(model_name)
        if not info:
            return {
                'model_name': model_name,
                'data_available': False,
                'model_trained': False,
                'model_validated': False,
                'model_deployed': False,
                'real_time_inference_available': False,
                'status': 'UNREGISTERED'
            }

        model_path = Path(settings.BASE_DIR) / info.get('model_path', '')
        file_exists = model_path.exists()
        has_metrics = bool(info.get('metrics'))
        is_prod = info.get('status') == 'PRODUCTION' and info.get('is_active', False)

        return {
            'model_name': model_name,
            'data_available': True,
            'model_trained': file_exists,
            'model_validated': has_metrics,
            'model_deployed': file_exists and is_prod,
            'real_time_inference_available': file_exists and is_prod,
            'version': info.get('version', '1.0.0'),
            'algorithm': info.get('algorithm', 'Unknown'),
            'metrics': info.get('metrics', {}),
            'status': info.get('status', 'STAGING')
        }
