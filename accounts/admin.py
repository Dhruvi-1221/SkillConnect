from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Profile, StudentProfile, CustomerProfile, Category, Skill, Follow


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False


class StudentProfileInline(admin.StackedInline):
    model = StudentProfile
    can_delete = False


class CustomerProfileInline(admin.StackedInline):
    model = CustomerProfile
    can_delete = False


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active', 'is_staff')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Platform Role', {'fields': ('role',)}),
    )
    inlines = [ProfileInline]


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'college_name', 'course', 'year_of_study', 'verification_status', 'is_available')
    list_filter = ('verification_status', 'is_available', 'year_of_study')
    search_fields = ('user__username', 'user__first_name', 'college_name', 'student_id')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon', 'is_active')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    list_filter = ('category',)
    search_fields = ('name',)


admin.site.register(CustomerProfile)
admin.site.register(Follow)
