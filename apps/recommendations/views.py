from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .engine import RecommendationEngine
from apps.students.models import Student

@login_required
def recommendation_hub(request):
    """
    Dedicated AI recommendation hub displaying personalized suggestions
    for Clubs, Events, Innovation Projects, and Complementary Teammates.
    """
    student = getattr(request.user, 'student_profile', None)
    if not student:
        student = Student.objects.first()

    clubs = RecommendationEngine.recommend_clubs_for_student(student, limit=6)
    events = RecommendationEngine.recommend_events_for_student(student, limit=6)
    teammates = RecommendationEngine.recommend_teammates_for_student(student, limit=6)

    context = {
        'student': student,
        'recommended_clubs': clubs,
        'recommended_events': events,
        'recommended_teammates': teammates,
    }
    return render(request, 'recommendations/hub.html', context)
