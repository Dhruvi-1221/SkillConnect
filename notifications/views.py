from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Notification


@login_required
def notification_list_view(request):
    notifications = Notification.objects.filter(recipient=request.user).select_related('sender').order_by('-created_at')
    return render(request, 'notifications/notification_list.html', {
        'notifications': notifications,
    })


@login_required
def mark_all_read_view(request):
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    messages.success(request, "All notifications marked as read.")
    return redirect('notifications')


@login_required
def read_notification_view(request, notification_id):
    notif = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notif.is_read = True
    notif.save()
    if notif.link:
        return redirect(notif.link)
    return redirect('notifications')
