from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from .models import Order, OrderStatusHistory
from .forms import OrderBookingForm
from services.models import Service
from notifications.models import Notification
from chat.models import Conversation


@login_required
def book_service_view(request, service_id):
    service = get_object_or_404(
        Service.objects.select_related('student', 'student__profile', 'student__student_profile'),
        id=service_id,
        is_active=True
    )

    if service.student == request.user:
        messages.warning(request, "You cannot book your own service.")
        return redirect('service_detail', service_id=service.id)

    if request.method == 'POST':
        form = OrderBookingForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.customer = request.user
            order.student = service.student
            order.service = service
            order.price = service.price
            order.status = 'REQUESTED'
            order.save()

            # Record initial history
            OrderStatusHistory.objects.create(
                order=order,
                status='REQUESTED',
                note='Order requested by customer',
                changed_by=request.user
            )

            # Send Notification to Student
            Notification.send(
                recipient=order.student,
                sender=request.user,
                notification_type='ORDER_REQUEST',
                title=f'New Order: {service.title}',
                message=f"{request.user.get_display_name()} requested your service '{service.title}' (₹{service.price}).",
                link=f"/orders/{order.id}/"
            )

            # Auto create/fetch conversation for direct communication
            Conversation.get_or_create_conversation(request.user, order.student)

            messages.success(request, f"Order #{order.order_number} successfully placed! The student will review your request.")
            return redirect('order_detail', order_id=order.id)
    else:
        form = OrderBookingForm()

    return render(request, 'orders/book_service.html', {
        'service': service,
        'form': form,
    })


@login_required
def order_list_view(request):
    tab = request.GET.get('tab', 'all')  # all, customer, student
    status_filter = request.GET.get('status', '')

    orders_as_customer = Order.objects.filter(customer=request.user).select_related('student', 'service')
    orders_as_student = Order.objects.filter(student=request.user).select_related('customer', 'service')

    if status_filter:
        orders_as_customer = orders_as_customer.filter(status=status_filter)
        orders_as_student = orders_as_student.filter(status=status_filter)

    return render(request, 'orders/order_list.html', {
        'orders_as_customer': orders_as_customer,
        'orders_as_student': orders_as_student,
        'tab': tab,
        'status_filter': status_filter,
        'status_choices': Order.STATUS_CHOICES,
    })


@login_required
def order_detail_view(request, order_id):
    order = get_object_or_404(
        Order.objects.select_related(
            'customer', 'customer__profile',
            'student', 'student__profile', 'student__student_profile',
            'service'
        ).prefetch_related('status_history', 'status_history__changed_by'),
        id=order_id
    )

    # Permission check: must be customer, student, or admin
    if order.customer != request.user and order.student != request.user and not request.user.is_platform_admin:
        return HttpResponseForbidden("You are not authorized to view this order.")

    # Status tracking step calculation
    # Steps: 1: REQUESTED, 2: ACCEPTED, 3: IN_PROGRESS, 4: READY, 5: COMPLETED
    step_order = ['REQUESTED', 'ACCEPTED', 'IN_PROGRESS', 'READY', 'COMPLETED']
    current_step = 0
    if order.status in step_order:
        current_step = step_order.index(order.status) + 1
    elif order.status in ['CANCELLED', 'REJECTED']:
        current_step = -1

    # Check review existence
    has_review = hasattr(order, 'review')
    review = getattr(order, 'review', None)

    # Find conversation
    other_user = order.student if request.user == order.customer else order.customer
    conv, _ = Conversation.get_or_create_conversation(request.user, other_user)

    return render(request, 'orders/order_detail.html', {
        'order': order,
        'current_step': current_step,
        'has_review': has_review,
        'review': review,
        'conversation': conv,
        'is_customer': (request.user == order.customer),
        'is_student': (request.user == order.student),
    })


@login_required
def update_order_status_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if order.customer != request.user and order.student != request.user and not request.user.is_platform_admin:
        return HttpResponseForbidden("Not authorized.")

    if request.method == 'POST':
        new_status = request.POST.get('status')
        note = request.POST.get('note', '')

        if not order.can_transition_to(new_status, request.user):
            messages.error(request, f"Cannot update order status to '{new_status}' at this time.")
            return redirect('order_detail', order_id=order.id)

        old_status = order.status
        order.status = new_status
        order.save()

        # Record history
        OrderStatusHistory.objects.create(
            order=order,
            status=new_status,
            note=note or f"Status changed from {old_status} to {new_status}",
            changed_by=request.user
        )

        # Notify other party
        recipient = order.customer if request.user == order.student else order.student
        
        status_labels = dict(Order.STATUS_CHOICES)
        Notification.send(
            recipient=recipient,
            sender=request.user,
            notification_type='ORDER_STATUS',
            title=f"Order #{order.order_number} Update",
            message=f"Order status changed to {status_labels.get(new_status, new_status)}.",
            link=f"/orders/{order.id}/"
        )

        messages.success(request, f"Order status updated to {status_labels.get(new_status, new_status)}.")

    return redirect('order_detail', order_id=order.id)
