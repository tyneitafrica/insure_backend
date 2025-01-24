from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta
from .manager import CustomUserManager
from .utility import generate_otp


# Custom User Model
class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        ORGANISATION = "ORGANISATION", "Organisation"
        APPLICANT = "APPLICANT", "Applicant"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.APPLICANT)
    otp = models.CharField(max_length=7, null=True, blank=True)
    otp_expiration = models.DateTimeField(null=True, blank=True)
    email = models.EmailField(unique=True)

    # Override username as the unique identifier
    username = None
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def set_otp(self):
        """Generate and set a one-time password."""
        self.otp = generate_otp()
        self.otp_expiration = timezone.now()
        self.save()

    def is_otp_valid(self):
        """Check if the OTP is still valid."""
        if self.otp_expiration:
            return timezone.now() < self.otp_expiration + timedelta(minutes=2)
        return False

    def __str__(self):
        return f"{self.email} - {self.role}"


# Applicant Model
class Applicant(models.Model):
    GENDER_CHOICES = [
        ("Male", "Male"),
        ("Female", "Female"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='applicant_profile')
    phone_number = models.CharField(max_length=20)
    yob = models.DateField(null=True, blank=True)  # Year of birth
    id_no = models.CharField(max_length=20, unique=True)
    occupation = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def age(self):
        """Calculate age based on year of birth."""
        if self.yob:
            today = timezone.now().date()
            return today.year - self.yob.year - ((today.month, today.day) < (self.yob.month, self.yob.day))
        return None

    def __str__(self):
        return f"{self.user.email} - {self.occupation}"


# Organisation Model
class Organisation(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='organisation_profile')
    company_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company_name}"


# Insurance Base Model
class Insurance(models.Model):
    TYPE_CHOICES = [
        ("Motor", "Motor"),
        ("Health", "Health"),
        ("Personal Accident", "Personal Accident"),
        ("Life", "Life"),
        ("Marine", "Marine"),
        ("Professional Indemnity", "Professional Indemnity"),
    ]

    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, related_name='insurances')
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    title = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.type}"


# Motor Insurance Model
class MotorInsurance(models.Model):
    insurance = models.OneToOneField(Insurance, on_delete=models.CASCADE, related_name='motor_details')
    vehicle_type = models.CharField(max_length=100)  # e.g., Private, Commercial
    vehicle_make = models.CharField(max_length=100)
    vehicle_model = models.CharField(max_length=100)
    vehicle_year = models.IntegerField()
    cover_start_date = models.DateField()
    vehicle_registration_number = models.CharField(max_length=100)
    cover_type = models.CharField(max_length=100)  # e.g., Comprehensive
    evaluated = models.BooleanField(default=False)
    vehicle_value = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.vehicle_registration_number} - {self.cover_type}"


# Health Insurance Model
class HealthInsurance(models.Model):
    insurance = models.OneToOneField(Insurance, on_delete=models.CASCADE, related_name='health_details')
    health_type = models.CharField(max_length=100)  # e.g., Individual, Family
    coverage_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_travel_related = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.health_type} - {self.coverage_amount}"


# Benefit Model
class Benefit(models.Model):
    insurance = models.ManyToManyField(Insurance, related_name='benefits')
    limit_of_liability = models.CharField(max_length=100)
    rate = models.DecimalField(max_digits=5, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.limit_of_liability} - {self.price}"


# Policy Model
class Policy(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("ACTIVE", "Active"),
        ("EXPIRED", "Expired"),
        ("CANCELLED", "Cancelled"),
    ]

    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE, related_name="policies")
    insurance = models.ForeignKey(Insurance, on_delete=models.CASCADE, related_name="policies")
    benefits = models.ManyToManyField(Benefit, related_name="policies")
    policy_number = models.CharField(max_length=100, unique=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    duration = models.PositiveIntegerField(default=12)  # in months
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.end_date:
            self.end_date = self.start_date + timedelta(days=self.duration * 30)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.policy_number} - {self.status}"


# Payment Model
class Payment(models.Model):
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE, related_name='payments')


    def __str__(self):
        return f"{self.transaction_id} - {self.amount}"
