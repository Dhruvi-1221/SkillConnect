from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from .models import Review
from .forms import ReviewForm
from orders.models import Order
from notifications.models import Notification


@login_required
def create_review_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    # Permission check: must be customer of this order and order must be completed
    if order.customer != request.user:
        return HttpResponseForbidden("Only the customer who placed this order can write a review.")

    if order.status != 'COMPLETED':
        messages.error(request, "You can only submit a review after the order has been completed.")
        return redirect('order_detail', order_id=order.id)

    if hasattr(order, 'review'):
        messages.info(request, "You have already submitted a review for this order.")
        return redirect('order_detail', order_id=order.id)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.order = order
            review.customer = request.user
            review.student = order.student
            review.save()

            Notification.send(
                recipient=order.student,
                sender=request.user,
                notification_type='REVIEW',
                title='New Review Received',
                message=f"{request.user.get_display_name()} left a {review.rating}★ review for order #{order.order_number}.",
                link=f"/profile/{order.student.username}/"
            )

            messages.success(request, "Thank you! Your rating and review have been published.")
            return redirect('order_detail', order_id=order.id)
    else:
        form = ReviewForm()

    return render(request, 'reviews/create_review.html', {
        'order': order,
        'form': form,
    })
