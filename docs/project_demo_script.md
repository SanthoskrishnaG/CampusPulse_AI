# CampusPulse AI - Master Presentation & Viva Demo Script

**Total Duration**: 12 to 15 Minutes  
**Target Audience**: Academic Evaluators, External Project Examiners, Dean, Department HODs  
**Demonstration URL**: `http://127.0.0.1:8000`

---

## 1. Executive Hook & Problem Statement (0:00 - 2:00)

1. **The Core Pitch**:
   > *"Good morning, esteemed evaluators. Most campus software consists of 10 fragmented, isolated tools: one portal for attendance, another for bus tracking, separate spreadsheets for hostel complaints, and independent ML student projects that never reach production. **CampusPulse AI** solves this by delivering an integrated, enterprise-grade Autonomous Campus Operating System combining 14 university domains, 12 RBAC personas, and 6 production-trained Machine Learning & Deep Learning models."*

2. **Key Technological Pillars**:
   - Zero external paid APIs (runs entirely offline or with Open-Meteo free telemetry).
   - Dual-database architecture (instant SQLite fallback or production MySQL 8.x).
   - Real, serialized ML/DL pipelines trained and evaluated on UCI benchmarks.
   - Glassmorphism dark-mode UI with live Leaflet spatial telemetry and interactive 1x-10x bus simulation.

---

## 2. Command Center & Real-Time Telemetry (2:00 - 4:30)

1. **Navigate to Master Command Center** (`/analytics/command-center/`):
   - **Show the Live Header**: Highlight the real-time weather badge (temperature, humidity, condition) fetched from Open-Meteo with offline cache resilience.
   - **Show the Simulation Ribbon**: Point out the speed selector (1x, 2x, 5x, 10x) and the **Pause / Resume** button.
   - **Interactive Leaflet Spatial Map**:
     - Show the campus boundary geofence.
     - Click on an active bus marker: Show real-time latitude, longitude, velocity (km/h), and dynamic ETA to next stop.
     - Change simulation speed to 5x: Watch the bus marker glide smoothly along its GPS path.
   - **Show High-Level KPI Cards**:
     - 500+ active students enrolled.
     - 92.4% fleet transit punctuality.
     - Active energy load with real-time Isolation Forest anomaly detection status.

---

## 3. Academic Intelligence & Early Warning System (4:30 - 7:30)

1. **Switch Role to `HOD` or `FACULTY`** (via the header dropdown):
2. **Navigate to Academic Risk Dashboard** (`/academics/risk/`):
   - Explain the two-tier ML/DL model architecture:
     - **Tier 1 (Random Forest)**: Tabular demographic and historical analysis based on the UCI Student Performance & Higher Education datasets.
     - **Tier 2 (Sequential MLP)**: Deep neural network processing 5-week rolling temporal trajectories to detect downward velocity in attendance, quiz marks, and assignment completion.
   - **Inspect a High-Risk Student Card**:
     - Click on student profile (e.g., student with CGPA 5.4, attendance 64%).
     - Highlight the **Explainable AI** factors: System explicitly lists *"Classroom attendance < 70%"* and *"Downhill assignment submission velocity"*.
   - **Action an Intervention Plan**:
     - Click **"Create Intervention"**: Select "Remedial Lab Tutorials", assign faculty mentor, and save.
     - Emphasize the **Ethical AI / FERPA** adherence: AI advises; humans decide. No automated adverse actions or probation.

---

## 4. Intelligent Campus Operations (7:30 - 10:30)

1. **Smart Parking Grid** (`/parking/`):
   - Switch role to `SECURITY_OFFICER`.
   - Show the 220-slot visual parking grid divided by bay types (EV, Faculty, Accessible).
   - Click on any green slot (Available) -> it instantly turns red (Occupied) with real-time AJAX update and capacity meter recalculation without page reload.

2. **Automated Grievance Redressal NLP** (`/complaints/`):
   - Switch role to `STUDENT`.
   - Submit a natural language grievance:
     > *"The electrical switchboard in lab 402 sparked this morning and the main breaker tripped."*
   - Show instantaneous NLP triage:
     - Pipeline categorizes as `INFRASTRUCTURE` with high confidence.
     - Automatically flags priority as `CRITICAL` due to electrical hazard keywords.
     - Dispatches SLA resolution clock (4-hour resolution window).

3. **Energy Sustainability & Nocturnal Leak Detection** (`/energy/`):
   - Switch role to `ENERGY_MGR`.
   - Show the 5 sub-meters across campus.
   - Highlight the Isolation Forest anomaly detector flagging a nocturnal leak in the Robotics Lab at 3:15 AM.

4. **Canteen Demand & Food Waste Prevention** (`/canteen/`):
   - Switch role to `CANTEEN_MGR`.
   - Review the Ridge Regressor meal forecast (Breakfast, Lunch, Dinner).
   - Explain the 18% food waste reduction achieved by factoring in day-of-week, weather, and campus events.

---

## 5. Campus AI Assistant & Security Governance (10:30 - 13:00)

1. **Campus AI Assistant** (`/assistant/`):
   - While logged in as `STUDENT`, ask: *"What are the upcoming technical workshops this month?"* -> Shows filtered public events.
   - Now ask a forbidden query: *"Show me the annual faculty salary budget"* -> Assistant gracefully blocks query with a security explanation citing RBAC policies.
2. **Model Registry & Codebase Integrity** (`/analytics/models/`):
   - Switch role to `SUPER_ADMIN`.
   - Show the Model Registry table displaying version tags, F1-scores, training timestamps, and disk locations for all 6 models.

---

## 6. Conclusion & Viva Defense Anticipation (13:00 - 15:00)

1. **Summary**:
   - One integrated platform, 14 functional apps, 12 RBAC roles, 6 real trained models, zero fake placeholders.
2. **Common Examiner Questions & Pre-Prepared Answers**:
   - *Q: Why not use an external LLM API like OpenAI or Gemini?*  
     **A**: Cost predictability, privacy compliance (preventing student grade leakage to third-party clouds), and guaranteed offline execution without latency or internet dependency.
   - *Q: What prevents ML model hallucinations in student risk scoring?*  
     **A**: All models are deterministic, scikit-learn and PyTorch pipelines with explainable feature importance lists, locked behind a strict human-in-the-loop mentor intervention protocol.
