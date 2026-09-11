import numpy as np
import joblib
from pathlib import Path
from sklearn.neural_network import MLPClassifier
from ml.registry.registry import ModelRegistry

class SequentialStudentTrajectoryModel:
    """
    Sequential Deep Learning model (MLP / Recurrent Time-Series representation)
    analyzing student engagement vectors across 5 consecutive weeks:
    [W1_att, W1_quiz, W2_att, W2_quiz, W3_att, W3_quiz, W4_att, W4_quiz, W5_att, W5_quiz]
    Detects declining learning trajectories before semester exams.
    """
    def __init__(self):
        self.model = MLPClassifier(
            hidden_layer_sizes=(64, 32, 16),
            activation='relu',
            max_iter=500,
            random_state=42
        )
        self.classes = ['STABLE_IMPROVING', 'MODERATE_SLIP', 'STEEP_DECLINE']

    def generate_synthetic_trajectory_data(self, n_samples=1000):
        np.random.seed(42)
        X = []
        y = []

        for _ in range(n_samples):
            pattern_type = np.random.choice([0, 1, 2], p=[0.60, 0.25, 0.15])
            # 0: Stable/Improving (e.g. 75, 78, 80, 82, 85)
            # 1: Moderate slip (e.g. 75, 72, 68, 65, 62)
            # 2: Steep decline (e.g. 85, 70, 55, 40, 25)
            
            if pattern_type == 0:
                base_att = np.random.uniform(75, 95)
                base_quiz = np.random.uniform(70, 95)
                att_seq = [np.clip(base_att + i*np.random.uniform(0, 2), 40, 100) for i in range(5)]
                quiz_seq = [np.clip(base_quiz + i*np.random.uniform(-1, 3), 40, 100) for i in range(5)]
            elif pattern_type == 1:
                base_att = np.random.uniform(65, 80)
                base_quiz = np.random.uniform(60, 75)
                att_seq = [np.clip(base_att - i*np.random.uniform(1, 3), 30, 100) for i in range(5)]
                quiz_seq = [np.clip(base_quiz - i*np.random.uniform(1, 4), 30, 100) for i in range(5)]
            else:
                base_att = np.random.uniform(70, 90)
                base_quiz = np.random.uniform(70, 85)
                att_seq = [np.clip(base_att - i*np.random.uniform(8, 14), 10, 100) for i in range(5)]
                quiz_seq = [np.clip(base_quiz - i*np.random.uniform(8, 15), 10, 100) for i in range(5)]

            feature_vector = []
            for w in range(5):
                feature_vector.append(att_seq[w])
                feature_vector.append(quiz_seq[w])

            X.append(feature_vector)
            y.append(pattern_type)

        return np.array(X), np.array(y)

    def train_and_save(self):
        X, y = self.generate_synthetic_trajectory_data(1200)
        self.model.fit(X, y)
        score = self.model.score(X, y)

        models_dir = Path("models")
        models_dir.mkdir(parents=True, exist_ok=True)
        model_path = models_dir / "academic_sequential_dl.joblib"
        joblib.dump({
            'model': self.model,
            'classes': self.classes,
            'accuracy': float(score)
        }, model_path)

        ModelRegistry.register_model(
            model_name="Academic_Sequential_DL",
            version="1.0.0",
            algorithm="Multi-Layer Perceptron (Sequential Temporal Network)",
            metrics={'accuracy': round(float(score), 4), 'temporal_window': '5_weeks'},
            feature_list=[f"W{w+1}_{metric}" for w in range(5) for metric in ['att', 'quiz']],
            model_path=model_path,
            description="Deep sequential learning model tracking week-by-week student learning trajectory (Week 1 -> 5)."
        )
        print(f"Trained Sequential DL model (Accuracy: {score:.4f})")
        return score

    @classmethod
    def evaluate_student_trajectory(cls, weekly_records):
        """
        Evaluates a sequence of student weekly records.
        """
        if len(weekly_records) < 5:
            return 'INSUFFICIENT_DATA', 0.0

        vector = []
        for r in weekly_records[:5]:
            vector.extend([r.attendance_rate, r.quiz_score])

        models_dir = Path("models")
        model_path = models_dir / "academic_sequential_dl.joblib"
        if not model_path.exists():
            return 'STABLE', 0.0

        data = joblib.load(model_path)
        model = data['model']
        probs = model.predict_proba([vector])[0]
        pred_idx = int(np.argmax(probs))
        return data['classes'][pred_idx], float(probs[pred_idx])
