import json
from datetime import timedelta
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Complaint, ComplaintStatusHistory
from ml.complaints.predict import ComplaintAITriage

@login_required
def complaint_list(request):
    """
    List complaints submitted by current user (if student), or all complaints if staff/admin.
    """
    if request.user.is_superuser or request.user.role in ['SUPER_ADMIN', 'COLLEGE_ADMIN', 'MAINTENANCE_STAFF', 'FACILITY_MANAGER']:
        complaints = Complaint.objects.select_related('user', 'assigned_to').all()
    else:
        complaints = Complaint.objects.filter(user=request.user)

    cat = request.GET.get('cat')
    status = request.GET.get('status')
    if cat:
        complaints = complaints.filter(category=cat)
    if status:
        complaints = complaints.filter(status=status)

    paginator = Paginator(complaints, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'complaints/list.html', {
        'page_obj': page_obj,
        'categories': Complaint.Category.choices,
        'statuses': Complaint.Status.choices,
        'selected_cat': cat,
        'selected_status': status
    })

@login_required
def submit_complaint(request):
    """
    Natural Language Complaint Submission.
    Runs real-time AI triage extracting category, priority, department, and location.
    """
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')

        # Run AI Triage
        triage = ComplaintAITriage.triage_complaint(f"{title}. {description}")

        complaint = Complaint.objects.create(
            user=request.user,
            title=title,
            description=description,
            category=triage['category'],
            priority=triage['priority'],
            target_department=triage['target_department'],
            location_extracted=triage['location_extracted'],
            confidence=triage['confidence'],
            sla_hours=triage['sla_hours'],
            status=Complaint.Status.SUBMITTED
        )

        ComplaintStatusHistory.objects.create(
            complaint=complaint,
            status=Complaint.Status.SUBMITTED,
            updated_by=request.user,
            comments=f"AI auto-triaged to {triage['target_department']} with {triage['priority']} priority (Confidence: {triage['confidence']*100:.0f}%)."
        )

        messages.success(
            request,
            f"Complaint registered! AI classified as '{complaint.get_category_display()}' with '{complaint.get_priority_display()}' priority routed to {complaint.target_department}."
        )
        return redirect('complaints:detail', pk=complaint.pk)

    return render(request, 'complaints/submit.html')

@login_required
def complaint_detail(request, pk):
    complaint = get_object_or_404(Complaint.objects.select_related('user', 'assigned_to'), pk=pk)
    history = complaint.history.select_related('updated_by').all()
    return render(request, 'complaints/detail.html', {'complaint': complaint, 'history': history})

@login_required
def complaint_dashboard(request):
    """
    Facility & Maintenance Command Center:
    Workload distribution, open complaints, overdue alerts, and category heatmap.
    """
    all_complaints = Complaint.objects.all()
    total = all_complaints.count()
    open_count = all_complaints.exclude(status__in=['RESOLVED', 'REJECTED']).count()
    resolved_count = all_complaints.filter(status='RESOLVED').count()
    urgent_count = all_complaints.filter(priority='URGENT').exclude(status='RESOLVED').count()

    # Category breakdown
    from django.db.models import Count
    category_breakdown = list(all_complaints.values('category').annotate(count=Count('id')).order_by('-count'))

    recent_complaints = all_complaints.select_related('user')[:10]

    return render(request, 'complaints/dashboard.html', {
        'total': total,
        'open_count': open_count,
        'resolved_count': resolved_count,
        'urgent_count': urgent_count,
        'category_breakdown': category_breakdown,
        'recent_complaints': recent_complaints,
    })

@login_required
def update_complaint_status(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        notes = request.POST.get('notes', '')

        complaint.status = new_status
        if new_status == 'RESOLVED':
            complaint.resolved_at = timezone.now()
            complaint.resolution_notes = notes
        complaint.save()

        ComplaintStatusHistory.objects.create(
            complaint=complaint,
            status=new_status,
            updated_by=request.user,
            comments=notes
        )

        messages.success(request, f"Complaint status updated to {complaint.get_status_display()}.")
        return redirect('complaints:detail', pk=complaint.pk)

    return redirect('complaints:detail', pk=complaint.pk)


def escalate_overdue_complaints():
    """
    Automated Priority Escalation Engine.
    Scans active tickets against their SLA deadlines.
    Escalates priority, registers audit history, and alerts facility managers.
    """
    now = timezone.now()
    open_complaints = Complaint.objects.exclude(status__in=[Complaint.Status.RESOLVED, Complaint.Status.REJECTED])
    
    escalated_count = 0
    priority_order = [Complaint.Priority.LOW, Complaint.Priority.MEDIUM, Complaint.Priority.HIGH, Complaint.Priority.URGENT]
    
    for c in open_complaints:
        deadline = c.created_at + timedelta(hours=c.sla_hours)
        if now > deadline:
            old_priority = c.priority
            current_idx = priority_order.index(c.priority) if c.priority in priority_order else 1
            if current_idx < len(priority_order) - 1:
                new_priority = priority_order[current_idx + 1]
                c.priority = new_priority
                c.save()
                
                hours_overdue = max(1, int((now - deadline).total_seconds() // 3600))
                ComplaintStatusHistory.objects.create(
                    complaint=c,
                    status=c.status,
                    updated_by=None,
                    comments=f"AI Auto-Escalation: SLA exceeded by {hours_overdue}h. Priority elevated from {old_priority} to {new_priority}."
                )
                
                # Send high-priority notification to maintenance staff & admins
                from apps.accounts.models import User
                from apps.notifications.models import Notification
                admin_users = User.objects.filter(role__in=['SUPER_ADMIN', 'COLLEGE_ADMIN', 'FACILITY_MANAGER', 'MAINTENANCE_STAFF'])[:10]
                for admin in admin_users:
                    Notification.objects.create(
                        user=admin,
                        title=f"🚨 Ticket Auto-Escalated: CMP-{c.id:04d}",
                        message=f"{c.title} ({c.target_department}) breached SLA. Elevated to {new_priority}.",
                        category=Notification.Category.COMPLAINT_UPDATE
                    )
                escalated_count += 1
                
    return escalated_count


def api_triage_preview(request):
    """
    Real-time NLP Triage API preview for interactive complaint typing.
    Returns predicted category, department routing, extracted location, confidence, and SLA hours.
    """
    text = request.GET.get('text') or request.POST.get('text') or ''
    if not text.strip():
        return JsonResponse({'status': 'empty', 'message': 'No text provided'})

    triage = ComplaintAITriage.triage_complaint(text, user=request.user)
    return JsonResponse({
        'status': 'success',
        'category': triage.get('category'),
        'category_display': dict(Complaint.Category.choices).get(triage.get('category'), triage.get('category')),
        'priority': triage.get('priority'),
        'target_department': triage.get('target_department'),
        'location_extracted': triage.get('location_extracted'),
        'confidence': triage.get('confidence'),
        'sla_hours': triage.get('sla_hours'),
    })


@login_required
def api_escalate_complaints(request):
    """Manual or scheduled trigger for the AI priority escalation engine."""
    count = escalate_overdue_complaints()
    return JsonResponse({
        'status': 'success',
        'message': f"Evaluated open complaints. {count} ticket(s) escalated due to SLA expiration.",
        'escalated_count': count
    })

