from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
from .forms import (
    UserRegistrationForm, LoginForm, ProfileUpdateForm,
    StudentProfileUpdateForm, VerificationSubmissionForm
)
from .models import Profile, StudentProfile, CustomerProfile, Follow, Category, Skill
from notifications.models import Notification

User = get_user_model()


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            role = form.cleaned_data['role']
            full_name = form.cleaned_data['full_name']
            names = full_name.split(' ', 1)
            first_name = names[0]
            last_name = names[1] if len(names) > 1 else ''

            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                first_name=first_name,
                last_name=last_name,
                role=role
            )

            # Create generic Profile
            Profile.objects.create(user=user)

            if role == 'STUDENT':
                student_profile = StudentProfile.objects.create(
                    user=user,
                    college_name=form.cleaned_data.get('college_name', ''),
                    college_email=form.cleaned_data.get('college_email', ''),
                    student_id=form.cleaned_data.get('student_id', ''),
                    course=form.cleaned_data.get('course', ''),
                    year_of_study=form.cleaned_data.get('year_of_study', ''),
                    college_id_card=form.cleaned_data.get('college_id_card', None),
                    verification_status='PENDING'
                )
                login(request, user)
                messages.success(request, f"Welcome to SkillConnect, {user.first_name}! Your student account is created. Please complete your profile and verification.")
                return redirect('verification')
            else:
                CustomerProfile.objects.create(user=user)
                login(request, user)
                messages.success(request, f"Welcome to SkillConnect, {user.first_name}! Let's select your interests.")
                return redirect('interests_setup')
    else:
        initial_role = request.GET.get('role', 'CUSTOMER')
        form = UserRegistrationForm(initial={'role': initial_role})

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.get_display_name()}!")
            
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            
            if user.is_platform_admin:
                return redirect('admin_dashboard')
            elif user.is_student:
                return redirect('student_dashboard')
            else:
                return redirect('home')
        else:
            messages.error(request, "Invalid username/email or password. Please try again.")
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been safely logged out. See you soon!")
    return redirect('landing')


def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    is_self = (request.user.is_authenticated and request.user == profile_user)
    is_following = False

    if request.user.is_authenticated and not is_self:
        is_following = Follow.objects.filter(follower=request.user, following=profile_user).exists()

    student_profile = getattr(profile_user, 'student_profile', None)
    customer_profile = getattr(profile_user, 'customer_profile', None)

    posts = profile_user.posts.filter(is_active=True).order_by('-created_at')
    services = profile_user.services.filter(is_active=True).order_by('-created_at') if profile_user.is_student else []
    
    from reviews.models import Review
    reviews = Review.objects.filter(student=profile_user).select_related('customer', 'customer__profile') if profile_user.is_student else []

    context = {
        'profile_user': profile_user,
        'student_profile': student_profile,
        'customer_profile': customer_profile,
        'posts': posts,
        'services': services,
        'reviews': reviews,
        'is_self': is_self,
        'is_following': is_following,
        'followers_count': Follow.objects.filter(following=profile_user).count(),
        'following_count': Follow.objects.filter(follower=profile_user).count(),
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def edit_profile_view(request):
    user = request.user
    profile = getattr(user, 'profile', None)
    if not profile:
        profile = Profile.objects.create(user=user)

    student_profile = getattr(user, 'student_profile', None)

    if request.method == 'POST':
        profile_form = ProfileUpdateForm(
            request.POST, request.FILES, instance=profile,
            initial={'full_name': user.get_full_name(), 'email': user.email}
        )
        student_form = None
        if user.is_student and student_profile:
            student_form = StudentProfileUpdateForm(request.POST, instance=student_profile)

        if profile_form.is_valid() and (not student_form or student_form.is_valid()):
            # Update user fields
            full_name = profile_form.cleaned_data['full_name']
            names = full_name.split(' ', 1)
            user.first_name = names[0]
            user.last_name = names[1] if len(names) > 1 else ''
            user.email = profile_form.cleaned_data['email']
            user.save()

            profile_form.save()
            if student_form:
                student_form.save()

            messages.success(request, "Your profile has been updated successfully!")
            return redirect('profile', username=user.username)
    else:
        profile_form = ProfileUpdateForm(
            instance=profile,
            initial={'full_name': user.get_full_name(), 'email': user.email}
        )
        student_form = StudentProfileUpdateForm(instance=student_profile) if (user.is_student and student_profile) else None

    categories = Category.objects.filter(is_active=True)
    all_skills = Skill.objects.select_related('category')

    return render(request, 'accounts/edit_profile.html', {
        'profile_form': profile_form,
        'student_form': student_form,
        'categories': categories,
        'all_skills': all_skills,
    })


@login_required
def verification_view(request):
    if not request.user.is_student:
        messages.warning(request, "Only student accounts undergo the student verification process.")
        return redirect('home')

    student_profile = getattr(request.user, 'student_profile', None)
    if not student_profile:
        student_profile = StudentProfile.objects.create(user=request.user)

    if request.method == 'POST':
        form = VerificationSubmissionForm(request.POST, request.FILES, instance=student_profile)
        if form.is_valid():
            updated_profile = form.save(commit=False)
            updated_profile.verification_status = 'PENDING'
            updated_profile.save()
            messages.success(request, "Verification documents submitted successfully! Our admin team will review your student status shortly.")
            return redirect('verification')
    else:
        form = VerificationSubmissionForm(instance=student_profile)

    return render(request, 'accounts/verification.html', {
        'student_profile': student_profile,
        'form': form,
    })


@login_required
def interests_setup_view(request):
    profile = getattr(request.user, 'profile', None)
    if not profile:
        profile = Profile.objects.create(user=request.user)

    categories = Category.objects.filter(is_active=True)

    if request.method == 'POST':
        selected_ids = request.POST.getlist('interests')
        profile.interests.set(selected_ids)
        messages.success(request, "Interests saved! Your personalized recommendation feed is ready.")
        return redirect('home')

    user_interest_ids = list(profile.interests.values_list('id', flat=True))
    return render(request, 'accounts/interests_setup.html', {
        'categories': categories,
        'user_interest_ids': user_interest_ids,
    })


@login_required
@require_POST
def follow_toggle_view(request, username):
    target_user = get_object_or_404(User, username=username)
    if target_user == request.user:
        return JsonResponse({'error': 'You cannot follow yourself.'}, status=400)

    follow_record = Follow.objects.filter(follower=request.user, following=target_user).first()
    if follow_record:
        follow_record.delete()
        is_following = False
    else:
        Follow.objects.create(follower=request.user, following=target_user)
        is_following = True
        Notification.send(
            recipient=target_user,
            sender=request.user,
            notification_type='FOLLOW',
            title='New Follower',
            message=f"{request.user.get_display_name()} started following you.",
            link=f"/profile/{request.user.username}/"
        )

    followers_count = Follow.objects.filter(following=target_user).count()
    return JsonResponse({
        'is_following': is_following,
        'followers_count': followers_count,
        'message': 'Followed' if is_following else 'Unfollowed'
    })


@login_required
def student_dashboard_view(request):
    if not request.user.is_student:
        messages.warning(request, "Access restricted to student accounts.")
        return redirect('home')

    student_profile = getattr(request.user, 'student_profile', None)
    
    from orders.models import Order
    from posts.models import Post
    from services.models import Service

    incoming_orders = Order.objects.filter(student=request.user).select_related('customer', 'service').order_by('-created_at')
    active_orders = incoming_orders.filter(status__in=['REQUESTED', 'ACCEPTED', 'IN_PROGRESS', 'READY'])
    completed_orders = incoming_orders.filter(status='COMPLETED')

    posts = Post.objects.filter(student=request.user, is_active=True).order_by('-created_at')[:6]
    services = Service.objects.filter(student=request.user).order_by('-created_at')

    total_earnings = sum(o.price for o in completed_orders)

    context = {
        'student_profile': student_profile,
        'incoming_orders': incoming_orders[:5],
        'active_orders_count': active_orders.count(),
        'completed_orders_count': completed_orders.count(),
        'total_earnings': total_earnings,
        'posts_count': Post.objects.filter(student=request.user, is_active=True).count(),
        'services_count': services.count(),
        'followers_count': Follow.objects.filter(following=request.user).count(),
        'posts': posts,
        'services': services,
    }
    return render(request, 'accounts/student_dashboard.html', context)
