# CampusPulse AI - Database Schema & ER Documentation

CampusPulse AI utilizes a fully normalized relational schema designed for high-throughput transactional integrity (OLTP) and analytics queries (OLAP). The schema is 100% portable across MySQL 8.x (InnoDB engine) and SQLite 3.

---

## 1. High-Level Entity-Relationship (ER) Overview

```
 [User] (Custom User Model)
    |-- 1:1 --> [Student] (CGPA, attendance, semester, skills, department)
    |              |-- 1:N --> [Enrollment] (Course Offering, final grade)
    |              |-- 1:N --> [WeeklyPerformanceRecord] (5-week rolling temporal marks)
    |              |-- 1:N --> [AcademicRiskAssessment] (RF & MLP score, factors)
    |              |-- 1:N --> [AcademicIntervention] (Remedial plan, mentor)
    |              |-- 1:N --> [ClubMembership] (Role, join date)
    |              |-- 1:N --> [EventRegistration] (QR Token, check-in status)
    |              |-- 1:N --> [TeamMember] --> [Team] --> [Project]
    |-- 1:1 --> [Faculty] (Designation, specialization, department)
    |-- 1:N --> [Complaint] (NLP category, priority, SLA status)
    |-- 1:N --> [AuditLog] (Action, timestamp, IP, actor)
    |-- 1:N --> [Notification] (Title, message, read flag)

 [Department]
    |-- 1:N --> [Faculty]
    |-- 1:N --> [Student]
    |-- 1:N --> [Course] --> [CourseOffering]
    |-- 1:N --> [DepartmentAnnouncement]
    |-- 1:N --> [DepartmentResource]

 [Smart Campus Infrastructure]
    |-- [BusRoute] --> 1:N --> [BusStop]
    |-- [BusRoute] --> 1:N --> [Bus] (GPS lat/long, speed, simulated driver)
    |-- [ParkingLot] --> 1:N --> [ParkingSlot] (Bay code, slot type, occupancy flag)
    |-- [EnergyMeter] --> 1:N --> [EnergyReading] (kW load, anomaly flag, score)
    |-- [Canteen] --> 1:N --> [MenuItem]
    |-- [Canteen] --> 1:N --> [MealForecast] & [MealRecord]
    |-- [WasteRecord] (Material class, weight kg, recyclable flag)
```

---

## 2. Detailed Table Specifications

### 2.1 Identity & Access (`apps_accounts`)
- **`accounts_user`**:
  - `id` (INT, PK, AUTO_INCREMENT)
  - `username` (VARCHAR(150), UNIQUE)
  - `email` (VARCHAR(254), UNIQUE)
  - `role` (VARCHAR(30)): Enum [`SUPER_ADMIN`, `CAMPUS_ADMIN`, `DEAN`, `HOD`, `FACULTY`, `STUDENT`, `CLUB_LEAD`, `TRANSPORT_MGR`, `WARDEN`, `CANTEEN_MGR`, `ENERGY_MGR`, `SECURITY_OFFICER`]
  - `department_id` (FK -> `departments_department`, NULLABLE)
  - `phone_number` (VARCHAR(20))
  - `avatar` (VARCHAR(255))
  - Standard Django auth fields (`password`, `is_active`, `is_staff`, `is_superuser`, `date_joined`)

---

### 2.2 Academic Records (`apps_academics`, `apps_students`)
- **`students_student`**:
  - `id` (INT, PK)
  - `user_id` (FK -> `accounts_user`, UNIQUE)
  - `roll_number` (VARCHAR(30), UNIQUE, INDEXED)
  - `department_id` (FK -> `departments_department`)
  - `current_semester` (INT: 1-8)
  - `current_cgpa` (DECIMAL(4, 2))
  - `overall_attendance_rate` (DECIMAL(5, 2))
  - `past_failures_count` (INT)
  - `skills` (TEXT: comma-separated skill tokens)
  - `interests` (TEXT)
  - `mentor_id` (FK -> `faculty_faculty`, NULLABLE)

- **`academics_weeklyperformancerecord`**:
  - `id` (INT, PK)
  - `student_id` (FK -> `students_student`, INDEXED)
  - `course_offering_id` (FK -> `academics_courseoffering`)
  - `week_number` (INT: 1-16)
  - `attendance_percentage` (DECIMAL(5, 2))
  - `quiz_score` (DECIMAL(5, 2))
  - `assignment_submitted` (BOOLEAN)
  - `notes` (TEXT)

- **`academics_academicriskassessment`**:
  - `id` (INT, PK)
  - `student_id` (FK -> `students_student`)
  - `assessment_date` (DATETIME, DEFAULT NOW)
  - `risk_level` (VARCHAR(10)): `LOW`, `MEDIUM`, `HIGH`
  - `risk_score` (DECIMAL(4, 3)): e.g. 0.842
  - `model_version` (VARCHAR(50))
  - `contributing_factors` (JSON / TEXT)
  - `is_resolved` (BOOLEAN)

---

### 2.3 Grievance Redressal (`apps_complaints`)
- **`complaints_complaint`**:
  - `id` (INT, PK)
  - `ticket_number` (VARCHAR(30), UNIQUE)
  - `complainant_id` (FK -> `accounts_user`)
  - `title` (VARCHAR(200))
  - `raw_description` (TEXT)
  - `nlp_predicted_category` (VARCHAR(50))
  - `category_confidence` (DECIMAL(4, 3))
  - `priority` (VARCHAR(20)): `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`
  - `status` (VARCHAR(20)): `SUBMITTED`, `TRIAGED`, `IN_PROGRESS`, `RESOLVED`, `CLOSED`
  - `sla_deadline` (DATETIME)
  - `assigned_staff_id` (FK -> `accounts_user`, NULLABLE)
  - `created_at`, `updated_at` (DATETIME)

---

### 2.4 Smart Operations & Facilities
- **`transport_bus`**:
  - `id` (INT, PK)
  - `bus_number` (VARCHAR(20), UNIQUE)
  - `route_id` (FK -> `transport_busroute`)
  - `driver_name` (VARCHAR(100))
  - `driver_phone` (VARCHAR(20))
  - `current_latitude` (DECIMAL(9, 6))
  - `current_longitude` (DECIMAL(9, 6))
  - `speed_kmh` (DECIMAL(5, 2))
  - `is_active` (BOOLEAN)

- **`parking_parkingslot`**:
  - `id` (INT, PK)
  - `lot_id` (FK -> `parking_parkinglot`)
  - `slot_code` (VARCHAR(20)): e.g. "BAY-A1", "EV-04"
  - `slot_type` (VARCHAR(20)): `TWO_WHEELER`, `CAR_STUDENT`, `CAR_FACULTY`, `EV_CHARGING`, `ACCESSIBLE`
  - `is_occupied` (BOOLEAN, DEFAULT FALSE)
  - `updated_at` (DATETIME)

- **`energy_energymeter` & `energy_energyreading`**:
  - `meter_code` (VARCHAR(50), UNIQUE)
  - `location_name` (VARCHAR(150))
  - `current_reading_kw` (DECIMAL(8, 2))
  - `is_anomaly_flagged` (BOOLEAN)
  - `anomaly_score` (DECIMAL(5, 3))

---

## 3. Database Indexes & Performance Optimizations

1. **Roll Number & Ticket Lookups**: Unique B-tree indexes on `roll_number` and `ticket_number` guarantee $O(1)$ lookup time during campus identity checks.
2. **Composite Indexes for Temporal Sequence Queries**:
   - `CREATE INDEX idx_student_week ON academics_weeklyperformancerecord (student_id, week_number);`
3. **Telemetry Filtering**:
   - `CREATE INDEX idx_bus_active ON transport_bus (is_active, route_id);`
   - `CREATE INDEX idx_parking_occupied ON parking_parkingslot (lot_id, is_occupied);`
