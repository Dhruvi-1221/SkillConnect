from functools import wraps
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.db.models import Count, Sum, Q
from django.utils import timezone
from accounts.models import User, StudentProfile, Category, Skill
from posts.models import Post, Comment
from services.models import Service
from orders.models import Order
from reports.models import Report
from notifications.models import Notification


def admin_required(view_func):
    @wraps(view_func)
    @login_required
    def _wrapped(request, *args, **kwargs):
        if not (request.user.is_superuser or request.user.is_staff or getattr(request.user, 'role', '') == 'ADMIN'):
            messages.error(request, "Access restricted to SkillConnect platform administrators.")
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return _wrapped


@admin_required
def dashboard_view(request):
    total_users = User.objects.count()
    total_students = User.objects.filter(role='STUDENT').count()
    total_customers = User.objects.filter(role='CUSTOMER').count()
    
    verified_students = StudentProfile.objects.filter(verification_status='VERIFIED').count()
    pending_verifications = StudentProfile.objects.filter(verification_status='PENDING').count()
    
    total_posts = Post.objects.filter(is_active=True).count()
    total_services = Service.objects.count()
    total_orders = Order.objects.count()
    completed_orders = Order.objects.filter(status='COMPLETED').count()
    pending_reports = Report.objects.filter(status='PENDING').count()
    
    total_volume = Order.objects.filter(status='COMPLETED').aggregate(Sum('price'))['price__sum'] or 0

    recent_verifications = StudentProfile.objects.filter(verification_status='PENDING').select_related('user')[:5]
    recent_reports = Report.objects.filter(status='PENDING').select_related('reported_by')[:5]
    recent_orders = Order.objects.select_related('customer', 'student', 'service').order_by('-created_at')[:6]

    return render(request, 'admin_panel/dashboard.html', {
        'total_users': total_users,
        'total_students': total_students,
        'total_customers': total_customers,
        'verified_students': verified_students,
        'pending_verifications': pending_verifications,
        'total_posts': total_posts,
        'total_services': total_services,
        'total_orders': total_orders,
        'completed_orders': completed_orders,
        'pending_reports': pending_reports,
        'total_volume': total_volume,
        'recent_verifications': recent_verifications,
        'recent_reports': recent_reports,
        'recent_orders': recent_orders,
    })


@admin_required
def user_management_view(request):
    query = request.GET.get('q', '').strip()
    role_filter = request.GET.get('role', '')

    users_qs = User.objects.all().order_by('-date_joined')
    if query:
        users_qs = users_qs.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )
    if role_filter:
        users_qs = users_qs.filter(role=role_filter)

    return render(request, 'admin_panel/user_management.html', {
        'users': users_qs,
        'query': query,
        'role_filter': role_filter,
    })


@admin_required
def toggle_user_status_view(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    if target_user == request.user:
        messages.error(request, "You cannot suspend your own admin account.")
        return redirect('admin_users')

    target_user.is_active = not target_user.is_active
    target_user.save()
    status_msg = "activated/unblocked" if target_user.is_active else "suspended/blocked"
    messages.success(request, f"User {target_user.username} has been {status_msg}.")
    return redirect('admin_users')


@admin_required
def verifications_management_view(request):
    status_filter = request.GET.get('status', 'PENDING')
    
    verifications = StudentProfile.objects.select_related('user', 'user__profile').order_by('-updated_at')
    if status_filter != 'ALL':
        verifications = verifications.filter(verification_status=status_filter)

    return render(request, 'admin_panel/verifications.html', {
        'verifications': verifications,
        'status_filter': status_filter,
    })


@admin_required
def process_verification_view(request, profile_id):
    student_profile = get_object_or_404(StudentProfile, id=profile_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        notes = request.POST.get('notes', '').strip()

        if action == 'APPROVE':
            student_profile.verification_status = 'VERIFIED'
            student_profile.verified_at = timezone.now()
            student_profile.verification_notes = notes or "Identity successfully verified by SkillConnect Administrator."
            student_profile.save()

            Notification.send(
                recipient=student_profile.user,
                sender=request.user,
                notification_type='VERIFICATION',
                title='Congratulations! You are now a Verified Student',
                message='Your college identity has been verified. The Verified Student badge is now active on your profile!',
                link=f"/profile/{student_profile.user.username}/"
            )
            messages.success(request, f"Student {student_profile.user.get_display_name()} has been approved and granted Verified status.")

        elif action == 'REJECT':
            student_profile.verification_status = 'REJECTED'
            student_profile.verification_notes = notes or "Document was unreadable or could not be verified. Please re-submit."
            student_profile.save()

            Notification.send(
                recipient=student_profile.user,
                sender=request.user,
                notification_type='VERIFICATION',
                title='Student Verification Update',
                message=f'Verification could not be approved: {student_profile.verification_notes}',
                link="/verification/"
            )
            messages.warning(request, f"Student {student_profile.user.get_display_name()} verification was rejected.")

    return redirect('admin_verifications')


@admin_required
def reports_management_view(request):
    status_filter = request.GET.get('status', 'PENDING')
    reports = Report.objects.select_related('reported_by').order_by('-created_at')
    
    if status_filter != 'ALL':
        reports = reports.filter(status=status_filter)

    return render(request, 'admin_panel/reports.html', {
        'reports': reports,
        'status_filter': status_filter,
    })


@admin_required
def process_report_view(request, report_id):
    report = get_object_or_404(Report, id=report_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        notes = request.POST.get('admin_notes', '').strip()

        report.admin_notes = notes
        report.resolved_by = request.user

        if action == 'DISMISS':
            report.status = 'DISMISSED'
            report.save()
            messages.info(request, f"Report #{report.id} dismissed.")

        elif action == 'REMOVE_CONTENT':
            # Remove target content
            if report.target_type == 'POST':
                Post.objects.filter(id=report.target_id).delete()
            elif report.target_type == 'COMMENT':
                Comment.objects.filter(id=report.target_id).delete()
            elif report.target_type == 'SERVICE':
                Service.objects.filter(id=report.target_id).delete()

            report.status = 'RESOLVED'
            report.save()
            messages.success(request, f"Reported content removed and report #{report.id} marked as resolved.")

        elif action == 'SUSPEND_USER':
            target_user = None
            if report.target_type == 'USER':
                target_user = User.objects.filter(id=report.target_id).first()
            elif report.target_type == 'POST':
                post = Post.objects.filter(id=report.target_id).first()
                if post:
                    target_user = post.student
            elif report.target_type == 'SERVICE':
                service = Service.objects.filter(id=report.target_id).first()
                if service:
                    target_user = service.student

            if target_user and not target_user.is_superuser:
                target_user.is_active = False
                target_user.save()
                messages.warning(request, f"User {target_user.username} has been suspended.")

            report.status = 'RESOLVED'
            report.save()

    return redirect('admin_reports')


@admin_required
def category_management_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'ADD_CATEGORY':
            name = request.POST.get('name', '').strip()
            icon = request.POST.get('icon', 'palette').strip()
            desc = request.POST.get('description', '').strip()
            if name:
                Category.objects.create(name=name, icon=icon, description=desc)
                messages.success(request, f"Category '{name}' created.")
        elif action == 'ADD_SKILL':
            category_id = request.POST.get('category_id')
            skill_name = request.POST.get('skill_name', '').strip()
            if category_id and skill_name:
                category = get_object_or_404(Category, id=category_id)
                Skill.objects.get_or_create(category=category, name=skill_name)
                messages.success(request, f"Skill '{skill_name}' added under {category.name}.")

        return redirect('admin_categories')

    categories = Category.objects.prefetch_related('skills').all()
    return render(request, 'admin_panel/categories.html', {'categories': categories})


@admin_required
def orders_overview_view(request):
    status_filter = request.GET.get('status', '')
    orders = Order.objects.select_related('customer', 'student', 'service').order_by('-created_at')
    
    if status_filter:
        orders = orders.filter(status=status_filter)

    return render(request, 'admin_panel/orders_overview.html', {
        'orders': orders,
        'status_filter': status_filter,
        'status_choices': Order.STATUS_CHOICES,
    })
