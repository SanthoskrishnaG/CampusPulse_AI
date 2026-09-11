# CampusPulse AI - Privacy Policy & Ethical AI Principles

CampusPulse AI is committed to upholding the highest standards of student privacy, algorithmic fairness, and data protection in educational technology. The platform adheres to the core tenets of the **Family Educational Rights and Privacy Act (FERPA)** principles, the **General Data Protection Regulation (GDPR)** guidelines, and India's **Digital Personal Data Protection Act (DPDP Act)**.

---

## 1. Ethical AI Principles

### 1.1 Decision-Support, Not Automated Disciplinary Action
- **Human-in-the-Loop Mandate**: Machine Learning and Deep Learning models within CampusPulse AI are strictly configured as **advisory and early-warning tools**.
- **No Automated Adverse Action**: No student can be placed on academic probation, dismissed, penalized, or demoted based solely on an automated ML risk score.
- **Faculty Review Requirement**: Every high-risk alert triggers a confidential advisory notification to the assigned faculty mentor (`apps/academics`), who must conduct a private 1-on-1 counseling session before any academic intervention is logged.

### 1.2 Algorithmic Bias Mitigation
- **Exclusion of Protected Attributes**: Model feature sets explicitly exclude protected demographic and socioeconomic indicators such as caste, religion, native language, sexual orientation, disability status, or financial loan history.
- **Equal Opportunity Auditing**: Model training pipelines calculate false-positive rates (FPR) across departments and admission quotas to ensure equitable treatment and avoid disproportionate flagging of specific student demographics.

### 1.3 Explainability & Interpretability
- **No Black-Box Scoring**: Whenever an academic risk score or complaint priority is generated, the system computes and renders **top contributing factors** (e.g., "Downward quiz trend over past 3 weeks", "Classroom attendance below statutory 75% threshold").
- **Auditability**: All model inferences, version tags, and timestamps are recorded in `apps.academics.models.AcademicRiskAssessment` for longitudinal review.

---

## 2. Student Data Privacy & Access Controls

### 2.1 Role-Based Access Control (RBAC) Isolation
- **Peer Isolation**: Students can only view their own grades, attendance, risk status, and registered events. Student accounts have zero read or write access to peer records.
- **Departmental Firewalls**: Faculty and Department Heads (HODs) are scoped to their respective departments. An HOD in Mechanical Engineering cannot inspect or modify student grades in Computer Science.
- **Dean & Leadership Governance**: Deans and Campus Administrators receive aggregated, de-identified cohort analytics (e.g., department-wide pass percentages) rather than unnecessary individual private details.

### 2.2 Telemetry & Location Privacy
- **Campus Vehicle Tracking Only**: The GPS tracking subsystem (`apps/transport`) tracks institutional fleet buses and campus shuttles exclusively. The system does **not** track personal student smartphones, wearables, or private vehicles.
- **De-Identified Parking Bays**: Smart parking slots track bay occupancy (Occupied / Available) without logging private driver license plates or facial recognition data.

---

## 3. Data Retention & Deletion Rights

1. **Right to Rectification**: Students have the right to challenge incorrect attendance records or grade postings directly through the integrated grievance redressal portal (`apps/complaints`).
2. **Audit Logging**: All administrative edits, grade modifications, and role transitions are committed to `apps.common.models.AuditLog`, providing an immutable trace of data access and modifications.
3. **Data Portability**: Academic transcripts and semester performance reports can be exported to standard CSV / PDF formats upon graduation.
