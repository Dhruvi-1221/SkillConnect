from django.db import models
from django.conf import settings
from orders.models import Order


class Review(models.Model):
    RATING_CHOICES = (
        (1, '★☆☆☆☆ (1/5 Poor)'),
        (2, '★★☆☆☆ (2/5 Fair)'),
        (3, '★★★☆☆ (3/5 Good)'),
        (4, '★★★★☆ (4/5 Very Good)'),
        (5, '★★★★★ (5/5 Excellent)'),
    )

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='review'
    )
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='given_reviews'
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_reviews'
    )
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.rating}★ Review by {self.customer.username} for {self.student.username} (Order #{self.order.order_number})"
