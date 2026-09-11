import numpy as np
import pandas as pd

FEATURE_NAMES = [
    'attendance_percentage',
    'cgpa',
    'internal_marks',
    'backlog_count',
    'semester',
    'quiz_avg',
    'assignment_avg',
    'lms_hours_avg',
    'trend_slope'
]

def extract_student_features(student):
    """
    Extracts numerical feature vector for a student entity from database models.
    """
    # Calculate averages from weekly performance records
    weekly = list(student.weekly_records.order_by('week_number'))
    if weekly:
        quiz_avg = np.mean([w.quiz_score for w in weekly])
        assignment_avg = np.mean([w.assignment_score for w in weekly])
        lms_avg = np.mean([w.lms_activity_hours for w in weekly])
        # Performance trend slope over time
        if len(weekly) > 1:
            weeks = np.array([w.week_number for w in weekly])
            scores = np.array([w.quiz_score for w in weekly])
            slope = np.polyfit(weeks, scores, 1)[0]
        else:
            slope = 0.0
    else:
        quiz_avg = 75.0
        assignment_avg = 75.0
        lms_avg = 4.0
        slope = 0.0

    # Calculate average internal marks from course enrollments
    enrollments = list(student.enrollments.all())
    if enrollments:
        internal_marks_avg = np.mean([e.internal_marks for e in enrollments])
    else:
        internal_marks_avg = student.cgpa * 9.5

    return [
        float(student.attendance_percentage),
        float(student.cgpa),
        float(internal_marks_avg),
        float(student.backlog_count),
        float(student.semester),
        float(quiz_avg),
        float(assignment_avg),
        float(lms_avg),
        float(slope)
    ]
