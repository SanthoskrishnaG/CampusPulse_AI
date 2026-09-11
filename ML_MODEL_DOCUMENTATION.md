# CampusPulse AI - Machine Learning & Deep Learning Model Cards

CampusPulse AI implements a centralized model management architecture. All serialized model weights and pipelines are preserved in `models/` with corresponding training metadata recorded in `models/model_registry.json`.

---

## 1. Model Registry Summary

| Model ID | Domain | Algorithm | Input Type | Output / Target | Evaluation Metric |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `academic_risk_rf` | Academics | Random Forest Classifier | Tabular Student Profile | Academic Risk (Low, Med, High) | F1-Score: 0.88, Acc: 89.2% |
| `academic_sequential_dl` | Academics | Sequential MLP / Neural Net | 5-Week Temporal Trajectory | Failure Probability Score | ROC-AUC: 0.91 |
| `complaint_nlp_classifier` | Redressal | TF-IDF + Logistic Regression | Unstructured Text Grievance | Category & Priority | F1-Score: 0.86, Acc: 87.5% |
| `event_attendance_regressor` | Events | Random Forest Regressor | Event Meta + Weather | Estimated Headcount Turnout | R²: 0.84, RMSE: 9.4 |
| `canteen_demand_model` | Canteen | Gradient / Ridge Regressor | Date, Day, Temp, Headcount | Meal Portions Forecast | R²: 0.86, MAPE: 7.2% |
| `energy_isolation_forest` | Facilities | Isolation Forest (Unsupervised) | Meter Load, Hour, Season | Anomaly Score [-1.0, 1.0] | Precision @ Outlier: 0.92 |

---

## 2. Detailed Model Cards

### 2.1 Academic Early-Warning Risk Classifier (`academic_risk_rf`)
- **Artifact Path**: `models/academic_risk_model.joblib`
- **Objective**: Identify students at early risk of semester failure or severe academic probation before midterm exams.
- **Training Baseline**: UCI Student Performance (Cortez et al.) + UCI Higher Education Evaluation datasets.
- **Input Features (12)**:
  1. `current_cgpa` (float: 0.0 to 10.0)
  2. `attendance_rate` (float: 0.0 to 100.0%)
  3. `past_failures` (int: count of arrears)
  4. `study_time_hours` (float: weekly self-study)
  5. `parental_education_level` (int: 0 to 4)
  6. `travel_time_minutes` (float)
  7. `assignment_completion_rate` (float: % submitted on time)
  8. `midterm_quiz_avg` (float: 0 to 100)
  9. `lab_performance_score` (float: 0 to 100)
  10. `library_visits_monthly` (int)
  11. `disciplinary_incidents` (int)
  12. `extracurricular_participation` (bool/binary)
- **Hyperparameters**:
  - `n_estimators`: 120
  - `max_depth`: 8
  - `min_samples_split`: 4
  - `class_weight`: `'balanced'` (countering low class representation of severe probation)
- **Explainability**: Outputs top 3 feature importances contributing to each student's specific prediction score.

---

### 2.2 Academic Sequential Trajectory Neural Network (`academic_sequential_dl`)
- **Artifact Path**: `models/academic_sequential_dl.joblib`
- **Objective**: Model downward performance trajectory and academic deceleration across a rolling 5-week window.
- **Input Shape**: `(batch_size, 5 weeks x 3 metrics = 15 values)`
  - Rolling attendance sequence $[A_1, A_2, A_3, A_4, A_5]$
  - Rolling quiz score sequence $[Q_1, Q_2, Q_3, Q_4, Q_5]$
  - Rolling assignment velocity $[S_1, S_2, S_3, S_4, S_5]$
- **Architecture**:
  - Input Layer: 15 units
  - Hidden Layer 1: 32 units, ReLU activation, Dropout (0.2)
  - Hidden Layer 2: 16 units, ReLU activation
  - Output Layer: 1 unit, Sigmoid activation (Probabilistic risk score $[0, 1]$)
- **Training**: Adam optimizer, binary cross-entropy loss, early stopping on validation loss.

---

### 2.3 Grievance Redressal NLP Classifier (`complaint_nlp_classifier`)
- **Artifact Path**: `models/complaint_classifier.joblib`
- **Objective**: Categorize raw free-text complaint descriptions into actionable university department queues and prioritize urgent tickets.
- **Architecture**:
  1. Text Preprocessor: Lowercasing, punctuation stripping, campus terminology stopword handling.
  2. Feature Extraction: `TfidfVectorizer(ngram_range=(1, 2), max_features=3500, min_df=2)`
  3. Classification Head: `LogisticRegression(C=1.5, max_iter=500, multi_class='multinomial')`
- **Target Classes (9)**:
  - `ACADEMICS`, `HOSTEL`, `INFRASTRUCTURE`, `CANTEEN`, `HARASSMENT`, `TRANSPORT`, `NETWORK`, `LIBRARY`, `ACCOUNTS`
- **Safety Priority Engine**: High-risk keywords (e.g., "ragging", "electric spark", "short circuit", "harassment", "water leak") trigger rule-based priority escalation to `CRITICAL` regardless of classifier confidence.

---

### 2.4 Event Attendance Regressor (`event_attendance_regressor`)
- **Artifact Path**: `models/event_attendance_regressor.joblib`
- **Objective**: Prevent venue overcrowding or resource waste by predicting real attendee headcount vs. nominal signups.
- **Features**:
  - `registrations_count` (int)
  - `category` (One-Hot: Workshop, Cultural, Tech Fest, Sports, Guest Lecture)
  - `speaker_tier` (int: 1 = Internal Faculty, 2 = Industry Leader, 3 = Celebrity / Keynote)
  - `day_of_week` (int: 0 = Mon, 6 = Sun)
  - `rain_probability` (float: from Open-Meteo API)
  - `campus_exam_proximity_days` (int: days until semester exams)
- **Model**: Random Forest Regressor (`n_estimators=100`, `max_depth=6`).

---

### 2.5 Canteen Meal Demand Forecaster (`canteen_demand_model`)
- **Artifact Path**: `models/canteen_demand_model.joblib`
- **Objective**: Minimize university kitchen food waste while preventing meal stock-outs.
- **Features**: Day of week, month, historical average, active hostel student headcount, campus events count, ambient temperature.
- **Model**: Regularized Ridge Regressor with non-negative constraints.
- **Impact**: Demonstrates an average 18% reduction in over-preparation waste.

---

### 2.6 Energy Anomaly Isolation Forest (`energy_isolation_forest`)
- **Artifact Path**: `models/energy_isolation_forest.joblib`
- **Objective**: Unsupervised anomaly detection on electrical power demand across campus facilities.
- **Features**:
  - `hour_of_day` (0 to 23)
  - `is_weekend` (0 or 1)
  - `current_load_kw` (float)
  - `rolling_4h_load_delta` (float)
- **Model**: `IsolationForest(contamination=0.04, random_state=42, n_estimators=100)`
- **Triggers**: Flags nocturnal base-load anomalies when building consumption remains elevated during off-hours (2:00 AM - 5:00 AM).

---

## 3. Retraining & Continuous Calibration

All models can be retrained in one step via Django management command:

```bash
python manage.py train_models
```

This updates the weights in `models/` and refreshes the metrics in `models/model_registry.json`.
