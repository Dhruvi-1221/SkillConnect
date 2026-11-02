from django.urls import path
from . import views

urlpatterns = [
    path('report/<str:target_type>/<int:target_id>/', views.submit_report_view, name='submit_report'),
]
