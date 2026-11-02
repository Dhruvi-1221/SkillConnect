from django.db import models
from django.conf import settings


class Notification(models.Model):
    TYPE_CHOICES = (
        ('ORDER_REQUEST', 'New Order Request'),
        ('ORDER_ACCEPTED', 'Order Accepted'),
        ('ORDER_REJECTED', 'Order Rejected'),
        ('ORDER_STATUS', 'Order Status Update'),
        ('MESSAGE', 'New Message'),
        ('FOLLOW', 'New Follower'),
        ('COMMENT', 'New Comment'),
        ('LIKE', 'New Post Like'),
        ('VERIFICATION', 'Student Verification Update'),
        ('REVIEW', 'New Review Received'),
    )

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='triggered_notifications'
    )
    notification_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    title = models.CharField(max_length=150)
    message = models.TextField()
    link = models.CharField(max_length=255, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.recipient.username}: {self.title}"

    @classmethod
    def send(cls, recipient, notification_type, title, message, sender=None, link=''):
        """Convenience helper to dispatch notifications cleanly."""
        if recipient == sender:
            return None
        return cls.objects.create(
            recipient=recipient,
            sender=sender,
            notification_type=notification_type,
            title=title,
            message=message,
            link=link
        )
