import uuid
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Event, EventRegistration, EventFeedback, Certificate
from apps.students.models import Student
from apps.departments.models import Department
from apps.clubs.models import Club
from ml.events.predict import EventAttendancePredictor

def event_list(request):
    events = Event.objects.select_related('department', 'club').all()
    q = request.GET.get('q')
    event_type = request.GET.get('type')
    dept = request.GET.get('dept')

    if q:
        events = events.filter(title__icontains=q) | events.filter(description__icontains=q)
    if event_type:
        events = events.filter(event_type=event_type)
    if dept:
        events = events.filter(department__code=dept)

    return render(request, 'events/list.html', {
        'events': events,
        'selected_type': event_type,
        'selected_dept': dept,
        'event_types': Event.EventType.choices,
    })

def event_detail(request, pk):
    event = get_object_or_404(Event.objects.select_related('department', 'club'), pk=pk)
    is_registered = False
    user_registration = None

    if request.user.is_authenticated and hasattr(request.user, 'student_profile'):
        user_registration = EventRegistration.objects.filter(event=event, student=request.user.student_profile).first()
        is_registered = user_registration is not None

    # Get ML prediction
    prediction = EventAttendancePredictor.predict_attendance(event)

    feedbacks = event.feedbacks.select_related('student')[:10]

    return render(request, 'events/detail.html', {
        'event': event,
        'is_registered': is_registered,
        'user_registration': user_registration,
        'prediction': prediction,
        'feedbacks': feedbacks,
    })

@login_required
def event_register(request, pk):
    event = get_object_or_404(Event, pk=pk)
    student = getattr(request.user, 'student_profile', None)
    if not student:
        messages.error(request, "Only students can register for events.")
        return redirect('events:detail', pk=pk)

    if not event.is_registration_open():
        messages.warning(request, "Registrations for this event are currently closed.")
        return redirect('events:detail', pk=pk)

    reg, created = EventRegistration.objects.get_or_create(event=event, student=student)
    if created:
        messages.success(request, f"You are registered for '{event.title}'! Your entry pass is ready.")
        # Create notification
        from apps.notifications.models import Notification
        Notification.objects.create(
            user=request.user,  
            title="Event Registration Confirmed",
            message=f"You are registered for {event.title} on {event.start_time.strftime('%b %d, %H:%M')}.",
            category=Notification.Category.EVENT_REMINDER
        )
    else:
        messages.info(request, "You are already registered for this event.")
    return redirect('events:detail', pk=pk)

@login_required
def event_checkin(request, qr_token):
    """
    QR-based event check-in validation endpoint.
    """
    reg = get_object_or_404(EventRegistration.objects.select_related('student', 'event'), qr_token=qr_token)
    reg.attended = True
    reg.attended_at = timezone.now()
    reg.save()

    # Generate certificate upon attendance
    Certificate.objects.get_or_create(
        event=reg.event,
        student=reg.student,
        defaults={'certificate_id': f"CERT-{reg.event.id}-{reg.student.student_id}-{uuid.uuid4().hex[:6].upper()}"}
    )

    messages.success(request, f"Attendance marked for {reg.student.get_display_name()} for event '{reg.event.title}'!")
    return redirect('events:detail', pk=reg.event.id)
