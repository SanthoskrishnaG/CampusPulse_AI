# CampusPulse AI - REST API Documentation

CampusPulse AI provides a modular RESTful API built on Django REST Framework (DRF). All API endpoints return JSON responses with standard HTTP status codes (`200 OK`, `201 Created`, `400 Bad Request`, `401 Unauthorized`, `403 Forbidden`, `404 Not Found`).

---

## 1. Authentication & Session Endpoints

### 1.1 Fast Demo Login Switcher
- **Endpoint**: `POST /accounts/demo-login/`
- **Description**: Instantly switches session identity between 12 campus personas during demonstrations.
- **Request Body**:
  ```json
  {
    "role": "DEAN" // or "FACULTY", "STUDENT", "HOD", "TRANSPORT_MGR", etc.
  }
  ```
- **Response** (`302 Found` / Redirect to domain dashboard).

### 1.2 User Profile
- **Endpoint**: `GET /accounts/profile/`
- **Description**: Returns authenticated user identity, role, department, and active permissions.

---

## 2. Academic Intelligence APIs

### 2.1 Calculate Academic Risk
- **Endpoint**: `POST /academics/api/assess-risk/`
- **Role Required**: `FACULTY`, `HOD`, `DEAN`, `SUPER_ADMIN`
- **Request Body**:
  ```json
  {
    "student_id": 104,
    "current_cgpa": 5.82,
    "attendance_rate": 68.5,
    "past_failures": 2,
    "weekly_quiz_avg": 54.0,
    "assignment_completion_rate": 60.0
  }
  ```
- **Response**:
  ```json
  {
    "status": "success",
    "student_id": 104,
    "risk_level": "HIGH",
    "risk_score": 0.842,
    "confidence": 0.91,
    "top_contributing_factors": [
      "Low classroom attendance (< 70%)",
      "Historical arrears / course failures >= 2",
      "Downward assignment completion trend over 3 weeks"
    ],
    "suggested_interventions": [
      "Assign peer tutor for Data Structures & Algorithms",
      "Schedule counselor consultation regarding hostel attendance"
    ]
  }
  ```

### 2.2 Submit Academic Intervention
- **Endpoint**: `POST /academics/api/interventions/`
- **Role Required**: `FACULTY`, `HOD`
- **Request Body**:
  ```json
  {
    "student_id": 104,
    "title": "Remedial Coaching - Circuit Theory",
    "intervention_type": "REMEDIAL_CLASS",
    "notes": "Student agreed to attend 4 Saturday lab tutorials."
  }
  ```

---

## 3. Grievance & Complaints NLP APIs

### 3.1 Submit & Auto-Triage Complaint
- **Endpoint**: `POST /complaints/api/submit/`
- **Description**: Ingests raw natural language complaint, executes NLP triage pipeline, assigns category, priority score, and SLA target.
- **Request Body**:
  ```json
  {
    "title": "WiFi router dead on 3rd floor hostel",
    "description": "The internet connectivity in Block B has been offline since yesterday night. Students cannot submit online lab assignments."
  }
  ```
- **Response**:
  ```json
  {
    "ticket_id": "TKT-2026-0814",
    "predicted_category": "NETWORK",
    "confidence": 0.89,
    "priority": "HIGH",
    "estimated_sla_hours": 8,
    "assigned_department": "Campus IT Infrastructure",
    "status": "TRIAGED"
  }
  ```

---

## 4. Smart Operations & Telemetry APIs

### 4.1 Bus Fleet Live Tracking
- **Endpoint**: `GET /transport/api/fleet-positions/`
- **Description**: Returns live GPS coordinates, speeds, occupancy, next stop, and ETA for all active buses.
- **Response**:
  ```json
  [
    {
      "bus_id": 1,
      "route_name": "Route 1: City Center to Campus Main Gate",
      "latitude": 13.0428,
      "longitude": 80.2115,
      "speed_kmh": 34.5,
      "current_occupancy": 32,
      "capacity": 45,
      "next_stop": "Anna Arch",
      "eta_minutes": 7.2
    }
  ]
  ```

### 4.2 Parking Slot Status & AJAX Toggle
- **Endpoint**: `GET /parking/api/slots/`
- **Description**: Returns occupancy grid for all 220 parking bays.
- **Endpoint**: `POST /parking/api/toggle-slot/`
- **Request Body**:
  ```json
  {
    "slot_id": 42,
    "is_occupied": true
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "slot_id": 42,
    "slot_code": "B-12",
    "is_occupied": true,
    "lot_name": "East Academic Bay",
    "available_slots_in_lot": 28
  }
  ```

### 4.3 Energy Telemetry & Anomaly Stream
- **Endpoint**: `GET /energy/api/telemetry/`
- **Description**: Returns real-time meter readings and Isolation Forest anomaly status.
- **Response**:
  ```json
  {
    "meter_name": "Robotics & AI Research Lab",
    "current_load_kw": 48.2,
    "baseline_expected_kw": 22.5,
    "is_anomaly": true,
    "anomaly_score": -0.68,
    "flag": "HIGH_NOCTURNAL_CONSUMPTION",
    "timestamp": "2026-09-11T12:00:00Z"
  }
  ```

### 4.4 Waste Classification Inference
- **Endpoint**: `POST /waste/api/classify/`
- **Request**: Multipart image upload (`image` field)
- **Response**:
  ```json
  {
    "material_type": "PLASTIC",
    "confidence": 0.88,
    "recyclable": true,
    "target_bin": "Blue Recycling Bin (Plastics & Polymers)",
    "eco_points_earned": 5
  }
  ```

---

## 5. Event & Canteen Machine Learning APIs

### 5.1 Event Attendance Forecaster
- **Endpoint**: `POST /events/api/forecast-turnout/`
- **Request Body**:
  ```json
  {
    "category": "WORKSHOP",
    "registrations_count": 120,
    "is_weekend": false,
    "rain_probability": 15.0,
    "is_flagship": true
  }
  ```
- **Response**:
  ```json
  {
    "predicted_turnout": 104,
    "expected_show_up_rate_percent": 86.6,
    "seating_recommendation": "Auditorium Hall 2 (Capacity 120)"
  }
  ```

### 5.2 Canteen Daily Meal Demand
- **Endpoint**: `GET /canteen/api/forecast-demand/?date=2026-09-12`
- **Response**:
  ```json
  {
    "forecast_date": "2026-09-12",
    "predicted_portions": {
      "breakfast": 380,
      "lunch": 640,
      "dinner": 410
    },
    "waste_prevention_factor": "-18% vs unguided prep",
    "cost_savings_estimate_inr": 8500
  }
  ```

---

## 6. Campus AI Assistant NLP API

### 6.1 Conversational Query Endpoint
- **Endpoint**: `POST /assistant/api/chat/`
- **Description**: Natural language question-answering with strict RBAC boundary checks.
- **Request Body**:
  ```json
  {
    "message": "When is the next AI club workshop and where is it held?"
  }
  ```
- **Response**:
  ```json
  {
    "response": "The next AI Club event is 'Deep Learning on Edge Hardware', scheduled for September 18th at 3:30 PM in Seminar Hall 3.",
    "role_context": "STUDENT",
    "data_sources_queried": ["apps.events.models.Event"]
  }
  ```
