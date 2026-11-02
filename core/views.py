from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q, Count
from accounts.models import User, StudentProfile, Category, Skill, Follow
from posts.models import Post
from services.models import Service
from .models import ContactMessage


def landing_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    categories = Category.objects.filter(is_active=True).annotate(posts_count=Count('posts'))[:8]
    featured_students = StudentProfile.objects.filter(
        verification_status='VERIFIED'
    ).select_related('user', 'user__profile')[:4]
    
    recent_posts = Post.objects.filter(is_active=True).select_related(
        'student', 'student__student_profile', 'student__profile', 'category'
    )[:6]

    return render(request, 'core/landing.html', {
        'categories': categories,
        'featured_students': featured_students,
        'recent_posts': recent_posts,
    })


def home_feed_view(request):
    """Personalized recommended feed for students & customers."""
    categories = Category.objects.filter(is_active=True)
    following_users = []
    recommended_posts = []

    if request.user.is_authenticated:
        profile = getattr(request.user, 'profile', None)
        user_interests = profile.interests.all() if profile else Category.objects.none()
        following_ids = Follow.objects.filter(follower=request.user).values_list('following_id', flat=True)

        base_qs = Post.objects.filter(is_active=True).select_related(
            'student', 'student__student_profile', 'student__profile', 'category'
        ).prefetch_related('likes', 'comments')

        if user_interests.exists():
            # Posts matching user interests OR from followed students
            interest_posts = base_qs.filter(
                Q(category__in=user_interests) | Q(student_id__in=following_ids)
            ).distinct()
            other_posts = base_qs.exclude(id__in=interest_posts.values_list('id', flat=True))
            recommended_posts = list(interest_posts) + list(other_posts)
        else:
            recommended_posts = list(base_qs)
    else:
        recommended_posts = list(
            Post.objects.filter(is_active=True).select_related(
                'student', 'student__student_profile', 'student__profile', 'category'
            ).prefetch_related('likes', 'comments')
        )

    # Active top students for sidebar
    suggested_students = StudentProfile.objects.filter(
        verification_status='VERIFIED'
    ).exclude(user=request.user if request.user.is_authenticated else None).select_related('user', 'user__profile')[:5]

    return render(request, 'core/home_feed.html', {
        'posts': recommended_posts,
        'categories': categories,
        'suggested_students': suggested_students,
    })


def search_view(request):
    query = request.GET.get('q', '').strip()
    category_slug = request.GET.get('category', '')
    filter_type = request.GET.get('type', 'all')  # all, students, services, posts

    students = []
    services = []
    posts = []

    selected_category = None
    if category_slug:
        selected_category = Category.objects.filter(slug=category_slug).first()

    if query or selected_category:
        # Search Students
        student_qs = StudentProfile.objects.select_related('user', 'user__profile').prefetch_related('skills')
        if query:
            student_qs = student_qs.filter(
                Q(user__username__icontains=query) |
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query) |
                Q(college_name__icontains=query) |
                Q(course__icontains=query) |
                Q(skills__name__icontains=query)
            ).distinct()
        if selected_category:
            student_qs = student_qs.filter(skills__category=selected_category).distinct()
        students = student_qs[:12]

        # Search Services
        service_qs = Service.objects.filter(is_active=True).select_related('student', 'student__profile', 'student__student_profile', 'category')
        if query:
            service_qs = service_qs.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(student__username__icontains=query) |
                Q(student__first_name__icontains=query) |
                Q(student__last_name__icontains=query)
            )
        if selected_category:
            service_qs = service_qs.filter(category=selected_category)
        services = service_qs[:12]

        # Search Posts
        post_qs = Post.objects.filter(is_active=True).select_related('student', 'student__profile', 'student__student_profile', 'category')
        if query:
            post_qs = post_qs.filter(
                Q(caption__icontains=query) |
                Q(skill_tags__icontains=query) |
                Q(student__username__icontains=query) |
                Q(student__first_name__icontains=query)
            )
        if selected_category:
            post_qs = post_qs.filter(category=selected_category)
        posts = post_qs[:12]

    categories = Category.objects.filter(is_active=True)

    return render(request, 'core/search.html', {
        'query': query,
        'category_slug': category_slug,
        'selected_category': selected_category,
        'filter_type': filter_type,
        'students': students,
        'services': services,
        'posts': posts,
        'categories': categories,
        'total_results': len(students) + len(services) + len(posts),
    })


def about_view(request):
    return render(request, 'core/about.html')


def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        if name and email and message:
            ContactMessage.objects.create(
                name=name,
                email=email,
                subject=subject or 'General Inquiry',
                message=message
            )
            messages.success(request, "Thank you for getting in touch! Our student support team will respond to your email promptly.")
            return redirect('contact')
        else:
            messages.error(request, "Please fill in all required fields.")

    return render(request, 'core/contact.html')
