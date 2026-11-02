from django.contrib import admin
from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('order', 'customer', 'student', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('customer__username', 'student__username', 'comment')
