from django.db import models
from django.conf import settings
from accounts.models import Category


class Service(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='services'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='services'
    )
    title = models.CharField(max_length=150)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text='Price in INR (₹)')
    delivery_time_days = models.PositiveIntegerField(default=2, help_text='Estimated completion time in days')
    image = models.ImageField(upload_to='services/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} (₹{self.price}) by {self.student.username}"

    def get_display_image(self):
        if self.image:
            return self.image.url
        # Fallback to category or student profile
        return None
