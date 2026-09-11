import json
import joblib
from pathlib import Path
from .features import extract_student_features, FEATURE_NAMES
from .sequential_model import SequentialStudentTrajectoryModel

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
        Runs ML prediction + Sequential DL trend analysis on a Student object.
        Returns: risk_level, risk_score, confidence, factors, recommendation
        """
        model_data = cls.get_model()
        features = extract_student_features(student)

        if model_data:
            pipeline = model_data['pipeline']
            probs = pipeline.predict_proba([features])[0]
            pred_idx = int(pipeline.predict([features])[0])
            risk_level = model_data['classes'][pred_idx]
            confidence = float(probs[pred_idx])
            # Calibrated probability percentage of being at risk (Medium or High)
            risk_score = float((probs[1] * 50 + probs[2] * 100))
        else:
            # Fallback heuristic if models not trained yet
            if student.attendance_percentage < 70 or student.cgpa < 5.5:
                risk_level = 'HIGH'
                risk_score = 84.0
            elif student.attendance_percentage < 80 or student.cgpa < 6.8:
                risk_level = 'MEDIUM'
                risk_score = 52.0
            else:
                risk_level = 'LOW'
                risk_score = 14.0
            confidence = 0.85

        # Check Sequential DL trend
        weekly_records = list(student.weekly_records.order_by('week_number'))
        trajectory_label, traj_conf = SequentialStudentTrajectoryModel.evaluate_student_trajectory(weekly_records)

        # Generate human-explainable factors
        factors = []
        if student.attendance_percentage < 75.0:
            factors.append(f"Attendance ({student.attendance_percentage:.1f}%) is below the mandatory 75% institutional threshold.")
        elif student.attendance_percentage < 82.0:
            factors.append(f"Attendance ({student.attendance_percentage:.1f}%) is on a borderline trajectory.")

        if student.cgpa < 6.0:
            factors.append(f"Cumulative GPA ({student.cgpa:.2f}) indicates academic stress across prior semesters.")

        if student.backlog_count > 0:
            factors.append(f"Active backlog count: {student.backlog_count} subject(s) pending clearance.")

        if trajectory_label == 'STEEP_DECLINE':
            factors.append("Sequential Deep Learning: Steep multi-week decline in weekly quiz and attendance engagement detected.")
            if risk_level == 'LOW':
                risk_level = 'MEDIUM'
                risk_score = max(risk_score, 48.0)
        elif trajectory_label == 'MODERATE_SLIP':
            factors.append("Sequential Deep Learning: Gradual slip in weekly quiz performance across weeks 1 to 5.")

        if not factors:
            factors.append("Consistent attendance and coursework marks within healthy departmental percentiles.")

        # Recommended action based on risk level
        if risk_level == 'HIGH':
            rec = "Immediate faculty 1-on-1 mentoring session, remedial classes for core subjects, and assignment support extension."
        elif risk_level == 'MEDIUM':
            rec = "Encourage attendance recovery, participation in peer study groups, and review quiz problem sets."
        else:
            rec = "Standard academic progression. Student is eligible for advanced honours projects and club leadership."

        return {
            'risk_level': risk_level,
            'risk_score': round(risk_score, 1),
            'confidence': round(confidence, 3),
            'factors': factors,
            'recommendation': rec,
            'model_name': 'RandomForest-Ensemble-v1' if model_data else 'RuleEngine-Fallback'
        }

    @classmethod
    def batch_assess_all_students(cls):
        """
        Assesses all active students and persists results to AcademicRiskAssessment.
        """
        from apps.students.models import Student
        from apps.academics.models import AcademicRiskAssessment

        students = Student.objects.filter(is_active=True).prefetch_related('enrollments', 'weekly_records')
        count = 0
        for s in students:
            result = cls.predict_student_risk(s)
            AcademicRiskAssessment.objects.create(
                student=s,
                risk_level=result['risk_level'],
                risk_score=result['risk_score'],
                confidence=result['confidence'],
                model_name=result['model_name'],
                contributing_factors_json=json.dumps(result['factors']),
                recommended_action=result['recommendation']
            )
            count += 1
        return count
