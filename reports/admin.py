from django.contrib import admin
from .models import Report

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'reported_by', 'target_type', 'target_id', 'reason', 'status', 'created_at')
    list_filter = ('target_type', 'reason', 'status', 'created_at')
    search_fields = ('reported_by__username', 'details')
