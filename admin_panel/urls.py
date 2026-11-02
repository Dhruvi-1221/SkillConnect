from django.urls import path
from . import views

urlpatterns = [
    path('platform-admin/', views.dashboard_view, name='admin_dashboard'),
    path('platform-admin/users/', views.user_management_view, name='admin_users'),
    path('platform-admin/users/<int:user_id>/toggle/', views.toggle_user_status_view, name='admin_toggle_user'),
    path('platform-admin/verifications/', views.verifications_management_view, name='admin_verifications'),
    path('platform-admin/verifications/<int:profile_id>/process/', views.process_verification_view, name='admin_process_verification'),
    path('platform-admin/reports/', views.reports_management_view, name='admin_reports'),
    path('platform-admin/reports/<int:report_id>/process/', views.process_report_view, name='admin_process_report'),
    path('platform-admin/categories/', views.category_management_view, name='admin_categories'),
    path('platform-admin/orders/', views.orders_overview_view, name='admin_orders'),
]
