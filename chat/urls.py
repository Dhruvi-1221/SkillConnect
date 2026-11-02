from django.urls import path
from . import views

urlpatterns = [
    path('chat/', views.chat_view, name='chat'),
    path('chat/<int:conversation_id>/', views.chat_view, name='chat_conversation'),
    path('chat/start/<str:username>/', views.start_chat_view, name='start_chat'),
    path('chat/<int:conversation_id>/send/', views.send_message_ajax, name='send_message_ajax'),
    path('chat/<int:conversation_id>/poll/', views.poll_messages_ajax, name='poll_messages_ajax'),
]
