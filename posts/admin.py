from django.contrib import admin
from .models import Post, PostLike, Comment

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'category', 'created_at', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('student__username', 'caption', 'skill_tags')

admin.site.register(PostLike)
admin.site.register(Comment)
