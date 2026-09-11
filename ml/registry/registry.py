import json
import os
from pathlib import Path
from django.conf import settings

REGISTRY_FILE = Path(settings.BASE_DIR) / 'models' / 'model_registry.json'

class ModelRegistry:
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
    def register_model(cls, model_name, version, algorithm, metrics, feature_list, model_path, description=""):
        data = cls._load_registry()
        data[model_name] = {
            'version': version,
            'algorithm': algorithm,
            'metrics': metrics,
            'features': feature_list,
            'model_path': str(model_path),
            'description': description,
            'is_active': True
        }
        cls._save_registry(data)
        return data[model_name]

    @classmethod
    def get_all_models(cls):
        return cls._load_registry()

    @classmethod
    def get_model_info(cls, model_name):
        return cls._load_registry().get(model_name, None)
