from django.urls import path
from . import views

urlpatterns = [
    path('notifications/', views.notification_list_view, name='notifications'),
    path('notifications/mark-all-read/', views.mark_all_read_view, name='mark_all_notifications_read'),
    path('notifications/<int:notification_id>/read/', views.read_notification_view, name='read_notification'),
]
