"""
Strict Data Validation Utilities for CampusPulse AI ML Pipelines.
Enforces schema validity, missing value detection, range constraints,
and prevents target / temporal leakage.
"""

def validate_academic_features(data: dict) -> dict:
    required = [
        'attendance_percentage', 'cgpa', 'internal_marks',
        'backlog_count', 'semester', 'quiz_avg',
        'assignment_avg', 'lms_hours_avg', 'trend_slope'
    ]
    missing = [f for f in required if f not in data or data[f] is None]
    if missing:
        raise ValueError(f"Missing required academic features: {', '.join(missing)}")

    # Range & Type validations
    att = float(data['attendance_percentage'])
    if not (0.0 <= att <= 100.0):
        raise ValueError(f"Attendance percentage must be between 0 and 100. Received: {att}")

    cgpa = float(data['cgpa'])
    if not (0.0 <= cgpa <= 10.0):
        raise ValueError(f"CGPA must be between 0.0 and 10.0. Received: {cgpa}")

    marks = float(data['internal_marks'])
    if not (0.0 <= marks <= 100.0):
        raise ValueError(f"Internal marks must be between 0 and 100. Received: {marks}")

    backlogs = int(data['backlog_count'])
    if backlogs < 0:
        raise ValueError(f"Backlog count cannot be negative. Received: {backlogs}")

    sem = int(data['semester'])
    if not (1 <= sem <= 10):
        raise ValueError(f"Semester must be between 1 and 10. Received: {sem}")

    quiz = float(data['quiz_avg'])
    if not (0.0 <= quiz <= 100.0):
        raise ValueError(f"Quiz average must be between 0 and 100. Received: {quiz}")

    assignment = float(data['assignment_avg'])
    if not (0.0 <= assignment <= 100.0):
        raise ValueError(f"Assignment average must be between 0 and 100. Received: {assignment}")

    lms = float(data['lms_hours_avg'])
    if lms < 0:
        raise ValueError(f"LMS hours cannot be negative. Received: {lms}")

    slope = float(data['trend_slope'])

    return {
        'attendance_percentage': att,
        'cgpa': cgpa,
        'internal_marks': marks,
        'backlog_count': backlogs,
        'semester': sem,
        'quiz_avg': quiz,
        'assignment_avg': assignment,
        'lms_hours_avg': lms,
        'trend_slope': slope
    }


def validate_canteen_features(data: dict) -> dict:
    required = ['day_of_week', 'meal_type', 'is_event', 'is_weekend', 'student_base']
    missing = [f for f in required if f not in data or data[f] is None]
    if missing:
        raise ValueError(f"Missing required canteen demand features: {', '.join(missing)}")

    dow = int(data['day_of_week'])
    if not (0 <= dow <= 6):
        raise ValueError(f"Day of week must be 0 (Mon) to 6 (Sun). Received: {dow}")

    meal_type = str(data['meal_type']).upper().strip()
    valid_meals = ['BREAKFAST', 'LUNCH', 'SNACKS', 'DINNER']
    if meal_type not in valid_meals:
        raise ValueError(f"Meal type must be one of {valid_meals}. Received: '{meal_type}'")

    is_event = int(bool(data['is_event']))
    is_weekend = int(bool(data['is_weekend']))
    base = int(data['student_base'])
    if base <= 0:
        raise ValueError(f"Student base must be positive. Received: {base}")

    return {
        'day_of_week': dow,
        'meal_type': meal_type,
        'is_event': is_event,
        'is_weekend': is_weekend,
        'student_base': base
    }


def validate_food_waste_features(data: dict) -> dict:
    required = ['meals_prepared', 'predicted_demand', 'meal_type', 'day_of_week', 'is_event']
    missing = [f for f in required if f not in data or data[f] is None]
    if missing:
        raise ValueError(f"Missing required food waste features: {', '.join(missing)}")

    prepared = int(data['meals_prepared'])
    demand = int(data['predicted_demand'])
    if prepared <= 0:
        raise ValueError(f"Meals prepared must be positive. Received: {prepared}")
    if demand <= 0:
        raise ValueError(f"Predicted demand must be positive. Received: {demand}")

    dow = int(data['day_of_week'])
    if not (0 <= dow <= 6):
        raise ValueError(f"Day of week must be 0 to 6. Received: {dow}")

    meal_type = str(data['meal_type']).upper().strip()

    return {
        'meals_prepared': prepared,
        'predicted_demand': demand,
        'meal_type': meal_type,
        'day_of_week': dow,
        'is_event': int(bool(data['is_event'])),
    }


def validate_complaint_text(text: str) -> str:
    if not text or not isinstance(text, str):
        raise ValueError("Complaint text must be a non-empty string.")
    cleaned = text.strip()
    if len(cleaned) < 5:
        raise ValueError("Complaint text must be at least 5 characters long for reliable classification.")
    return cleaned


def validate_energy_features(data: dict) -> dict:
    required = ['hour', 'is_weekend', 'occupancy', 'kwh_consumed']
    missing = [f for f in required if f not in data or data[f] is None]
    if missing:
        raise ValueError(f"Missing required energy features: {', '.join(missing)}")

    hour = int(data['hour'])
    if not (0 <= hour <= 23):
        raise ValueError(f"Hour must be between 0 and 23. Received: {hour}")

    kwh = float(data['kwh_consumed'])
    if kwh < 0:
        raise ValueError(f"Energy consumed (kWh) cannot be negative. Received: {kwh}")

    occ = int(data['occupancy'])
    if occ < 0:
        raise ValueError(f"Occupancy cannot be negative. Received: {occ}")

    return {
        'hour': hour,
        'is_weekend': int(bool(data['is_weekend'])),
        'occupancy': occ,
        'kwh_consumed': kwh
    }


def validate_transport_features(data: dict) -> dict:
    required = ['distance_km', 'stop_sequence', 'is_peak_hour', 'passenger_count']
    missing = [f for f in required if f not in data or data[f] is None]
    if missing:
        raise ValueError(f"Missing required transport features: {', '.join(missing)}")

    dist = float(data['distance_km'])
    if dist <= 0:
        raise ValueError(f"Distance must be positive. Received: {dist}")

    stop_seq = int(data['stop_sequence'])
    if stop_seq < 1:
        raise ValueError(f"Stop sequence must be >= 1. Received: {stop_seq}")

    passengers = int(data['passenger_count'])
    if passengers < 0:
        raise ValueError(f"Passenger count cannot be negative. Received: {passengers}")

    return {
        'distance_km': dist,
        'stop_sequence': stop_seq,
        'is_peak_hour': int(bool(data['is_peak_hour'])),
        'passenger_count': passengers
    }


def validate_parking_features(data: dict) -> dict:
    required = ['total_slots', 'hour', 'day_of_week', 'is_event']
    missing = [f for f in required if f not in data or data[f] is None]
    if missing:
        raise ValueError(f"Missing required parking features: {', '.join(missing)}")

    total = int(data['total_slots'])
    if total <= 0:
        raise ValueError(f"Total slots must be positive. Received: {total}")

    hour = int(data['hour'])
    if not (0 <= hour <= 23):
        raise ValueError(f"Hour must be 0-23. Received: {hour}")

    dow = int(data['day_of_week'])
    if not (0 <= dow <= 6):
        raise ValueError(f"Day of week must be 0-6. Received: {dow}")

    return {
        'total_slots': total,
        'hour': hour,
        'day_of_week': dow,
        'is_event': int(bool(data['is_event']))
    }
