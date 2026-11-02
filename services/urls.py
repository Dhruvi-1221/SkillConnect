from django.urls import path
from . import views

urlpatterns = [
    path('services/', views.service_list_view, name='service_list'),
    path('services/create/', views.create_service_view, name='create_service'),
    path('services/<int:service_id>/', views.service_detail_view, name='service_detail'),
    path('services/<int:service_id>/edit/', views.edit_service_view, name='edit_service'),
    path('services/<int:service_id>/delete/', views.delete_service_view, name='delete_service'),
    path('student/services/', views.manage_services_view, name='manage_services'),
]
