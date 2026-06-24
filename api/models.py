from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        extra_fields.setdefault('role', 'USER')
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'ADMIN') # Default superuser to ADMIN role

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    class Roles(models.TextChoices):
        USER = 'USER', 'User'
        OFFICE = 'OFFICE', 'Office'
        ADMIN = 'ADMIN', 'Admin'
        
    username = None
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=Roles.choices, default=Roles.USER)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.email} ({self.role})"

class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_duration_hours = models.DecimalField(max_digits=4, decimal_places=1, default=1.0)

    def __str__(self):
        return self.name

class AppointmentSlot(models.Model):
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    max_capacity = models.PositiveIntegerField(default=1, help_text="Number of cars that can be detailed in this slot")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['date', 'start_time']

    def __str__(self):
        return f"{self.date} ({self.start_time} - {self.end_time})"

class Booking(models.Model):
    class BookingStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        CONFIRMED = 'CONFIRMED', 'Confirmed'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        READY = 'READY', 'Ready for Delivery'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    service = models.ForeignKey(Service, on_delete=models.PROTECT)
    slot = models.ForeignKey(AppointmentSlot, on_delete=models.PROTECT, related_name='bookings')
    status = models.CharField(max_length=20, choices=BookingStatus.choices, default=BookingStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.service.name} - {self.status}"
    
class BookingLog(models.Model):
    booking_id = models.IntegerField()
    client_email = models.EmailField()
    service_name = models.CharField(max_length=100)
    action_by = models.CharField(max_length=255, help_text="Email of the user/staff who triggered this action")
    status_changed_to = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"Booking #{self.booking_id} modified to {self.status_changed_to} by {self.action_by}"