import time
import json
import joblib
from pathlib import Path
from django.utils import timezone
from django.conf import settings
from .features import extract_student_features, FEATURE_NAMES
from .sequential_model import SequentialStudentTrajectoryModel
from ml.utils.validation import validate_academic_features

MODEL_PATH = Path("models") / "academic_risk_model.joblib"

class AcademicRiskPredictor:
    _cached_model = None

    @classmethod
    def get_model(cls):
        if cls._cached_model is None and MODEL_PATH.exists():
            cls._cached_model = joblib.load(MODEL_PATH)
        return cls._cached_model

    @classmethod
    def predict_student_risk(cls, student):
        """
        Runs verified ML prediction + Sequential DL trajectory analysis on a Student object.
        Persists inference to MLPredictionLog and updates AcademicRiskAssessment.
        """
        start_time = time.time()
        model_data = cls.get_model()

        if not model_data:
            return {
                'success': False,
                'risk_level': None,
                'risk_score': None,
                'confidence': None,
                'factors': [],
                'recommended_action': "Prediction unavailable — model requires training.",
                'model_name': "Academic_Risk_Classifier",
                'model_version': "1.0.0"
            }

        raw_features = extract_student_features(student)
        features_dict = dict(zip(FEATURE_NAMES, raw_features))
        validated = validate_academic_features(features_dict)

        pipeline = model_data['pipeline']
        feature_vector = [validated[name] for name in FEATURE_NAMES]
        probs = pipeline.predict_proba([feature_vector])[0]
        pred_idx = int(pipeline.predict([feature_vector])[0])

        risk_level = model_data['classes'][pred_idx]
        confidence = float(round(float(probs[pred_idx]), 3))
        # Mathematical risk index based on class probabilities
        risk_score = float(round(float(probs[1] * 50.0 + probs[2] * 100.0), 1))

        # Evaluate Sequential DL trajectory across weekly records
        weekly_records = list(student.weekly_records.order_by('week_number'))
        trajectory_label, traj_conf = SequentialStudentTrajectoryModel.evaluate_student_trajectory(weekly_records)

        # Build genuine explainable factor drivers
        factors = []
        if validated['attendance_percentage'] < 75.0:
            factors.append(f"Attendance ({validated['attendance_percentage']:.1f}%) is below mandatory 75% institutional threshold.")
        elif validated['attendance_percentage'] < 80.0:
            factors.append(f"Attendance ({validated['attendance_percentage']:.1f}%) is borderline.")

        if validated['cgpa'] < 6.0:
            factors.append(f"Cumulative GPA ({validated['cgpa']:.2f}) indicates historical academic distress.")

        if validated['backlog_count'] > 0:
            factors.append(f"Active backlog count: {validated['backlog_count']} course(s) pending clearance.")

        if validated['internal_marks'] < 50.0:
            factors.append(f"Current internal test average ({validated['internal_marks']:.1f}%) is in bottom quartile.")

        if trajectory_label == 'STEEP_DECLINE':
            factors.append("Multi-week sequential decline observed in continuous quiz and LMS engagement.")
            if risk_level == 'LOW':
                risk_level = 'MEDIUM'
                risk_score = max(risk_score, 45.0)

        if not factors:
            factors.append("Consistent attendance and coursework marks within healthy departmental percentiles.")

        if risk_level == 'HIGH':
            rec = "Model indicates elevated academic risk. Recommended intervention: Faculty 1-on-1 mentoring and remedial laboratory clinic."
        elif risk_level == 'MEDIUM':
            rec = "Model indicates moderate risk. Recommended intervention: Assignment support extension and peer study group enrollment."
        else:
            rec = "Regular coursework progression. Academic indicators remain healthy."

        latency_ms = round((time.time() - start_time) * 1000.0, 2)
        data_mode = getattr(settings, 'DATA_MODE', 'DEMO')

        # Persist to MLPredictionLog
        try:
            from apps.analytics.models import MLPredictionLog
            MLPredictionLog.objects.create(
                model_name="Academic_Risk_Classifier",
                model_version=model_data.get('version', '1.0.0'),
                task="CLASSIFICATION",
                input_summary=json.dumps({
                    'student_id': student.student_id,
                    'attendance': validated['attendance_percentage'],
                    'cgpa': validated['cgpa'],
                    'internal_marks': validated['internal_marks']
                }),
                prediction=risk_level,
                confidence=confidence,
                factors_json=json.dumps(factors),
                latency_ms=latency_ms,
                status=MLPredictionLog.Status.SUCCESS,
                data_mode=data_mode,
                user=student.user if student else None
            )
        except Exception:
            pass

        # Update or create AcademicRiskAssessment record for student
        try:
            from apps.academics.models import AcademicRiskAssessment
            AcademicRiskAssessment.objects.create(
                student=student,
                risk_level=risk_level,
                risk_score=risk_score,
                confidence=confidence,
                model_name=f"AcademicRiskClassifier-{model_data.get('version', '1.0.0')}",
                contributing_factors_json=json.dumps(factors),
                recommended_action=rec
            )
        except Exception:
            pass

        return {
            'success': True,
            'risk_level': risk_level,
            'risk_score': risk_score,
            'confidence': confidence,
            'factors': factors,
            'recommended_action': rec,
            'latency_ms': latency_ms,
            'model_name': "Academic_Risk_Classifier",
            'model_version': model_data.get('version', '1.0.0')
        }
