import uuid
from django.db import models
from django.conf import settings
from services.models import Service


class Order(models.Model):
    STATUS_CHOICES = (
        ('REQUESTED', 'Requested'),
        ('ACCEPTED', 'Accepted'),
        ('IN_PROGRESS', 'In Progress'),
        ('READY', 'Ready'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('REJECTED', 'Rejected'),
    )

    order_number = models.CharField(max_length=20, unique=True, editable=False)
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='customer_orders'
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_orders'
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.SET_NULL,
        null=True,
        related_name='orders'
    )
    requirements = models.TextField(help_text='Describe what you need done in detail')
    preferred_date = models.DateField(null=True, blank=True, help_text='Preferred delivery or event date')
    additional_message = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text='Order amount in INR (₹)')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='REQUESTED')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.order_number} - {self.service.title if self.service else 'Custom Service'} ({self.status})"

    def can_transition_to(self, new_status, user):
        """Validates allowable status transitions based on user role."""
        if self.status in ['COMPLETED', 'CANCELLED', 'REJECTED']:
            return False  # Terminal states
        
        # Student actions
        if user == self.student:
            valid_from = {
                'REQUESTED': ['ACCEPTED', 'REJECTED'],
                'ACCEPTED': ['IN_PROGRESS', 'CANCELLED'],
                'IN_PROGRESS': ['READY', 'CANCELLED'],
                'READY': ['COMPLETED'],
            }
            return new_status in valid_from.get(self.status, [])
        
        # Customer actions
        if user == self.customer:
            valid_from = {
                'REQUESTED': ['CANCELLED'],
                'READY': ['COMPLETED'],  # Customer can confirm completion
            }
            return new_status in valid_from.get(self.status, [])
        
        if user.is_staff or getattr(user, 'is_platform_admin', False):
            return True
            
        return False


class OrderStatusHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=20, choices=Order.STATUS_CHOICES)
    note = models.CharField(max_length=255, blank=True)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.order.order_number} -> {self.status} at {self.created_at.strftime('%Y-%m-%d %H:%M')}"
