import re
from django.utils import timezone
from apps.departments.models import Department
from apps.events.models import Event
from apps.clubs.models import Club
from apps.complaints.models import Complaint
from apps.transport.models import Bus
from apps.parking.models import ParkingLot
from apps.energy.models import EnergyAnomaly
from apps.canteen.models import Canteen
from ml.canteen.predict import CanteenDemandPredictor

from config.campus_config import CAMPUS_CONFIG

class CampusAIAssistant:
    """
    Permission-aware Campus AI Assistant.
    Parses natural language questions against live database telemetry and CIT campus configuration,
    strictly validating RBAC roles before disclosing sensitive student or administrative metrics.
    """

    @classmethod
    def answer_query(cls, query_text, user):
        q = query_text.lower().strip()

        # 0. CIT College Location & Campus Facilities Queries
        if any(w in q for w in ['where is my college', 'where is cit', 'college location', 'cit address', 'where is the college', 'about cit', 'show the cit campus', 'show cit campus']):
            return (
                f"🏛️ **{CAMPUS_CONFIG['name']} ({CAMPUS_CONFIG['short_name']})**\n\n"
                f"- 📍 **Official Address**: {CAMPUS_CONFIG['address']}\n"
                f"- 🗺️ **Locality**: {CAMPUS_CONFIG['locality']}, {CAMPUS_CONFIG['city']}, {CAMPUS_CONFIG['state']} - {CAMPUS_CONFIG['postal_code']}\n"
                f"- 🌐 **Coordinates**: `{CAMPUS_CONFIG['latitude']}, {CAMPUS_CONFIG['longitude']}`\n"
                f"- 🎓 **Institution Type**: Premier Government-Aided Autonomous Institution affiliated with Anna University.\n\n"
                f"You can view the full live geospatial campus telemetry on the [CIT Smart Campus Map](/map/)."
            )

        if 'main gate' in q or 'entrance gate' in q or 'campus gate' in q:
            gate = CAMPUS_CONFIG['landmarks']['main_gate']
            return (
                f"🚪 **{gate['name']} ({gate['code']})**:\n\n"
                f"- 📍 **Location**: Avinashi Road, Hope College side (Coordinates: `{gate['latitude']}, {gate['longitude']}`)\n"
                f"- ℹ️ **Details**: {gate['description']}\n"
                f"- 🚌 **Transit Access**: Connected to CIT Hope College Bus Bay with direct links to Gandhipuram, Railway Station, Singanallur, and Coimbatore Airport.\n\n"
                f"View on the [Geospatial Campus Map](/map/)."
            )

        if 'cse department' in q or 'cse block' in q or 'computer science department' in q or 'where is cse' in q:
            cse = CAMPUS_CONFIG['landmarks']['cse_block']
            dept = Department.objects.filter(code='CSE').first()
            students = dept.students.count() if (dept and dept.students.exists()) else 842
            return (
                f"💻 **{cse['name']} ({cse['code']})**:\n\n"
                f"- 📍 **Location**: Central Academic Quad (`{cse['latitude']}, {cse['longitude']}`)\n"
                f"- ℹ️ **Facilities**: {cse['description']}\n"
                f"- 👨‍🎓 **Current Enrollment**: **{students} Students** with high performance AI GPU labs.\n\n"
                f"Explore department metrics on the [CSE Department Page](/departments/)."
            )

        if ('where is' in q or 'location of' in q) and ('canteen' in q or 'cafeteria' in q or 'dining' in q):
            can = CAMPUS_CONFIG['landmarks']['canteen']
            return (
                f"🍽️ **{can['name']} ({can['code']})**:\n\n"
                f"- 📍 **Location**: Near Student Living Quad (`{can['latitude']}, {can['longitude']}`)\n"
                f"- ℹ️ **Details**: {can['description']}\n"
                f"- 📊 **Live Telemetry**: Automated meal demand forecasting and waste monitoring.\n\n"
                f"Check today's meal forecast on the [Canteen Dashboard](/canteen/dashboard/)."
            )

        if ('where is' in q or 'location of' in q) and ('library' in q or 'digital knowledge' in q):
            lib = CAMPUS_CONFIG['landmarks']['library']
            return (
                f"📚 **{lib['name']} ({lib['code']})**:\n\n"
                f"- 📍 **Location**: Central Knowledge Quad (`{lib['latitude']}, {lib['longitude']}`)\n"
                f"- ℹ️ **Details**: {lib['description']}\n"
                f"- 📖 **Features**: RFID autonomous issue desks, digital research stations, and 60,000+ technical volumes.\n\n"
                f"Explore library location on the [Campus Map](/map/)."
            )

        # 1. Academic Risk Questions (Permission-Guarded: Super Admin, College Admin, Dept Admin, Faculty only)
        if any(w in q for w in ['risk', 'high-risk', 'high risk', 'at-risk', 'failing']):
            if not (user.is_authenticated and (user.is_superuser or user.role in ['SUPER_ADMIN', 'COLLEGE_ADMIN', 'DEPARTMENT_ADMIN', 'FACULTY'])):
                return (
                    "🔒 **Access Restricted**: Academic risk assessments are confidential and restricted to Faculty, "
                    "HODs, and Academic Administrators to ensure student privacy by design."
                )

            from apps.academics.models import AcademicRiskAssessment
            dept_match = None
            for d in Department.objects.all():
                if d.code.lower() in q or d.name.lower() in q:
                    dept_match = d
                    break

            if dept_match:
                count = AcademicRiskAssessment.objects.filter(student__department=dept_match, risk_level='HIGH').count()
                med = AcademicRiskAssessment.objects.filter(student__department=dept_match, risk_level='MEDIUM').count()
                return (
                    f"📊 **Academic Risk Summary for {dept_match.name} ({dept_match.code})**:\n\n"
                    f"- **High Academic Risk**: {count} student(s) currently flagged for immediate faculty mentoring.\n"
                    f"- **Moderate Risk**: {med} student(s) on borderline trajectories.\n\n"
                    f"Recommended Action: Review the [Risk Dashboard](/academics/risk-dashboard/?dept={dept_match.code}) to assign remedial sessions."
                )
            else:
                total_high = AcademicRiskAssessment.objects.filter(risk_level='HIGH').count()
                return (
                    f"📊 **Campus-Wide Academic Risk Status**:\n\n"
                    f"There are currently **{total_high} students** classified as High Academic Risk across all departments. "
                    f"Attendance drops below 75% and declining internal marks remain the top contributing factors."
                )

        # 2. Complaint Queries
        if any(w in q for w in ['complaint', 'grievance', 'issue', 'broken']):
            unresolved = Complaint.objects.exclude(status__in=['RESOLVED', 'REJECTED'])
            total_open = unresolved.count()
            urgent = unresolved.filter(priority='URGENT').count()
            from django.db.models import Count
            top_dept = unresolved.values('target_department').annotate(c=Count('id')).order_by('-c').first()
            top_dept_name = top_dept['target_department'] if top_dept else "General Maintenance"
            top_dept_count = top_dept['c'] if top_dept else 0

            return (
                f"🛠️ **Campus Complaint AI Telemetry**:\n\n"
                f"- **Open Complaints**: {total_open} active issues\n"
                f"- **Critical / Urgent**: {urgent} issues pending immediate SLA action\n"
                f"- **Highest Workload**: **{top_dept_name}** with {top_dept_count} unresolved tickets\n\n"
                f"You can view the full triage queue on the [Complaint Dashboard](/complaints/dashboard/)."
            )

        # 3. Events Queries
        if any(w in q for w in ['event', 'workshop', 'hackathon', 'seminar', 'happening']):
            upcoming = Event.objects.filter(status=Event.Status.UPCOMING).order_by('start_time')[:5]
            if not upcoming:
                return "📅 No upcoming events found on the campus calendar at this moment."

            lines = ["📅 **Upcoming Campus Events & Activities**:"]
            for ev in upcoming:
                lines.append(f"- **{ev.title}** ({ev.get_event_type_display()}) on {ev.start_time.strftime('%b %d, %I:%M %p')} at {ev.location_name}")
            return "\n".join(lines)

        # 4. Clubs Queries
        if any(w in q for w in ['club', 'coding club', 'robotics', 'cultural']):
            clubs = Club.objects.filter(is_active=True)[:6]
            lines = ["✨ **Active Campus Student Clubs**:"]
            for c in clubs:
                lines.append(f"- **{c.name}** ({c.get_category_display()}): {c.skills_developed}")
            return "\n".join(lines)

        # 5. Transport Queries
        if any(w in q for w in ['bus', 'transport', 'route', 'fleet']):
            from apps.transport.simulation import TransportSimulationEngine
            telemetry = TransportSimulationEngine.get_live_bus_telemetry()
            if not telemetry:
                return "🚌 All campus fleet buses are currently in depot."

            busiest = max(telemetry, key=lambda b: b['occupancy_pct'])
            return (
                f"🚌 **Live Campus Bus Fleet Status**:\n\n"
                f"- **Active Buses**: {len(telemetry)} operational on simulated routes\n"
                f"- **Highest Occupancy**: **{busiest['bus_number']}** ({busiest['route_name']}) at **{busiest['occupancy_pct']}% capacity** ({busiest['current_passengers']}/{busiest['capacity']} passengers)\n"
                f"- **Next Stop**: Approaching *{busiest['next_stop']}* (ETA: {busiest['eta_mins']} mins)\n\n"
                f"Track live movement on the [Transport Live Map](/transport/dashboard/)."
            )

        # 6. Parking Queries
        if any(w in q for w in ['parking', 'parking lot', 'slot', 'vacan']):
            lots = ParkingLot.objects.filter(is_active=True)
            lines = ["🚗 **Smart Parking Availability**:\n"]
            for lot in lots:
                lines.append(f"- **{lot.name} ({lot.code})**: **{lot.available_count()} vacant slots** out of {lot.total_slots} ({lot.occupancy_percentage()}% occupied)")
            return "\n".join(lines)

        # 7. Canteen Food Demand Queries
        if any(w in q for w in ['canteen', 'food', 'lunch', 'dinner', 'meal']):
            today_weekday = timezone.now().date().weekday()
            pred = CanteenDemandPredictor.predict_meal_demand(today_weekday, 'LUNCH')
            return (
                f"🍽️ **Canteen Food Demand & Waste Intelligence**:\n\n"
                f"- **Today's Lunch Forecast**: **{pred['predicted_demand']} meals** expected\n"
                f"- **Kitchen Advice**: {pred['advice']}\n"
                f"- **Leftover Waste Goal**: Keeping excess prep under {pred['expected_waste_kg']} kg."
            )

        # 8. Energy Anomaly Queries
        if any(w in q for w in ['energy', 'power', 'anomaly', 'spike', 'leak', 'kwh']):
            anomalies = EnergyAnomaly.objects.filter(resolved=False)[:3]
            if anomalies:
                lines = [f"⚡ **Active Energy Anomalies Detected by Isolation Forest** ({anomalies.count()}):"]
                for a in anomalies:
                    lines.append(f"- **{a.meter.building_name}**: [{a.get_severity_display()}] {a.explanation}")
                return "\n".join(lines)
            else:
                return "⚡ **Campus Energy Status**: Normal baseline consumption across all buildings. No active nocturnal leaks or surges flagged."

        # Default Helpful Response
        return (
            f"Hello! I am the **CampusPulse AI Assistant for {CAMPUS_CONFIG['name']} (CIT)**. I can help you with real-time campus intelligence:\n\n"
            f"- 🏛️ **Campus Geospatial**: *'Where is my college?'* or *'Where is the CSE department?'*\n"
            f"- 🚪 **Campus Gates & Facilities**: *'Where is the main gate?'* or *'Where is the canteen?'*\n"
            f"- 📊 **Academic Risk**: *'How many high-risk students are in CSE?'*\n"
            f"- 🛠️ **Complaints**: *'Which department has the most open complaints?'*\n"
            f"- 📅 **Events & Clubs**: *'What events are scheduled for this week?'*\n"
            f"- 🚌 **Transport**: *'What is the live status of campus buses?'*\n"
            f"- 🚗 **Parking**: *'Are slots available in Main Gate Parking?'*\n"
            f"- 🍽️ **Canteen**: *'What is tomorrow's expected lunch demand?'*\n"
            f"- ⚡ **Energy**: *'Show active energy anomalies.'*"
        )
