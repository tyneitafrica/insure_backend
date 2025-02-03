from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
# from django.core.validators import RegexValidator, MinLengthValidator,MaxLengthValidator
from datetime import timedelta
from .manager import CustomUserManager
from .utility import generate_otp
from django.db.models.signals import post_save
from django.dispatch import receiver


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

# set up the receivor 
@receiver(post_save, sender=User)
def create_applicant_profile(sender, instance, created, **kwargs):
    if created and instance.role == User.Role.APPLICANT:
        Applicant.objects.create(user=instance)


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
    
class ApplicantKYC(models.Model):
    applicant = models.OneToOneField(Applicant, on_delete=models.CASCADE, related_name='kyc_details')
    national_id  = models.ImageField(upload_to='national_id_images/', null=True, blank=True)
    driving_license = models.ImageField(upload_to='driving_license_images/', null=True, blank=True)
    valuation_report = models.ImageField(upload_to='valuation_report_images/', null=True, blank=True)
    kra_pin_certificate = models.ImageField(upload_to='kra_pin_certificate_images/', null=True, blank=True)
    log_book = models.ImageField(upload_to='log_book_images/', null=True, blank=True) 

    def __str__(self):
        return f"{self.applicant}"


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
    company_name= models.CharField(max_length=200, null=True, blank=True)
    insurance_image = models.ImageField(upload_to='insurance_images/', null=True, blank=True) #will handle profile image of a specific insurance 
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    title = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} {self.type} {self.description} {self.organisation}"

# Motor Insurance Model
class MotorInsurance(models.Model):
    insurance = models.ForeignKey(Insurance, on_delete=models.CASCADE, related_name='motor_details')
    vehicle_type = models.CharField(max_length=100)  # e.g., saloon,bus,
    cover_type = models.CharField(max_length=100)  # e.g., Comprehensive
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.price} - {self.cover_type} - {self.insurance}"


# Health Insurance Model
class HealthInsurance(models.Model):
    insurance = models.ForeignKey(Insurance, on_delete=models.CASCADE, related_name='health_details')
    high_range= models.IntegerField()
    low_range= models.IntegerField()
    cover_type = models.CharField(max_length=100)  # e.g., Individual, Family
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at= models.DateTimeField(auto_now_add=True)
    updated_at= models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.cover_type} - {self.price}"

# Benefit Model
class Benefit(models.Model):
    insurance = models.ForeignKey(Insurance, on_delete=models.CASCADE, related_name='benefits')
    limit_of_liability = models.CharField(max_length=100)
    rate = models.DecimalField(max_digits=5, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.limit_of_liability} - {self.price}"

class HealthInsuaranceQuoteRequest(models.Model):
    class GenderChoice(models.TextChoices):
        MALE= 'MALE', 'Male'
        FEMALE= 'FEMALE', 'Female'
        OTHER= 'OTHER', 'Other'

    first_name= models.CharField(max_length=100, null=True, blank=True)
    last_name= models.CharField(max_length=100, null=True, blank=True)
    dob= models.DateField(null=True, blank=True)
    national_id= models.BigIntegerField()
    occupation= models.CharField(max_length=200, null=True, blank=True)
    phone_number= models.CharField(max_length=20, null=True, blank=True)
    gender= models.CharField(max_length=20, choices=GenderChoice.choices, default=GenderChoice.MALE)
    coverage_amount= models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    coverage_type= models.CharField(max_length=100, null=True, blank=True)  # e.g., Individual, Family
    is_travel_related= models.BooleanField(default=False, null=True, blank=True)
    is_covered= models.BooleanField(default=False, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    
class HealthLifestyle(models.Model):
    # one on one relation
    health_insuarance_quote_request = models.OneToOneField(HealthInsuaranceQuoteRequest, on_delete=models.CASCADE, related_name='health_lifestyle')
    pre_existing_condition= models.BooleanField(default=False)
    high_risk_activities= models.BooleanField(default=False)    
    medication= models.BooleanField(default=False)
    mode_of_transport= models.CharField(max_length=200, null=True, blank=True)
    smoking= models.BooleanField(default=False)
    past_claim= models.BooleanField(default=False)
    stress_level= models.BooleanField(default=False)
    family_history= models.BooleanField(default=False)
    allergies= models.BooleanField(default=False)
    mental_health= models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)




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

# to hold user data temporary   
class MotorInsuranceTempData(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    id_no = models.CharField(max_length=20)
    # motor details
    vehicle_category = models.CharField(max_length=100,choices=[('Private','Private'),('Commercial','Commercial'),('Public Service','Public Service')])
    vehicle_type = models.CharField(max_length=100)
    vehicle_model = models.CharField(max_length=100)
    vehicle_year = models.IntegerField()
    vehicle_value = models.DecimalField(max_digits=100, decimal_places=2)
    cover_start_date = models.DateField()
    is_evaluated = models.BooleanField(default=True)
    evaluated_price = models.DecimalField(max_digits=100,decimal_places=2,null=True,blank=True)
    vehicle_registration_number = models.CharField(max_length=100)
    insurance_type = models.CharField(max_length=50,
    choices=[
        ('comprehensive', 'Comprehensive'),
        ('third_party', 'Third Party'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.vehicle_registration_number}"   


# Marine Insurance Temporary Data Model
class MarineInsuranceTempData(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    id_no = models.CharField(max_length=20)
    # Marine-specific details
    vessel_type = models.CharField(max_length=100)  # e.g., Cargo Ship, Fishing Boat
    coverage_type = models.CharField(max_length=100, choices=[
        ('Hull Insurance', 'Hull Insurance'),
        ('Cargo Insurance', 'Cargo Insurance'),
        ('Freight Insurance', 'Freight Insurance'),
    ])
    is_evaluated = models.BooleanField(default=False)
    evaluated_price = models.DecimalField(max_digits=100, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.vessel_name}"
    

# Marine Insurance Model
class MarineInsurance(models.Model):
    insurance = models.ForeignKey(Insurance, on_delete=models.CASCADE, related_name='marine_details')
    vessel_type = models.CharField(max_length=100,choices=[
        ('Fishing Boat', 'Fishing Boat'),
        ('Cargo', 'Cargo'),
        ('Yacht', 'Yacht'),        
    ])  # e.g., Cargo Ship, Fishing Boat, Yacht
    cargo_type = models.CharField(max_length=100,null=True,blank=True)  # e.g., General Cargo, Oil, Containers
    voyage_type = models.CharField(max_length=100,null=True,blank=True)  # e.g., Coastal, International
    coverage_type = models.CharField(max_length=100, choices=[
        ('Hull Insurance', 'Hull Insurance'),
        ('Cargo Insurance', 'Cargo Insurance'),
        ('Freight Insurance', 'Freight Insurance'),    ])  # e.g., Hull Insurance, Cargo Insurance
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.vessel_type} - {self.coverage_type} - {self.price}"

