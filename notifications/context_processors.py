def notification_context(request):
    """Provides unread notification count across all views."""
    if not request.user.is_authenticated:
        return {'unread_notifications_count': 0}
    try:
        from notifications.models import Notification
        count = Notification.objects.filter(recipient=request.user, is_read=False).count()
        return {'unread_notifications_count': count}
    except Exception:
        return {'unread_notifications_count': 0}
