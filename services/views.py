from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.db.models import Q
from .models import Service
from .forms import ServiceForm
from accounts.models import Category


def service_list_view(request):
    category_slug = request.GET.get('category', '')
    sort_by = request.GET.get('sort', 'recent')
    query = request.GET.get('q', '').strip()

    services_qs = Service.objects.filter(is_active=True).select_related(
        'student', 'student__student_profile', 'student__profile', 'category'
    )

    if query:
        services_qs = services_qs.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(student__username__icontains=query)
        )

    selected_category = None
    if category_slug:
        selected_category = Category.objects.filter(slug=category_slug).first()
        if selected_category:
            services_qs = services_qs.filter(category=selected_category)

    if sort_by == 'price_low':
        services_qs = services_qs.order_by('price')
    elif sort_by == 'price_high':
        services_qs = services_qs.order_by('-price')
    else:
        services_qs = services_qs.order_by('-created_at')

    categories = Category.objects.filter(is_active=True)

    return render(request, 'services/service_list.html', {
        'services': services_qs,
        'categories': categories,
        'selected_category': selected_category,
        'sort_by': sort_by,
        'query': query,
    })


def service_detail_view(request, service_id):
    service = get_object_or_404(
        Service.objects.select_related('student', 'student__student_profile', 'student__profile', 'category'),
        id=service_id,
        is_active=True
    )
    student_profile = getattr(service.student, 'student_profile', None)
    other_services = Service.objects.filter(student=service.student, is_active=True).exclude(id=service.id)[:3]

    return render(request, 'services/service_detail.html', {
        'service': service,
        'student_profile': student_profile,
        'other_services': other_services,
    })


@login_required
def create_service_view(request):
    if not request.user.is_student:
        messages.warning(request, "Only registered student providers can offer services.")
        return redirect('home')

    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES)
        if form.is_valid():
            service = form.save(commit=False)
            service.student = request.user
            service.save()
            messages.success(request, f"Service '{service.title}' created and now visible on your profile!")
            return redirect('service_detail', service_id=service.id)
    else:
        form = ServiceForm()

    return render(request, 'services/create_service.html', {'form': form})


@login_required
def edit_service_view(request, service_id):
    service = get_object_or_404(Service, id=service_id, student=request.user)

    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, "Service details updated successfully.")
            return redirect('service_detail', service_id=service.id)
    else:
        form = ServiceForm(instance=service)

    return render(request, 'services/edit_service.html', {'form': form, 'service': service})


@login_required
def delete_service_view(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    if service.student != request.user and not request.user.is_platform_admin:
        return HttpResponseForbidden("Not authorized to delete this service.")

    if request.method == 'POST':
        service.delete()
        messages.success(request, "Service listing removed.")
        return redirect('manage_services' if request.user.is_student else 'service_list')

    return render(request, 'services/confirm_delete.html', {'service': service})


@login_required
def manage_services_view(request):
    if not request.user.is_student:
        return redirect('home')

    services = Service.objects.filter(student=request.user).order_by('-created_at')
    return render(request, 'services/manage_services.html', {'services': services})
