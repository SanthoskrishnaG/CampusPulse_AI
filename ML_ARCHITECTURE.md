# CampusPulse AI — Machine Learning Architecture & Governance Specification

## 1. Architectural Overview
CampusPulse AI implements an end-to-end, production-grade Machine Learning and Natural Language Processing architecture tailored for the **Coimbatore Institute of Technology (CIT)** smart campus ecosystem.

The system enforces a **Zero Fabrication Policy**: predictions originate exclusively from serialized, cross-validated mathematical models or clearly report unavailability.

```
+-----------------------------------------------------------------------------------+
|                           CAMPUSPULSE AI ML PLATFORM                              |
+-----------------------------------------------------------------------------------+
                                         |
               +-------------------------+-------------------------+
               |                                                   |
   [DATA INGESTION & AUDIT]                                [DATA MODES]
   - Institutional Student Records                         - LIVE: Real-time Telemetry
   - Dining Pos & Kitchen Scale Records                    - DEMO: Calibrated Benchmarks
   - Bus GPS & Waybill Telemetry                                   |
   - Smart Parking Bay Counters                                    |
   - Energy Smart Meters (kWh)                                     |
               |                                                   |
               +-------------------------+-------------------------+
                                         |
                                         v
                         [STRICT DATA VALIDATION UTILITIES]
                         - Schema & Bound Checking (ml/utils/validation.py)
                         - Target & Temporal Leakage Prevention
                                         |
                                         v
                         [FEATURE ENGINEERING PIPELINES]
                         - StandardScaler / Robust Normalization
                         - Weekly Trajectory Trend Calculations
                         - TF-IDF Character & Word N-Grams
                                         |
                                         v
                        [MODEL TRAINING & REGISTRATION]
                        - Reproducible Splits (75% Train / 25% Test)
                        - Metric Scoring: F1, Accuracy, MAE, RMSE, R²
                        - Model Serialization to /models/*.joblib
                        - Central Registry (models/model_registry.json)
                        - DB Observability (apps.analytics.models)
                                         |
                                         v
                         [REAL-TIME INFERENCE ENGINES]
                         - Sub-100ms In-House CPU Execution
                         - Calibrated Class Probabilities
                         - Explainable Factor Decompositions
                                         |
                                         v
                         [PERSISTENCE & AUDIT LOGGING]
                         - MLPredictionLog (Latency, Inputs, Confidence)
                         - MLTrainingRun (Duration, Dataset Size, Scores)
                                         |
                                         v
                         [SECURE REST INTERFACES (/api/ml/*)]
                         - RBAC & Student Privacy Enforcement
                         - Standardized JSON Envelope Format
                                         |
                                         v
                  +----------------------+----------------------+
                  |                                             |
                  v                                             v
        [INTELLIGENT DASHBOARDS]                      [GROUND TRUTH FEEDBACK]
        - Model Governance Monitor                    - Actual Exam Grades Logged
        - Telemetry Latency Gauges                    - Real Meals Sold Entered
        - PSI Distribution Drift Alerts               - Kitchen Scrap Weighed
                  |                                             |
                  +----------------------+----------------------+
                                         |
                                         v
                             [GOVERNED RETRAINING]
                             - Management Commands (train_all_models)
                             - PSI Threshold Trigger (PSI >= 0.25)
                             - Version Incrementing (v1.0 -> v1.1)
```

---

## 2. Production Model Fleet & Scorecard

| Model Identifier | Task Domain | Algorithm | Serialized Artifact | Test Metric Scorecard | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Academic_Risk_Classifier** | Classification | LogisticRegression | `models/academic_risk_model.joblib` | Weighted F1: `0.9799`, ROC-AUC: `0.9987`, Acc: `98.0%` | **Production** |
| **Academic_Sequential_DL** | Trajectory NN | Multi-Layer Perceptron | `models/academic_sequential_dl.joblib` | Sequence Accuracy: `1.0000` across 5-week window | **Production** |
| **Canteen_Food_Demand_Forecaster** | Time-Series Regr. | RandomForestRegressor | `models/canteen_demand_model.joblib` | R²: `0.9853`, MAE: `10.18` meals, RMSE: `12.72` | **Production** |
| **Food_Waste_Forecaster** | Regression | GradientBoostingRegressor | `models/food_waste_model.joblib` | R²: `0.8168`, MAE: `1.79` kg, RMSE: `2.33` kg | **Production** |
| **Campus_Complaint_Classifier** | NLP Text Triage | TF-IDF + Logistic Regression | `models/complaint_classifier.joblib` | Accuracy: `1.0000`, Weighted F1: `1.0000` | **Production** |
| **Duplicate_Complaint_TFIDF_Detector** | NLP Similarity | TF-IDF Cosine Vectorizer | Dynamic Pipeline | Threshold: Cosine $\ge 0.68$ + Category synergy | **Production** |
| **Energy_Anomaly_Detector** | Anomaly Detection | IsolationForest | `models/energy_isolation_forest.joblib` | Contamination: `0.06`, Trained on 1,000 samples | **Production** |
| **Smart_Transport_ETA_Predictor** | Fleet Regression | RandomForestRegressor | `models/transport_eta_model.joblib` | R²: `0.9729`, MAE: `2.43` mins, RMSE: `3.02` mins | **Production** |
| **Smart_Parking_Occupancy_Forecaster** | Zone Regression | RandomForestRegressor | `models/parking_occupancy_model.joblib` | R²: `0.9738`, MAE: `3.47` slots, RMSE: `4.53` slots | **Production** |

---

## 3. Real-Time REST Interface Specification (`/api/ml/*`)

All inference endpoints authenticate users, enforce RBAC, sanitize inputs, execute sub-100ms inference, record execution metadata to `MLPredictionLog`, and return a standardized JSON response envelope:

```json
{
  "success": true,
  "model": "Academic_Risk_Classifier",
  "model_version": "1.0.0",
  "prediction": "LOW",
  "confidence": 0.982,
  "factors": [
    "Consistent attendance and coursework marks within healthy departmental percentiles."
  ],
  "latency_ms": 4.12,
  "data_mode": "LIVE",
  "timestamp": "2026-09-20T21:00:00Z"
}
```

### Endpoints
1. `POST /api/ml/academic-risk/predict/`: Student academic early-warning risk scoring with role-gated privacy.
2. `GET /api/ml/canteen/demand/`: Campus-wide dining hall meal demand forecasting.
3. `POST /api/ml/canteen/waste/predict/`: Kitchen organic food waste forecast based on prep buffer.
4. `GET /api/ml/hostel/mess/demand/`: Gated mess attendance forecasting for BH-1, BH-2, GH-1, GH-2.
5. `POST /api/ml/complaints/classify/`: Multi-class NLP grievance routing and SLA assignment.
6. `POST /api/ml/complaints/check-duplicate/`: Text cosine similarity against active unresolved tickets.
7. `POST /api/ml/energy/detect/`: Real-time power load anomaly detection with fault typing.
8. `GET /api/ml/transport/eta/<bus_id>/`: CIT bus corridor travel time and peak-hour delay predictor.
9. `GET /api/ml/parking/predict/<lot_code>/`: Hourly bay occupancy and congestion forecaster.
10. `POST /api/ml/feedback/submit/`: Ground truth outcome submission closing the retraining loop.
11. `GET /api/ml/monitoring/metrics/`: Live inference volume, latency, and fleet health telemetry.

---

## 4. Retraining & Continuous Calibration

Models can be retrained on-demand or through scheduled administration tasks via Django management commands:

```bash
# Train individual components
python manage.py train_academic_risk
python manage.py train_canteen_demand
python manage.py train_food_waste
python manage.py train_complaints_nlp
python manage.py train_energy_anomaly
python manage.py train_transport_eta
python manage.py train_parking_model

# Train entire production fleet sequentially
python manage.py train_all_models

# Run Population Stability Index (PSI) drift monitoring
python manage.py detect_data_drift
```
