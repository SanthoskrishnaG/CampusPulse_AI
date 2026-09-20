import re
import time
import json
import joblib
import numpy as np
from pathlib import Path
from django.conf import settings
from ml.utils.validation import validate_complaint_text

MODEL_PATH = Path("models") / "complaint_classifier.joblib"

DEPT_ROUTING = {
    'ELECTRICAL': 'Electrical & Power Systems Division',
    'WATER': 'Plumbing & Water Infrastructure',
    'SANITATION': 'Housekeeping & Campus Hygiene',
    'CLASSROOM': 'Estate & Classroom Facilities',
    'LABORATORY': 'Central Computing & Lab Tech Support',
    'TRANSPORT': 'Campus Transport & Fleet Management',
    'HOSTEL': 'Chief Warden & Hostel Office',
    'CANTEEN': 'Canteen & Dining Services Committee',
    'PARKING': 'Campus Security & Traffic Management',
    'NETWORK': 'IT Network Operations Center (NOC)',
    'SECURITY': 'Campus Security Department',
    'ACADEMIC': 'Academic Affairs & Dean Office',
    'INFRASTRUCTURE': 'Civil Engineering & Maintenance',
    'OTHER': 'General Administrative Cell'
}

URGENT_KEYWORDS = ['spark', 'shock', 'fire', 'smoke', 'short circuit', 'gas', 'danger', 'flood', 'burst', 'accident', 'overflowing']
HIGH_KEYWORDS = ['not working', 'completely off', 'broken', 'urgent', 'leakage', 'failed', 'dead', 'no water', 'jammed']

class ComplaintAITriage:
    _cached_model = None

    @classmethod
    def get_model(cls):
        if cls._cached_model is None and MODEL_PATH.exists():
            cls._cached_model = joblib.load(MODEL_PATH)
        return cls._cached_model

    @classmethod
    def triage_complaint(cls, text: str, user=None):
        """
        Analyzes natural language complaint text using NLP pipeline.
        Returns: category, priority, target_department, location_extracted, confidence, sla_hours.
        Persists inference to MLPredictionLog.
        """
        start_time = time.time()
        validated_text = validate_complaint_text(text)
        text_lower = validated_text.lower()

        model_data = cls.get_model()
        if not model_data:
            return {
                'success': False,
                'category': 'INFRASTRUCTURE',
                'priority': 'MEDIUM',
                'target_department': 'General Maintenance',
                'location_extracted': 'Campus Premises',
                'confidence': None,
                'sla_hours': 24,
                'message': "Prediction unavailable — complaint classification model requires training.",
                'model_name': "Campus_Complaint_Classifier",
                'model_version': "1.0.0"
            }

        pipeline = model_data['pipeline']
        probs = pipeline.predict_proba([validated_text])[0]
        category = str(pipeline.predict([validated_text])[0])
        confidence = float(round(float(np.max(probs)), 3))

        # Priority Assessment
        if any(w in text_lower for w in URGENT_KEYWORDS):
            priority = 'URGENT'
            sla_hours = 4
        elif any(w in text_lower for w in HIGH_KEYWORDS):
            priority = 'HIGH'
            sla_hours = 12
        elif len(validated_text.split()) > 15:
            priority = 'MEDIUM'
            sla_hours = 24
        else:
            priority = 'LOW'
            sla_hours = 48

        # Entity Extraction: Location / Room / Block
        block_match = re.search(r'\b(block\s+[a-z0-9]+|tower\s+[a-z0-9]+)\b', validated_text, re.IGNORECASE)
        room_match = re.search(r'\b(room\s+[0-9]+|hall\s+[0-9]+|lab\s+[0-9]+|cabin\s+[0-9]+)\b', validated_text, re.IGNORECASE)
        place_match = re.search(r'\b(library|canteen|auditorium|cafeteria|parking lot|gate\s+[0-9]+)\b', validated_text, re.IGNORECASE)

        loc_parts = []
        if block_match:
            loc_parts.append(block_match.group(0).title())
        if room_match:
            loc_parts.append(room_match.group(0).title())
        if place_match and not (block_match or room_match):
            loc_parts.append(place_match.group(0).title())

        location = ", ".join(loc_parts) if loc_parts else "Campus Premises"
        target_department = DEPT_ROUTING.get(category, 'General Maintenance')

        latency_ms = round((time.time() - start_time) * 1000.0, 2)
        data_mode = getattr(settings, 'DATA_MODE', 'DEMO')

        # Persist to MLPredictionLog
        try:
            from apps.analytics.models import MLPredictionLog
            MLPredictionLog.objects.create(
                model_name="Campus_Complaint_Classifier",
                model_version=model_data.get('version', '1.0.0'),
                task="NLP",
                input_summary=json.dumps({'text_sample': validated_text[:120]}),
                prediction=category,
                confidence=confidence,
                factors_json=json.dumps([f"Department: {target_department}", f"Priority: {priority}", f"Location: {location}"]),
                latency_ms=latency_ms,
                status=MLPredictionLog.Status.SUCCESS,
                data_mode=data_mode,
                user=user
            )
        except Exception:
            pass

        return {
            'success': True,
            'category': category,
            'priority': priority,
            'target_department': target_department,
            'location_extracted': location,
            'confidence': confidence,
            'sla_hours': sla_hours,
            'latency_ms': latency_ms,
            'model_name': "Campus_Complaint_Classifier",
            'model_version': model_data.get('version', '1.0.0')
        }
