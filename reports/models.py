from django.db import models
from django.conf import settings


class Report(models.Model):
    TARGET_TYPE_CHOICES = (
        ('USER', 'User Profile'),
        ('POST', 'Student Post'),
        ('COMMENT', 'Comment'),
        ('SERVICE', 'Service Listing'),
    )

    REASON_CHOICES = (
        ('SPAM', 'Spam / Commercial advertising'),
        ('INAPPROPRIATE', 'Inappropriate or offensive content'),
        ('FAKE_ACCOUNT', 'Fake college credentials / Impersonation'),
        ('HARASSMENT', 'Harassment or abusive behavior'),
        ('FRAUD', 'Fraud or misleading service'),
        ('OTHER', 'Other issue'),
    )

    STATUS_CHOICES = (
        ('PENDING', 'Pending Review'),
        ('INVESTIGATING', 'Under Investigation'),
        ('RESOLVED', 'Resolved (Action Taken)'),
        ('DISMISSED', 'Dismissed (No Violation)'),
    )

    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='submitted_reports'
    )
    target_type = models.CharField(max_length=20, choices=TARGET_TYPE_CHOICES)
    target_id = models.PositiveIntegerField(help_text='ID of the reported object')
    reason = models.CharField(max_length=30, choices=REASON_CHOICES)
    details = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    admin_notes = models.TextField(blank=True)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_reports'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Report #{self.id} on {self.target_type} #{self.target_id} ({self.get_reason_display()})"
