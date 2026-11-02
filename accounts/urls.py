from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/<str:username>/', views.profile_view, name='profile'),
    path('settings/profile/', views.edit_profile_view, name='edit_profile'),
    path('verification/', views.verification_view, name='verification'),
    path('interests/', views.interests_setup_view, name='interests_setup'),
    path('student/dashboard/', views.student_dashboard_view, name='student_dashboard'),
    path('ajax/follow/<str:username>/', views.follow_toggle_view, name='ajax_follow_toggle'),
]
