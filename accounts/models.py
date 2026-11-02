from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='palette', help_text='Icon identifier (e.g. camera, brush, code, book, music)')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Skill(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        unique_together = ('category', 'name')
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.category.name})"


class User(AbstractUser):
    ROLE_CHOICES = (
        ('CUSTOMER', 'Customer'),
        ('STUDENT', 'Student / Service Provider'),
        ('ADMIN', 'Platform Administrator'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='CUSTOMER')
    email = models.EmailField(unique=True)

    @property
    def is_student(self):
        return self.role == 'STUDENT'

    @property
    def is_customer(self):
        return self.role == 'CUSTOMER'

    @property
    def is_platform_admin(self):
        return self.role == 'ADMIN' or self.is_superuser or self.is_staff

    def get_display_name(self):
        full = self.get_full_name()
        return full if full else self.username

    def __str__(self):
        return f"{self.get_display_name()} ({self.get_role_display()})"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    bio = models.TextField(blank=True, max_length=500)
    interests = models.ManyToManyField(Category, blank=True, related_name='interested_profiles')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_avatar_url(self):
        if self.profile_picture:
            return self.profile_picture.url
        return f"https://api.dicebear.com/7.x/initials/svg?seed={self.user.username}&backgroundColor=4f46e5,7c3aed,06b6d4"

    def __str__(self):
        return f"Profile for {self.user.username}"


class StudentProfile(models.Model):
    VERIFICATION_STATUS_CHOICES = (
        ('PENDING', 'Pending Verification'),
        ('VERIFIED', 'Verified Student'),
        ('REJECTED', 'Rejected'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    college_name = models.CharField(max_length=200)
    college_email = models.EmailField(blank=True)
    student_id = models.CharField(max_length=100, blank=True, help_text='Roll number or enrollment ID')
    course = models.CharField(max_length=150, help_text='e.g. B.Tech Computer Science, B.Des, MBA')
    year_of_study = models.CharField(max_length=50, help_text='e.g. 1st Year, 2nd Year, 3rd Year, Final Year')
    college_id_card = models.ImageField(upload_to='college_ids/', blank=True, null=True)
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS_CHOICES, default='PENDING')
    verification_notes = models.TextField(blank=True, help_text='Admin remarks regarding verification')
    verified_at = models.DateTimeField(null=True, blank=True)
    is_available = models.BooleanField(default=True, help_text='Whether student is accepting new orders')
    skills = models.ManyToManyField(Skill, blank=True, related_name='student_profiles')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_verified(self):
        return self.verification_status == 'VERIFIED'

    def average_rating(self):
        from reviews.models import Review
        reviews = Review.objects.filter(student=self.user)
        if reviews.exists():
            avg = reviews.aggregate(models.Avg('rating'))['rating__avg']
            return round(avg, 1)
        return 5.0  # Default friendly starter rating

    def reviews_count(self):
        from reviews.models import Review
        return Review.objects.filter(student=self.user).count()

    def completed_orders_count(self):
        from orders.models import Order
        return Order.objects.filter(student=self.user, status='COMPLETED').count()

    def followers_count(self):
        return Follow.objects.filter(following=self.user).count()

    def following_count(self):
        return Follow.objects.filter(follower=self.user).count()

    def __str__(self):
        return f"Student: {self.user.get_display_name()} ({self.college_name}) - {self.verification_status}"


class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    organization_or_event = models.CharField(max_length=150, blank=True, help_text='Optional club or department')
    preferred_contact_method = models.CharField(max_length=50, default='SkillConnect Chat')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Customer: {self.user.username}"


class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following_set')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers_set')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"
