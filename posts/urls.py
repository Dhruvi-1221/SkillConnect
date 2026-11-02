from django.urls import path
from . import views

urlpatterns = [
    path('posts/<int:post_id>/', views.post_detail_view, name='post_detail'),
    path('posts/create/', views.create_post_view, name='create_post'),
    path('posts/<int:post_id>/edit/', views.edit_post_view, name='edit_post'),
    path('posts/<int:post_id>/delete/', views.delete_post_view, name='delete_post'),
    path('posts/<int:post_id>/like/', views.like_toggle_view, name='like_toggle'),
    path('posts/<int:post_id>/comment/', views.add_comment_view, name='add_comment'),
    path('posts/comment/<int:comment_id>/delete/', views.delete_comment_view, name='delete_comment'),
    path('student/posts/', views.manage_posts_view, name='manage_posts'),
]
