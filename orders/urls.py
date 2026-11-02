from django.urls import path
from . import views

urlpatterns = [
    path('services/<int:service_id>/order/', views.book_service_view, name='book_service'),
    path('orders/', views.order_list_view, name='order_list'),
    path('orders/<int:order_id>/', views.order_detail_view, name='order_detail'),
    path('orders/<int:order_id>/status/', views.update_order_status_view, name='update_order_status'),
]
