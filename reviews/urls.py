from django.urls import path
from . import views

urlpatterns = [
    path('orders/<int:order_id>/review/', views.create_review_view, name='create_review'),
]
