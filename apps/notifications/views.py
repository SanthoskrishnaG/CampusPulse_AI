import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import Notification

@login_required
@ensure_csrf_cookie
def notification_list(request):
    """
    In-app Notification Center: Displays real-time alerts across all campus modules
    for the currently authenticated user.
    Supports filtering by status ('all', 'unread', 'read') and category.
    """
    filter_type = request.GET.get('filter', 'all')
    category_filter = request.GET.get('category', '')

    user_notifications = Notification.objects.filter(user=request.user)
    
    total_count = user_notifications.count()
    unread_count = user_notifications.filter(is_read=False).count()
    read_count = user_notifications.filter(is_read=True).count()

    filtered_qs = user_notifications
    if filter_type == 'unread':
        filtered_qs = filtered_qs.filter(is_read=False)
    elif filter_type == 'read':
        filtered_qs = filtered_qs.filter(is_read=True)

    if category_filter:
        filtered_qs = filtered_qs.filter(category=category_filter)

    categories = Notification.Category.choices

    context = {
        'notifications': filtered_qs,
        'filter_type': filter_type,
        'selected_category': category_filter,
        'total_count': total_count,
        'unread_count': unread_count,
        'read_count': read_count,
        'categories': categories,
    }
    return render(request, 'notifications/list.html', context)

@login_required
def unread_count_api(request):
    """
    JSON API: Returns the current unread notifications count for the authenticated user.
    Single source of truth for the navbar and sidebar badges.
    """
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({
        'status': 'ok',
        'count': count,
        'user': request.user.username
    })

@login_required
def notification_list_api(request):
    """
    JSON API: Serialized list of notifications for the authenticated user.
    """
    filter_type = request.GET.get('filter', 'all')
    category_filter = request.GET.get('category', '')

    qs = Notification.objects.filter(user=request.user)
    if filter_type == 'unread':
        qs = qs.filter(is_read=False)
    elif filter_type == 'read':
        qs = qs.filter(is_read=True)

    if category_filter:
        qs = qs.filter(category=category_filter)

    data = [
        {
            'id': n.id,
            'title': n.title,
            'message': n.message,
            'category': n.category,
            'category_display': n.get_category_display(),
            'link_url': n.link_url,
            'is_read': n.is_read,
            'created_at': n.created_at.strftime('%b %d, %Y · %I:%M %p'),
        }
        for n in qs[:50]
    ]
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({
        'status': 'ok',
        'unread_count': unread_count,
        'notifications': data
    })

@login_required
def mark_notification_read(request, pk):
    """
    Marks an individual notification as read.
    Enforces user-level ownership check.
    Supports both JSON AJAX and HTTP redirect.
    """
    notif = get_object_or_404(Notification, pk=pk, user=request.user)
    if not notif.is_read:
        notif.is_read = True
        notif.save(update_fields=['is_read'])

    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()

    is_ajax = (
        request.headers.get('x-requested-with') == 'XMLHttpRequest' or
        request.headers.get('accept') == 'application/json' or
        request.content_type == 'application/json'
    )
    if is_ajax:
        return JsonResponse({
            'status': 'ok',
            'id': pk,
            'unread_count': unread_count,
            'message': 'Notification marked as read.'
        })

    if notif.link_url:
        return redirect(notif.link_url)
    return redirect('notifications:list')

@login_required
def mark_all_notifications_read(request):
    """
    Marks all notifications belonging to the authenticated user as read.
    Supports both JSON AJAX and HTTP redirect.
    """
    updated = Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    
    is_ajax = (
        request.headers.get('x-requested-with') == 'XMLHttpRequest' or
        request.headers.get('accept') == 'application/json' or
        request.content_type == 'application/json'
    )
    if is_ajax:
        return JsonResponse({
            'status': 'ok',
            'updated_count': updated,
            'unread_count': 0,
            'message': 'All notifications marked as read.'
        })

    messages.success(request, "All notifications marked as read.")
    return redirect('notifications:list')
