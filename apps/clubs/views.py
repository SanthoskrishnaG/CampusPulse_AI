from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Club, ClubMembership, ClubAnnouncement, ClubAchievement
from apps.students.models import Student

def club_list(request):
    clubs = Club.objects.filter(is_active=True).prefetch_related('memberships')
    cat = request.GET.get('category')
    if cat:
        clubs = clubs.filter(category=cat)
    return render(request, 'clubs/list.html', {'clubs': clubs, 'selected_cat': cat})

def club_detail(request, code):
    club = get_object_or_404(Club.objects.prefetch_related('memberships', 'announcements', 'achievements'), code=code)
    is_member = False
    if request.user.is_authenticated and hasattr(request.user, 'student_profile'):
        is_member = ClubMembership.objects.filter(club=club, student=request.user.student_profile).exists()

    return render(request, 'clubs/detail.html', {
        'club': club,
        'is_member': is_member,
        'announcements': club.announcements.all()[:5],
        'achievements': club.achievements.all()[:5],
    })

@login_required
def join_club(request, code):
    club = get_object_or_404(Club, code=code)
    student = getattr(request.user, 'student_profile', None)
    if not student:
        messages.error(request, "Only students can join campus clubs.")
        return redirect('clubs:detail', code=code)

    membership, created = ClubMembership.objects.get_or_create(club=club, student=student)
    if created:
        messages.success(request, f"You have successfully enrolled in {club.name}!")
    else:
        messages.info(request, f"You are already a member of {club.name}.")
    return redirect('clubs:detail', code=code)

@login_required
def club_dashboard(request):
    """
    Club Administration Portal: manage events, memberships, and announcements.
    """
    clubs = Club.objects.filter(is_active=True)
    selected_code = request.GET.get('club')
    current_club = clubs.filter(code=selected_code).first() if selected_code else clubs.first()

    members = []
    announcements = []
    achievements = []
    if current_club:
        members = ClubMembership.objects.filter(club=current_club).select_related('student', 'student__user')[:20]
        announcements = current_club.announcements.all()[:5]
        achievements = current_club.achievements.all()[:5]

    return render(request, 'clubs/dashboard.html', {
        'clubs': clubs,
        'current_club': current_club,
        'members': members,
        'announcements': announcements,
        'achievements': achievements,
    })
