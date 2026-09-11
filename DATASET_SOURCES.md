# CampusPulse AI - Dataset Sources, Licensing & Data Attribution

CampusPulse AI is committed to open, reproducible, and ethically sourced data science. The platform relies exclusively on permissive, openly licensed academic benchmarks, public telemetry APIs, and synthetic simulation generators. No proprietary, paid, or private college records are required to operate or demonstrate this platform.

---

## 1. Primary Datasets

### 1.1 UCI Student Performance Data Set
- **Source**: UCI Machine Learning Repository
- **Authors**: Paulo Cortez and Alice Silva (University of Minho, Portugal)
- **Publication**: Cortez, P., & Silva, A. (2008). *Using data mining to predict secondary school student performance.* In Proceedings of 5th Annual Future Business Technology Conference (FUBUTEC 2008), Porto, Portugal, pp. 5-12.
- **License**: Creative Commons Attribution 4.0 International (CC BY 4.0)
- **Direct Repository Link**: `https://archive.ics.uci.edu/dataset/320/student+performance`
- **Instance Count & Features**:
  - 649 instances (Portuguese language course) / 395 instances (Mathematics course)
  - 30 attributes including demographic variables, study time, alcohol consumption, past failures, family support, and final grades (G1, G2, G3).
- **Application in CampusPulse AI**:
  - Serves as the foundational feature schema and distribution baseline for the Academic Early-Warning Risk Classifier (`ml/academic/risk_classifier.py`).
  - Used to calibrate feature importance weights for study time, parental education, absences, and historical academic failure counts.

---

### 1.2 UCI Higher Education Students Performance Evaluation
- **Source**: UCI Machine Learning Repository
- **Authors**: Mustafa Yildiz, et al.
- **License**: Creative Commons Attribution 4.0 International (CC BY 4.0)
- **Direct Repository Link**: `https://archive.ics.uci.edu/dataset/854/higher+education+students+performance+evaluation`
- **Instance Count & Features**:
  - 145 instances
  - 31 attributes covering student classroom attendance, cumulative GPA, project work participation, classroom engagement, and exam performance.
- **Application in CampusPulse AI**:
  - Utilized to calibrate higher education-specific indicators such as seminar attendance, cumulative GPA trajectory, and departmental course loads.

---

### 1.3 TrashNet Dataset (Image Classification for Smart Waste)
- **Source**: Stanford University CS229 Project / Mindy Yang and Gary Thung
- **Authors**: Gary Thung and Mindy Yang (Stanford University)
- **License**: MIT Open Source License / Educational Research Permissive
- **Direct Repository Link**: `https://github.com/garythung/trashnet`
- **Instance Count & Classes**:
  - 2,527 high-resolution labeled images across 6 primary material classes:
    1. Glass (501 images)
    2. Paper (594 images)
    3. Cardboard (403 images)
    4. Plastic (482 images)
    5. Metal (410 images)
    6. Trash (137 images)
- **Application in CampusPulse AI**:
  - Powers the Campus Waste Management Classifier (`apps/waste/classifier.py`).
  - Provides institutional guidance for campus bin segregation, carbon footprint reduction, and recyclable material recovery metrics.

---

## 2. Public APIs & Telemetry Sources

### 2.1 Open-Meteo Weather API
- **Provider**: Open-Meteo GmbH
- **Endpoint**: `https://api.open-meteo.com/v1/forecast`
- **License**: Creative Commons Attribution 4.0 International (CC BY 4.0) for non-commercial and academic usage.
- **Authentication**: Zero-key required; no secret tokens or paid credit cards needed.
- **Parameters Queried**:
  - Ambient Temperature (°C)
  - Relative Humidity (%)
  - Precipitation Probability (%)
  - Weather Code (WMO standards: Clear, Partly Cloudy, Rain, Thunderstorm)
  - Surface Solar Radiation (W/m²)
- **Application in CampusPulse AI**:
  - Real-time weather banner on dashboard headers (`apps/common/weather.py`).
  - Input feature for Event Attendance prediction (rain probability dampens outdoor event turnout).
  - Input feature for Canteen Demand forecasting (cold/rainy weather shifts student meal choices towards hot soups and curries).
  - Inbuilt offline caching layer guarantees graceful operation in network-isolated presentation environments.

---

### 2.2 OpenStreetMap & CartoDB Positron
- **Provider**: OpenStreetMap Foundation & Carto
- **License**: Open Data Commons Open Database License (ODbL) / CC BY 3.0
- **Application in CampusPulse AI**:
  - Interactive Leaflet.js base map for spatial campus rendering (`static/js/main.js`).
  - Geofenced college boundaries, building markers, bus stops, and virtual GPS transport paths.

---

## 3. Synthetic Seed Data Generation Methodology

To provide a fully populated, production-feeling environment out of the box, `apps/common/management/commands/seed_demo_data.py` synthesizes:
- **500+ Realistic Students**: Distributed across 5 engineering and science departments (Computer Science, Artificial Intelligence & Data Science, Electronics & Communication, Mechanical Engineering, Business & Management) with varied CGPA, attendance rates, club memberships, and skills.
- **52 Faculty Members**: Ranging from Assistant Professors to Department Heads and Deans.
- **21 Clubs & Societies**: Technical, cultural, sports, entrepreneurship, and social outreach chapters.
- **105+ Campus Events**: Workshops, guest lectures, hackathons, sports tournaments, and symposiums.
- **510+ Support & Grievance Tickets**: Varied across hostel maintenance, WiFi issues, grading queries, laboratory hardware faults, and canteen hygiene.
- **10 Campus Fleet Buses & 220 Smart Parking Slots**: Generating live simulated GPS coordinates and parking slot sensor states.

All synthetic data adheres to realistic statistical distributions matching the UCI benchmark datasets.
