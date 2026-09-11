import re
import joblib
import numpy as np
from pathlib import Path

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
    def triage_complaint(cls, text):
        """
        Analyzes natural language complaint text.
        Returns: category, priority, target_department, location_extracted, confidence, sla_hours
        """
        model_data = cls.get_model()
        text_lower = text.lower()

        if model_data:
            pipeline = model_data['pipeline']
            probs = pipeline.predict_proba([text])[0]
            category = str(pipeline.predict([text])[0])
            confidence = float(np.max(probs))
        else:
            # Heuristic category fallback
            if any(k in text_lower for k in ['fan', 'light', 'ac', 'switch', 'power', 'socket']):
                category = 'ELECTRICAL'
            elif any(k in text_lower for k in ['water', 'tap', 'leak', 'flush', 'washroom', 'restroom']):
                category = 'WATER'
            elif any(k in text_lower for k in ['wifi', 'network', 'lan', 'internet']):
                category = 'NETWORK'
            elif any(k in text_lower for k in ['bus', 'route', 'driver']):
                category = 'TRANSPORT'
            elif any(k in text_lower for k in ['food', 'canteen', 'lunch']):
                category = 'CANTEEN'
            elif any(k in text_lower for k in ['parking', 'vehicle', 'car', 'bike']):
                category = 'PARKING'
            else:
                category = 'INFRASTRUCTURE'
            confidence = 0.82

        # Priority Assessment
        if any(w in text_lower for w in URGENT_KEYWORDS):
            priority = 'URGENT'
            sla_hours = 4
        elif any(w in text_lower for w in HIGH_KEYWORDS):
            priority = 'HIGH'
            sla_hours = 12
        elif len(text.split()) > 15:
            priority = 'MEDIUM'
            sla_hours = 24
        else:
            priority = 'LOW'
            sla_hours = 48

        # Entity Extraction: Location / Room / Block
        location = ""
        block_match = re.search(r'\b(block\s+[a-z0-9]+|tower\s+[a-z0-9]+)\b', text, re.IGNORECASE)
        room_match = re.search(r'\b(room\s+[0-9]+|hall\s+[0-9]+|lab\s+[0-9]+|cabin\s+[0-9]+)\b', text, re.IGNORECASE)
        place_match = re.search(r'\b(library|canteen|auditorium|cafeteria|parking lot|gate\s+[0-9]+)\b', text, re.IGNORECASE)

        loc_parts = []
        if block_match:
            loc_parts.append(block_match.group(0).title())
        if room_match:
            loc_parts.append(room_match.group(0).title())
        if place_match and not (block_match or room_match):
            loc_parts.append(place_match.group(0).title())

        location = ", ".join(loc_parts) if loc_parts else "Campus Premises"

        target_department = DEPT_ROUTING.get(category, 'General Maintenance')

        return {
            'category': category,
            'priority': priority,
            'target_department': target_department,
            'location_extracted': location,
            'confidence': round(confidence, 2),
            'sla_hours': sla_hours
        }
