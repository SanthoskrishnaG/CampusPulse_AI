# CampusPulse AI - System Architecture & Engineering Design

CampusPulse AI is designed as a unified, enterprise-grade Autonomous Campus Operating System (ACOS). Instead of fragmented ML scripts or isolated department tools, CampusPulse AI integrates 14 core university domains into a cohesive event-driven architecture powered by traditional Machine Learning, Deep Learning, computer vision heuristics, real-time spatial telemetry, and role-based access control.

---

## 1. High-Level Architecture Diagram

```
+--------------------------------------------------------------------------------------------------+
|                                    PRESENTATION LAYER                                            |
|  - Vanilla HTML5 / Modern Glassmorphism CSS3 / Vanilla ES6+ JS                                  |
|  - Dynamic Canvas Chart.js Visualizations                                                        |
|  - Leaflet.js Interactive Spatial Campus Map (Dynamic GPS telemetry & bay occupancy)           |
|  - Role-Aware Dynamic Navigation (Student, Faculty, HOD, Dean, Transport, Energy, Admin, etc.)   |
+--------------------------------------------------------------------------------------------------+
                                                |
                                      HTTP / REST API / JSON
                                                |
+--------------------------------------------------------------------------------------------------+
|                                     APPLICATION LAYER                                            |
|                                     (Django 6.1.1 + DRF)                                         |
|                                                                                                  |
|  [Security & Middleware]                                                                         |
|   - Custom User Model (12 RBAC Roles + Department Isolation)                                     |
|   - `@role_required` Decorator & Fine-Grained Object-Level Permissions                           |
|   - Centralized Audit Logging (`AuditLog`) & Action Traceability                                 |
|                                                                                                  |
|  [Core Domain Services]                                                                          |
|   - apps.accounts        - apps.students         - apps.academics        - apps.faculty          |
|   - apps.departments     - apps.clubs            - apps.events           - apps.projects         |
|   - apps.recommendations - apps.complaints       - apps.transport        - apps.traffic          |
|   - apps.parking         - apps.canteen          - apps.energy           - apps.waste            |
|   - apps.ai_assistant    - apps.notifications    - apps.analytics (Command Center)               |
+--------------------------------------------------------------------------------------------------+
                                                |
                      +-------------------------+-------------------------+
                      |                                                   |
+------------------------------------------+    +--------------------------------------------------+
|          ML & INFERENCE CORE             |    |               PERSISTENCE LAYER                  |
|                                          |    |                                                  |
|  [Trained Production Artifacts]          |    |  [Dual Database Engine]                          |
|   - Academic Risk RF Classifier          |    |   - Primary: MySQL 8.x (InnoDB, UTF8mb4)         |
|   - Academic Temporal Sequential MLP     |    |   - Fallback: SQLite (`campuspulse.sqlite3`)      |
|   - Complaint NLP (TF-IDF + LogReg)      |    |   - Automatic connection failover handler        |
|   - Event Attendance Regressor           |    |                                                  |
|   - Canteen Demand Forecaster            |    |  [Storage Subsystem]                             |
|   - Energy Isolation Forest Detector     |    |   - Static Assets (`static/`)                    |
|   - Waste TrashNet Vision Classifier     |    |   - User Uploads / Media (`media/`)              |
|   - Traffic Flow CV Analyzer             |    |   - Trained Models (`models/`)                   |
|   - Model Registry (`model_registry.json`|    |                                                  |
+------------------------------------------+    +--------------------------------------------------+
                      |                                                   |
+--------------------------------------------------------------------------------------------------+
|                                  EXTERNAL INTEGRATIONS & TELEMETRY                               |
|  - Open-Meteo REST API (Real-time weather, temperature, solar irradiance; zero-key, CC-BY 4.0)    |
|  - Dynamic Offline Weather Cache (Instant failover for offline / air-gapped demo environments)   |
|  - Virtual Bus GPS Simulation Loop (Adjustable speed 1x to 10x with geofencing)                  |
|  - Computer Vision frame ingestion (Synthetic & real campus camera feeds)                        |
+--------------------------------------------------------------------------------------------------+
```

---

## 2. Subsystem Descriptions

### 2.1 Web & Application Core (`config/`, `apps/accounts`, `apps/common`)
- **Django 6.1.1 Engine**: Configured with asynchronous WSGI capabilities, clean modular routing, and enterprise security headers (CSRF, XSS filter, clickjacking protection).
- **Custom User Model (`User`)**: Extends `AbstractUser` to support 12 distinct campus personas, department affiliations, phone numbers, and profile avatars.
- **Audit Logging**: Every sensitive action (grade updates, role switches, complaints triage, intervention actions) is automatically committed to `apps.common.models.AuditLog` with timestamp, actor, IP address, and payload delta.

### 2.2 Academic Intelligence & Early Warning (`apps/academics`, `ml/academic`)
- **Multi-Horizon Risk Architecture**:
  1. *Tabular Demographic & Historic Predictor*: Scikit-Learn Random Forest trained on UCI Student Performance & Higher Education datasets. Computes early baseline risk before semester midterms.
  2. *Sequential Temporal Trajectory Engine*: PyTorch/MLP architecture processing 5-week rolling attendance, quiz marks, and assignment completion sequences to capture downward performance velocity.
- **Intervention Lifecycle**: Flags students as High, Medium, or Low Risk; automatically drafts individualized intervention plans assigned to department faculty mentors.

### 2.3 Intelligent Operations & Facilities (`apps/transport`, `apps/parking`, `apps/energy`, `apps/waste`, `apps/canteen`)
- **Smart Transport & Telemetry**:
  - Live GPS bus tracking on OpenStreetMap with Leaflet.js.
  - Interactive simulation engine with 1x, 2x, 5x, and 10x speed multipliers.
  - Dynamic ETA prediction based on distance remaining and simulated route velocity.
- **Visual Parking Grid**:
  - 220 individual parking bays categorized by vehicle type (Two-Wheeler, Faculty Car, Student Car, EV Charging, Accessible).
  - Real-time AJAX occupancy toggling and zone-level capacity gauges.
- **Energy Anomaly & Sustainability**:
  - Scikit-Learn `IsolationForest` continuously monitors kilowatt readings across campus sub-meters (Academic Block A, Engineering Labs, Central Library, Hostels, Sports Complex).
  - Detects nocturnal base-load leaks, abnormal spikes, and equipment idling during off-hours.
- **Waste Management (TrashNet Classifier)**:
  - Six-class waste image classifier categorizing discarded materials into *Cardboard, Glass, Metal, Paper, Plastic, Trash*.
  - Provides institutional disposal instructions and recycling incentives.
- **Canteen Demand Forecaster**:
  - Multi-feature regressor forecasting daily meal counts (Breakfast, Lunch, Dinner) based on day of week, active student headcount, campus events scheduled, and weather conditions.

### 2.4 Campus Social & Collaborative Hub (`apps/clubs`, `apps/events`, `apps/projects`, `apps/recommendations`)
- **Smart Event Hub**:
  - Event publishing, capacity gating, and automated QR check-in tokens.
  - Random Forest attendance predictor estimating actual turnout vs. registration count based on speaker tier, category, day of week, and weather forecast.
- **Complementary Team Formation Engine**:
  - Content-based TF-IDF and Euclidean skill matching.
  - Recommends multi-disciplinary teammates for hackathons and capstone projects by identifying students with complementary skills (e.g., matching a Frontend UI developer with a Backend Django/ML engineer and UI/UX designer).

### 2.5 Grievance Redressal & Support (`apps/complaints`, `apps/ai_assistant`)
- **Automated NLP Triage**:
  - Logistic Regression pipeline with TF-IDF n-gram vectorizer trained on labeled campus grievance corpora.
  - Categorizes raw complaint descriptions into *Academic, Hostel, Infrastructure, Canteen, Harassment, Transport, Network, Library, Accounts*.
  - Calculates priority, urgency score, and estimated SLA resolution timeline.
- **Permission-Aware Campus AI Assistant**:
  - Conversational NLP assistant with strict role-based access control.
  - Students cannot query institutional budgets or peer confidential grades.
  - Faculty and HODs receive aggregated metrics and department analytics.

---

## 3. Dual-Database Failover Architecture

CampusPulse AI implements a robust dual-database layer configured in `config/settings.py`:

```python
# Primary: MySQL 8.x
# Fallback: Zero-friction embedded SQLite (campuspulse.sqlite3)
```

1. **Production Mode (MySQL 8.x)**: Uses `pymysql` driver with connection pooling, transaction isolation, and UTF8mb4 encoding for high concurrency.
2. **Development / Offline Mode (SQLite)**: If MySQL is not detected or credentials are left at default without a running daemon, the system automatically falls back to `campuspulse.sqlite3` without throwing runtime exceptions or halting deployment.
3. **Database Portability**: All database models avoid proprietary database-specific functions, ensuring 100% schema parity across MySQL, PostgreSQL, and SQLite.

---

## 4. Machine Learning Pipeline Architecture

```
                       [ RAW DATASETS ]
    (UCI Student Performance, TrashNet, Simulated Campus Telemetry)
                              |
                              v
                  [ PREPROCESSING & CLEANING ]
          - Missing value imputation
          - One-hot encoding for categorical attributes
          - Standard scaling for continuous metrics
          - TF-IDF vectorization for unstructured text
                              |
                              v
                   [ MODEL TRAINING SUITE ]
  +-------------------------------------------------------------+
  | - Academic Risk RF & Sequential MLP                         |
  | - Complaint NLP Classifier (TF-IDF + Logistic Regression)   |
  | - Event Attendance Regressor                                |
  | - Canteen Demand Forecaster                                 |
  | - Energy Isolation Forest                                   |
  | - TrashNet Waste Vision Classifier                          |
  +-------------------------------------------------------------+
                              |
                              v
                 [ ARTIFACT PERSISTENCE & REGISTRY ]
          - Serialized .joblib artifacts saved in `models/`
          - Performance metrics logged in `models/model_registry.json`
                              |
                              v
                     [ INFERENCE ENGINE ]
          - Fast in-memory CPU evaluation (< 25ms per query)
          - Transparent explainability features (risk factor list)
```

---

## 5. Security & RBAC Matrix

The system implements 12 strictly segregated roles:
- `SUPER_ADMIN`: Universal system administration, model retraining, database audit.
- `CAMPUS_ADMIN`: Overall campus operations, facility management, announcements.
- `DEAN`: Academic governance, cross-department analytics, faculty oversight.
- `HOD`: Departmental operations, faculty assignment, curriculum review.
- `FACULTY`: Course delivery, student grading, academic intervention mentoring.
- `STUDENT`: Course enrollment, attendance, grievance submission, event check-in.
- `CLUB_LEAD`: Club management, event organization, budget requests.
- `TRANSPORT_MGR`: Fleet tracking, bus route management, driver assignment.
- `WARDEN`: Hostel allocation, room discipline, curfew monitoring.
- `CANTEEN_MGR`: Meal forecasting, menu management, consumption records.
- `ENERGY_MGR`: Sub-meter telemetry, anomaly alerts, sustainability tracking.
- `SECURITY_OFFICER`: Parking management, visitor logs, campus gate surveillance.

Access is enforced at both view level (`@role_required`) and object/queryset level, preventing horizontal privilege escalation across departments and student records.
