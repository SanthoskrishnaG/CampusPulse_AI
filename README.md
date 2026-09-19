# CampusPulse AI
### AI-Powered Real-Time Intelligent Campus Operating, Management and Student Experience Platform

![Python](https://img.shields.io/badge/Python-3.11%2B%20%7C%203.14-blue)
![Django](https://img.shields.io/badge/Django-5.x%20%26%206.x-green)
![Database](https://img.shields.io/badge/Database-MySQL%208.x%20%7C%20SQLite-orange)
![Machine Learning](https://img.shields.io/badge/Machine%20Learning-Scikit--Learn-purple)
![Deep Learning](https://img.shields.io/badge/Deep%20Learning-MLP%20%2F%20Sequential%20Temporal%20Net-red)
![License](https://img.shields.io/badge/License-MIT-blue)

---

## Executive Overview
**CampusPulse AI** is an enterprise-grade, integrated higher-education campus operating system. Built as a single cohesive platform rather than disconnected mini-projects, CampusPulse AI unifies **14 campus domains**, **12 role-based access control (RBAC) tiers**, **6 machine learning and deep learning pipelines**, and a **real-time command center** sharing one database, one authentication system, and one telemetry engine.

The platform continuously analyzes campus data, **predicts** what is likely to happen, **explains** why, **recommends** proactive interventions, and **learns** from real-world outcomes.

---

## Unified Functional Scope

| Domain | Key Capabilities | ML / DL Intelligence Model |
| :--- | :--- | :--- |
| **Student Intelligence** | Academic transcripts, attendance percentiles, skill profiles | Profile Vectorizer |
| **Academic Risk AI** | Early warning diagnostics, faculty intervention scheduling | Random Forest Ensemble + Sequential Temporal DL (Week 1->5) |
| **Department Management** | HOD command center, student risk breakdown, syllabi | Multi-Department Aggregator |
| **Events & Workshops** | Unified event calendar, QR check-in entry passes | Random Forest Attendance & No-Show Regressor |
| **Student Clubs** | 20+ clubs, membership rosters, achievements | Content-Based TF-IDF Recommender |
| **Projects & Teammates** | Capstone requirements, complementary team formation | Multi-Disciplinary Complementary Skill Matcher |
| **Complaint AI** | Natural language grievance intake, SLA enforcement | TF-IDF + Logistic Classifier + Regex Entity Triage |
| **Smart Transport** | Live GPS bus tracking, simulated movement (1x-10x) | Arrival Delay & Route ETA Regressor |
| **Traffic & Gate Vision** | Camera snapshot vehicle counting (cars, bikes, buses) | Computer Vision Vehicle Density & Congestion Analyzer |
| **Smart Parking** | Live bay visualizer, interactive entry/exit simulation | Time-Series Bay Occupancy Forecaster |
| **Canteen Intelligence** | Portion planning, food waste audit, actuals logging | Meal Demand Regressor with Safety Buffer |
| **Energy Anomaly AI** | Live kWh telemetry, building meters, nocturnal alerts | Unsupervised Isolation Forest Anomaly Detector |
| **Waste Computer Vision** | 6-Class TrashNet segregation scanner, disposal guide | Computer Vision Texture & Color Moment Classifier |
| **AI Campus Assistant** | Permission-aware natural language query engine | Rule & Structured Query Engine with RBAC Safeguards |

---

## 12 Role-Based Access Control (RBAC) Demo Credentials

All demo accounts share the password: `admin123`

| Username | Role | Dashboard Route |
| :--- | :--- | :--- |
| `superadmin` | Super Administrator | `/analytics/dashboard/` (Master Command Center) |
| `collegeadmin` | College Administrator | `/analytics/dashboard/` |
| `deptadmin` | Department Administrator (HOD) | `/departments/dashboard/` |
| `faculty` | Faculty Member & Mentor | `/faculty/dashboard/` |
| `student` | Student | `/students/dashboard/` |
| `clubadmin` | Club Administrator | `/clubs/dashboard/` |
| `clubmember` | Club Member | `/students/dashboard/` |
| `transportmgr` | Fleet & Transport Manager | `/transport/dashboard/` |
| `canteenmgr` | Dining & Kitchen Manager | `/canteen/dashboard/` |
| `maintenance` | Maintenance Field Staff | `/complaints/dashboard/` |
| `facilitymgr` | Facilities Operations Manager | `/complaints/dashboard/` |
| `security` | Campus Security Staff | `/traffic/dashboard/` |

> [!TIP]
> Use the **Role Switcher Dropdown** in the top navigation bar during vivas or presentations to instantly switch perspectives without logging out!

---

## Local Windows Installation Guide

### Prerequisites
- **Python 3.11+** installed (verified on Python 3.14)
- **Git** installed
- **MySQL 8.x** (optional: if MySQL credentials are not configured, system automatically falls back to SQLite `campuspulse.sqlite3` with zero friction).

### 1. Clone or Open the Workspace
```powershell
cd c:\Users\Santhoskrishna\Documents\CampusPulse_AI
```

### 2. Environment Configuration
Copy the configuration template:
```powershell
copy .env.example .env
```
To enable MySQL 8.x, set in `.env`:
```ini
USE_MYSQL=True
DB_NAME=campuspulse_db
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=127.0.0.1
DB_PORT=3306
```
*(If `USE_MYSQL=False` or connection fails, the platform automatically logs a notice and runs cleanly on SQLite).*

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 4. Run Migrations
```powershell
python manage.py makemigrations
python manage.py migrate
```

### 5. Train Baseline Machine Learning Models
```powershell
python manage.py train_models
```
*(Trains and registers all 6 ML/DL models into `models/model_registry.json`).*

### 6. Seed Complete Demo Campus Data
```powershell
python manage.py seed_demo_data
```
*(Populates 500+ students, 50+ faculty, 7 departments, 20+ clubs, 100+ events, 500+ complaints, transport, and runs initial ML risk inference).*

### 7. Run Test Suite
```powershell
python manage.py test tests
```

### 8. Running the Application

#### DEVELOPMENT
Preferred Windows startup:
```cmd
start_dev.bat
```
*(or `./start_dev.ps1` in PowerShell)*

The startup script sets the official Django 6.1 environment variable:
```powershell
$env:DJANGO_RUNSERVER_HIDE_WARNING="true"
python manage.py runserver
```
This cleanly hides the development-server warning during local development while preserving all genuine migration warnings, system check errors, and tracebacks.

> [!NOTE]
> Setting `DJANGO_RUNSERVER_HIDE_WARNING=true` only suppresses the development warning banner; it does **not** make `runserver` a production server. For production deployments or production-like local execution, use the WSGI server below.

#### PRODUCTION-LIKE LOCAL SERVER
Run:
```powershell
waitress-serve --listen=127.0.0.1:8000 config.wsgi:application
```
This starts the application using **Waitress** instead of Django's development server, removing the development server warning and serving assets via the production WSGI interface.

Alternatively, on Windows you can simply run:
```cmd
start_production.bat
```
*(or `./start_production.ps1` in PowerShell)*

Open your browser at **`http://127.0.0.1:8000/`**.

---

### 9. Accessing & Testing in Windows PowerShell

> [!NOTE]
> In Windows PowerShell, **`GET`** is an HTTP protocol method name, not a terminal executable command. Entering `GET http://...` in PowerShell causes an error (`The term 'GET' is not recognized as the name of a cmdlet...`). Always use the native PowerShell cmdlets below or open the URL in your browser:

#### A. Open Dashboard in Web Browser
```powershell
Start-Process "http://127.0.0.1:8000/canteen/dashboard/"
```
*Alternatively, simply open `http://127.0.0.1:8000/canteen/dashboard/` in Chrome or Edge.*

#### B. Verify HTTP Status in PowerShell (`Invoke-WebRequest`)
```powershell
Invoke-WebRequest "http://127.0.0.1:8000/canteen/dashboard/"
```
To inspect status code directly:
```powershell
(Invoke-WebRequest -UseBasicParsing "http://127.0.0.1:8000/canteen/dashboard/").StatusCode
# Returns: 200
```

#### C. Test REST APIs in PowerShell (`Invoke-RestMethod`)
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/transport/api/live-telemetry/"
```