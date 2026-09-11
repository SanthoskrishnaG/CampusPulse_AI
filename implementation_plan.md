# Implementation Plan: CampusPulse AI

**CampusPulse AI** is a production-grade, AI-powered real-time intelligent campus operating, management, and student experience platform designed as a single, unified college operating system. Rather than ten disconnected ML mini-projects, CampusPulse AI integrates all domains into **one unified architecture** sharing one authentication system, one role-based permission system (RBAC with 12 distinct roles), one database layer (MySQL with automatic SQLite fallback), one machine learning & deep learning service pipeline, one notification engine, one simulation engine, and one responsive web command center.

---

## User Review Required

> [!IMPORTANT]
> **Database Engine & Offline Portability**: 
> The project is designed with a dual-mode database engine. When MySQL 8.x is configured in `.env` (service `MySQL80` is running on your machine), it connects via PyMySQL. If MySQL credentials are not yet configured or if running in a zero-setup presentation environment, it automatically falls back to an SQLite database (`campuspulse.sqlite3`) so the entire system, test suite, and ML pipelines run immediately without blocking.
>
> **CPU-Safe Deep Learning & Computer Vision**:
> All ML/DL models (Academic Risk sequential neural net / LSTM, Complaint NLP classifier, Food & Transport regressors, Energy Isolation Forest, Vehicle Detector, and Waste Image CNN) are engineered for CPU execution and laptop demonstrations, preventing GPU memory crashes while retaining full training scripts and model registries.

---

## Architecture Overview

```
                                  CAMPUSPULSE AI PLATFORM
+--------------------------------------------------------------------------------------------------+
|                                    Presentation & UX Layer                                       |
|  - Modern Dark-Theme Command Center (Glassmorphism, CSS Tokens, Micro-animations)                |
|  - 12 Role-Specific Dashboards (Student, Faculty, HOD, Club, Transport, Canteen, Facility, Admin) |
|  - Interactive Leaflet AI Campus Map (Custom DB-Stored Building Coordinates)                     |
|  - Real-Time Telemetry & Chart.js Visualizations                                                 |
+--------------------------------------------------------------------------------------------------+
|                                     Core Services Layer                                          |
|  - Unified Auth & RBAC (12 Roles, Session Security, Audit Logging)                              |
|  - In-App Notification Center & Real-Time Telemetry / WebSocket Polling                          |
|  - Permission-Aware AI Campus Assistant (Structured natural language query engine)              |
|  - Multi-Speed Simulation Engine (1x, 2x, 5x, 10x for Buses, Parking, Energy, Canteen)          |
|  - CSV Importer with Validation, Preview, Anonymized ID support, and Sample Templates           |
|  - Open-Meteo Weather Service with local caching and offline fallback                           |
+--------------------------------------------------------------------------------------------------+
|                                     ML / DL Intelligence Core                                    |
|  1. Academic Risk ML (Random Forest / GBM + SHAP Feature Importance & Interventions)             |
|  2. Academic Temporal DL (Sequential Week-over-Week Learning Trajectory Model)                   |
|  3. Event Attendance Regressor (Capacity, category & interest forecasting)                       |
|  4. Club & Event Semantic Recommender (TF-IDF & profile compatibility)                          |
|  5. Project & Complementary Team Formation Recommender                                           |
|  6. Complaint AI (NLP Category, Priority & Department auto-routing + SLA)                        |
|  7. Smart Transport (Route ETA & delay prediction + simulated GPS telemetry)                     |
|  8. Traffic & Vehicle Detection (OpenCV / MobileNet CPU-safe detection pipeline)                 |
|  9. Smart Parking (Occupancy forecasting & live slot allocation)                                 |
| 10. Canteen Food Demand & Leftover Waste Reduction Predictor                                     |
| 11. Energy Consumption Anomaly Detector (Isolation Forest spike detection)                      |
| 12. Waste Segregation (TrashNet 6-class CNN image classification)                                |
| 13. Model Registry & Health Monitoring (Version, F1, ROC-AUC, Drift metrics)                     |
+--------------------------------------------------------------------------------------------------+
|                                     Data & Persistence Layer                                     |
|  - Unified Normalized Schema: User, Student, Faculty, Department, Course, Attendance, Marks,    |
|    Event, Club, Complaint, Bus, Parking, Canteen, Energy, Waste, AIModel, Notification, AuditLog |
|  - Dual Database Backend: MySQL 8.x + SQLite zero-friction development fallback                  |
+--------------------------------------------------------------------------------------------------+
```

---

## Proposed Changes

### 1. Project Scaffolding & Configuration
- **`config/`**:
  - `settings.py`: Environment-driven configuration (`python-dotenv`), MySQL/SQLite dual backend switch, static & media configurations, DRF setup, custom user model integration.
  - `urls.py`: Unified URL router mounting all web UI routes, authentication routes, and REST APIs under `/api/`.
  - `wsgi.py` / `asgi.py`.
- **Root Files**:
  - `.env.example`: Config template for `SECRET_KEY`, `DEBUG`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `WEATHER_API_BASE_URL`.
  - `.env`: Default configured with local fallback.
  - `requirements.txt`: Python package requirements.
  - `.gitignore`: Ignoring virtualenv, `__pycache__`, media caches, credentials.

### 2. Core Apps Architecture
- **`apps/accounts/`**:
  - Custom `User` model inheriting from `AbstractUser` with `role` choices (12 RBAC roles: `SUPER_ADMIN`, `COLLEGE_ADMIN`, `DEPARTMENT_ADMIN`, `FACULTY`, `STUDENT`, `CLUB_ADMIN`, `CLUB_MEMBER`, `TRANSPORT_MANAGER`, `MAINTENANCE_STAFF`, `CANTEEN_MANAGER`, `SECURITY_STAFF`, `FACILITY_MANAGER`).
  - Role-based redirect views, permission decorators (`@role_required`), audit logging signals.
- **`apps/students/`**:
  - `Student` model: anonymized student ID, department, semester, section, CGPA, attendance, skills, interests, career goals, project history, achievements.
  - Student profile views, CSV import tool for batch student data with preview & verification.
- **`apps/academics/`**:
  - `Course`, `Enrollment`, `AttendanceRecord`, `Assessment`, `AcademicRiskAssessment`, `AcademicIntervention`.
  - Academic analytics, week-by-week performance tracking, faculty intervention assignment.
- **`apps/departments/`**:
  - `Department`, `Section`, `Announcement`, `DepartmentResource`.
  - HOD / Department Admin dashboard: student distribution, risk breakdown, faculty workload, department complaints.
- **`apps/faculty/`**:
  - `Faculty` model: department, designation, courses handled, mentoring assignments.
  - Faculty dashboard: course attendance, at-risk student list, intervention management.
- **`apps/clubs/`**:
  - `Club`, `ClubMembership`, `ClubAchievement`, `ClubAnnouncement`.
  - Club discovery, joining requests, member management.
- **`apps/events/`**:
  - `Event`, `EventRegistration`, `EventAttendance` (with QR-code check-in support), `EventFeedback`, `Certificate`.
  - Event calendar, registration workflow, attendance prediction integration.
- **`apps/complaints/`**:
  - `Complaint`, `ComplaintCategory`, `ComplaintStatusHistory`, `ComplaintAssignment`.
  - Natural language complaint submission, AI triage (category, priority, target department), SLA tracking, resolution workflow, heatmap data.
- **`apps/transport/`**:
  - `Bus`, `BusRoute`, `BusStop`, `GPSRecord`, `TransportPrediction`.
  - Live GPS simulation (controllable 1x/2x/5x/10x), ETA calculation, passenger occupancy.
- **`apps/traffic/`**:
  - `TrafficObservation`, `VehicleDetectionRecord`.
  - Video/image upload processing, vehicle count breakdown (car, motorcycle, bus, truck), congestion index.
- **`apps/parking/`**:
  - `ParkingLot`, `ParkingSlot`, `ParkingObservation`, `ParkingPrediction`.
  - Slot visualizer (vacant vs occupied), peak hours predictor, lot recommendations.
- **`apps/canteen/`**:
  - `Canteen`, `MenuItem`, `MealRecord`, `FoodDemandPrediction`, `FoodWasteRecord`.
  - Meal demand forecasting (breakfast, lunch, dinner, snacks), leftover tracking, chef preparation guidance.
- **`apps/energy/`**:
  - `EnergyMeter`, `EnergyReading`, `EnergyAnomaly`.
  - Real-time kWh telemetry, baseline comparison, spike/night-leak anomaly detection.
- **`apps/waste/`**:
  - `WasteRecord`, `WastePrediction`, `WasteImagePrediction`.
  - TrashNet 6-class image upload classifier, disposal guidance, campus waste volume forecast.
- **`apps/projects/`**:
  - `Project`, `ProjectSkill`, `Team`, `TeamMember`, `TeamRecommendation`.
  - Project requirement posting, complementary skill-matching algorithm for student teams.
- **`apps/recommendations/`**:
  - Recommendation engine coordinating recommendations across clubs, events, projects, and peers.
- **`apps/ai_assistant/`**:
  - Natural language campus query assistant with permission-aware DB access (e.g. at-risk queries restricted to faculty/admin).
- **`apps/notifications/`**:
  - In-app notification center for academic alerts, transport delays, event reminders, complaint updates.
- **`apps/analytics/`**:
  - Campus Command Center with unified analytics, KPIs, Chart.js visualizations, and model health dashboard.
- **`apps/common/`**:
  - Base models, audit logging, Open-Meteo weather client, simulation controller.

### 3. Machine Learning & Deep Learning Core (`ml/`)
Every module contains `preprocessing.py`, `train.py`, `predict.py`, `evaluate.py`, and `model_registry.py`:
- **`ml/academic/`**:
  - **Traditional ML**: Logistic Regression, Random Forest, Gradient Boosting for academic risk (LOW, MEDIUM, HIGH) evaluated on Accuracy, Precision, Recall, F1, ROC-AUC.
  - **Explainability**: Top feature importance indicators (attendance percentage, internal marks decline, missing assignments).
  - **Sequential DL**: Temporal LSTM / GRU network tracking student learning performance across 5 consecutive weeks to catch negative trajectories early.
- **`ml/events/`**:
  - Random Forest Regressor predicting expected event turnout and no-show rate based on category, capacity, and day/time.
- **`ml/recommendations/`**:
  - Content-based TF-IDF and profile cosine similarity matching student skills and interests to events and clubs.
  - Complementary team formation algorithm (matching frontend, backend, ML, database, domain skills).
- **`ml/complaints/`**:
  - NLP classifier (TF-IDF + Linear Classifier / SVM) predicting Category, Priority, and Department routing from natural language complaint text.
- **`ml/transport/`**:
  - ETA and delay regression model conditioned on route, stop distance, passenger load, and weather.
- **`ml/traffic/`**:
  - CPU-safe computer vision pipeline detecting vehicles (cars, buses, motorcycles, trucks) from images/video frames.
- **`ml/parking/`**:
  - Parking demand time-series forecaster predicting occupancy percentage and peak overflow times.
- **`ml/canteen/`**:
  - Meal demand regression model predicting required breakfast/lunch/dinner portions to minimize food waste.
- **`ml/energy/`**:
  - Isolation Forest anomaly detector flagging unexpected consumption spikes and nighttime power leakage.
- **`ml/waste/`**:
  - 6-class waste image classifier (Cardboard, Glass, Metal, Paper, Plastic, Trash) using lightweight CNN architecture with CPU inference.
- **`ml/registry/`**:
  - Model registry tracking active models, versions, evaluation metrics, and training timestamps.

### 4. Data Layer & Seed System (`data_generation/` & `scripts/`)
- **`python manage.py seed_demo_data`**:
  - Creates 7 academic departments (CSE, IT, ECE, EEE, MECH, CIVIL, AIDS).
  - Creates 12 demo users with known credentials for all RBAC roles (`admin123`).
  - Creates 500+ realistic student profiles with correlated attendance, CGPA, marks, and skill vectors.
  - Creates 50+ faculty profiles, 20+ clubs, 100+ events, 500+ complaints with realistic text.
  - Creates 10 campus buses with realistic stop coordinates, 3 parking lots with 200+ slots.
  - Populates historical canteen meal records, energy meter time series, and campus locations.
- **`python manage.py train_models`**:
  - Trains and persists all baseline ML and DL models with evaluation metrics saved into the Model Registry.
- **`data/`**:
  - Structured directories (`raw/`, `processed/`, `synthetic/`) and CSV import templates for students, marks, attendance, complaints, energy, canteen.

### 5. UI/UX Design System (`templates/` & `static/`)
- **Design Language**:
  - Modern college command center aesthetic: sleek dark theme with glassmorphism card accents, vibrant accent colors (Cyan `#00f2fe`, Violet `#4facfe`, Emerald `#10b981`, Amber `#f59e0b`, Rose `#ef4444`).
  - Google Fonts: *Inter* / *Outfit*.
  - Rich interactive components: responsive sidebar, top KPI ribbons, Chart.js telemetry charts, Leaflet interactive campus map with custom markers for buildings, bus stops, and parking lots.
  - Dedicated dashboards tailored to all 12 roles.
  - Interactive simulation control panel (Start, Pause, Reset, 1x/2x/5x/10x speed).

### 6. Documentation Suite
- `README.md`: Quick start guide, Windows setup, MySQL & SQLite configuration, CLI commands.
- `ARCHITECTURE.md`: High-level system architecture and data flow diagrams.
- `DATASET_SOURCES.md`: Full attribution and licensing for UCI datasets, TrashNet, Open-Meteo, OpenStreetMap.
- `API_DOCUMENTATION.md`: REST API specifications with request/response payloads.
- `ML_MODEL_DOCUMENTATION.md`: Model cards for all 10 ML/DL models with feature inputs, algorithms, evaluation metrics, and explainability.
- `DATABASE_SCHEMA.md`: Normalized schema documentation and ER diagram.
- `PRIVACY.md`: Data protection, anonymization, and ethical AI guidelines.
- `docs/project_demo_script.md`: Turnkey 15-minute viva/presentation demonstration guide.
- `docs/final_year_project_report_skeleton.md`: Complete 27-chapter final-year academic report framework.

---

## Verification Plan

### Automated Tests
1. **Model & Database Sanity Tests**:
   - `python manage.py test` covering authentication, RBAC authorization decorators, model creation, and data validation.
2. **ML Pipeline Tests**:
   - Automated inference tests ensuring all models load, predict valid classes/values, and return explainability factors without errors.
3. **API Endpoint Tests**:
   - DRF endpoint testing for students, events, complaints, predictions, and recommendations.

### Manual & Demonstration Verification
1. **Role Login & Navigation**:
   - Verify student login -> academic risk status -> club recommendation -> complaint submission.
   - Verify admin login -> complaint triage dashboard -> model registry -> campus command center.
2. **Simulation Control**:
   - Verify live bus movement and parking occupancy updating on the campus map at 1x, 2x, and 5x speed.
3. **AI Assistant**:
   - Querying campus stats (e.g. "How many high-risk students in CSE?", "What events are happening this week?") and confirming permission enforcement.
4. **CSV Import**:
   - Uploading student CSV template and verifying validation, preview, and database persistence.
