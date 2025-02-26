from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
# from django.core.validators import RegexValidator, MinLengthValidator,MaxLengthValidator
from datetime import timedelta
from .manager import CustomUserManager
from .utility import generate_otp
from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal
from datetime import date
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
from .utility import *
from cloudinary_storage.storage import RawMediaCloudinaryStorage
from django.contrib.auth.models import User
import uuid
from django.contrib.auth.models import User



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
    national_id  = models.ImageField(upload_to='national_id_images/', null=True, blank=True,storage=RawMediaCloudinaryStorage())
    driving_license = models.ImageField(upload_to='driving_license_images/', null=True, blank=True,storage=RawMediaCloudinaryStorage())
    valuation_report = models.ImageField(upload_to='valuation_report_images/', null=True, blank=True,storage=RawMediaCloudinaryStorage())
    kra_pin_certificate = models.ImageField(upload_to='kra_pin_certificate_images/', null=True, blank=True,storage=RawMediaCloudinaryStorage())
    log_book = models.ImageField(upload_to='log_book_images/', null=True, blank=True,storage=RawMediaCloudinaryStorage()) 
    is_uploded = models.BooleanField(default=False)
    
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
    insurance_image = models.ImageField(upload_to='insurance_images/', null=True, blank=True, storage=RawMediaCloudinaryStorage()) #will handle profile image of a insurance company
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    title = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} {self.type} {self.description} {self.organisation} {self.insurance_image.url}"



class MotorInsurance(models.Model):
    COVER_TYPE_CHOICES = [
        ("Comprehensive", "Comprehensive"),
        ("Third Party Only", "Third Party Only"),
        ("Third Party Fire and Theft", "Third Party Fire and Theft"),
    ]

    insurance = models.ForeignKey(Insurance, on_delete=models.CASCADE, related_name='motor_details')
    cover_type = models.CharField(max_length=100, choices=COVER_TYPE_CHOICES)

    def __str__(self):
        return f"{self.cover_type} - {self.insurance}"

# represents the diffrent vehicle types we have 
class VehicleType(models.Model):
    VEHICLE_TYPE_CHOICES = [
        ("Private", "Private"),
        ("Commercial", "Commercial"),
        ("Public_Service", "Public_Service"),
    ]
    vehicle_category = models.CharField(max_length=100,choices=VEHICLE_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.vehicle_category}"

# each vehicle_type is assocated to a specific risk type 
class RiskType(models.Model):
    RISK_TYPE_CATEGORIES = [
        ("Motor_Private","Motor_Private"), #specific to private vehicles
        ("General_Cortage","General_Cortage"), # specifc to commercial vehicles
        ("Institutional_Vehicles","Institutional_Vehicles"),
        ("Online_Taxis","Online_Taxis"),
        ("Own_Goods","Own_Goods"),
        ("Chaffer_Driven","Chaffer_Driven"), #specific to public service 
        ("Chaffer_driven_taxi","Chaffer_driven_taxi"),
        ("Motor_Psv","Motor_Psv")
    ]
    vehicle_type = models.ForeignKey(VehicleType,on_delete=models.CASCADE,related_name="risk_type")
    risk_name = models.CharField(max_length=100,choices=RISK_TYPE_CATEGORIES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.vehicle_type} {self.risk_name}"

# the rate ranges is associated to a specific risk type and motro insurance cover

class WeightCategory(models.Model):
    weight_category = models.CharField(max_length=100,null=True,blank=True)

    def __str__(self):
        return f"{self.weight_category}"
class RateRange(models.Model):  
    motor_insurance = models.ForeignKey(MotorInsurance, on_delete=models.CASCADE, related_name='rate_ranges')
    risk_type = models.ForeignKey(RiskType,on_delete=models.CASCADE) #to add related name later 
    usage_category = models.CharField(max_length=50, null=True,blank=True, choices=[
        ('Fleet', 'Fleet'),
        ('Standard', 'Standard'),
    ])
    weight_category = models.ManyToManyField(WeightCategory,max_length=50,blank=True)
    max_car_age = models.IntegerField()  # Maximum age threshold (e.g., 5 years)
    min_value = models.DecimalField(max_digits=15, decimal_places=2,db_index=True)  # Minimum vehicle value for this range
    max_value = models.DecimalField(max_digits=15, decimal_places=2,db_index=True)  # Maximum vehicle value for this range
    rate = models.DecimalField(max_digits=5, decimal_places=2,db_index=True)  # Rate in percentage
    min_sum_assured = models.DecimalField(max_digits=15, decimal_places=2)  # Minimum premium for this range
    
    # class Meta:
    #     unique_together = ("motor_insurance", "min_value", "max_value",'min_year','max_year')  # Prevent duplicate ranges for the same plan

    def __str__(self):
        return f"{self.motor_insurance} - {self.risk_type} {self.max_car_age} - {self.min_value} to {self.max_value}"
    
    def clean(self):
        if self.max_value <= self.min_value:
            raise ValidationError("Max value must be greater than min value")
        # if self.min_year >= self.max_year:
        #         raise ValidationError("Min year must be less than max year")
        # if self.max_year <= self.min_year:
        #     raise ValidationError("Max year must be greater than min year")

# apply extra charges depending on the insurance poliy choosen (will include eg.excess protector, pvt)
class ExcessCharges(models.Model):
    motor_insurance = models.ForeignKey(MotorInsurance, on_delete=models.CASCADE, related_name='excess_charges')
    limit_of_liability = models.CharField(max_length=100)
    excess_rate = models.DecimalField(max_digits=5, decimal_places=2)
    min_price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.limit_of_liability} - {self.min_price} - {self.excess_rate}"

class OptionalExcessCharge(models.Model): #to be factored in during calculation of premium 
    insurance = models.ForeignKey(Insurance, on_delete=models.CASCADE, related_name="optional_excess_charges")
    under_21_age_charge = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    under_1_year_experience_charge = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    def __str__(self):
        return f"{self.insurance} {self.under_1_year_experience_charge} {self.under_21_age_charge}"


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

# Benefit Model will handle the benefits in relation to a speific insurance 
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
    cover_type= models.CharField(max_length=100, null=True, blank=True)
    risk_name= models.CharField(max_length=100, null=True, blank=True)
    age= models.IntegerField(null=True, blank=True)
    policy_number = models.CharField(max_length=200, unique=True)
    total_amount= models.FloatField(blank=True, null=True)
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
    invoice_id= models.CharField(max_length=100, unique=True, null=True, blank=True)
    api_ref_id= models.CharField(max_length=100, unique=True, null=True, blank=True)
    transaction_id= models.CharField(max_length=100, unique=True, null=True, blank=True)
    merchant_request_id= models.CharField(max_length=100, unique=True, null=True, blank=True)
    checkout_request_id= models.CharField(max_length=100, unique=True, null=True, blank=True)
    amount= models.FloatField(max_length=100, null=True, blank=True)
    phone_number= models.CharField(max_length=20, null=True, blank=True)
    pay_method= models.CharField(max_length=250, null=True, blank=True)
    pay_date= models.DateTimeField(default=timezone.now)
    description= models.TextField(null=True, blank=True)
    status= models.CharField(max_length=20, default="PENDING")
    result_desc= models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"{self.invoice_id} - {self.amount} - {self.pay_method} - {self.pay_date}"

@receiver(post_save, sender=Payment)
def send_invoice_on_success(sender, instance, **kwargs):
    print(f"Payment status updated: {instance.status}")
    if instance.status == "PAID":
        print(f"Sending invoice for payment ID: {instance.id}")
        patch_policy(instance)
        send_invoice_email(instance)        

    elif instance.status == "FAILED":
        print("Payment status is not 'PAID'. No invoice sent.")
        patch_policy(instance)
        send_invoice_pay_failure_email(instance)


# to hold user data temporary   
class MotorInsuranceTempData(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    id_no = models.CharField(max_length=20)
    yob = models.DateField()
    age = models.IntegerField(default=0)
    # motor details
    vehicle_category = models.CharField(max_length=100,choices=[('Private','Private'),('Commercial','Commercial'),('Public Service','Public Service')])
    vehicle_type = models.CharField(max_length=100)
    vehicle_model = models.CharField(max_length=100)
    vehicle_year = models.IntegerField()
    vehicle_age = models.IntegerField()
    vehicle_value = models.DecimalField(max_digits=100, decimal_places=2)
    cover_start_date = models.DateField()
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



# Marine Insurance Data Model
class BasicInfo(models.Model):
    ENTITY_TYPE_CHOICES = [
        ('Individual', 'Individual'),
        ('Company', 'Company'),
    ]
    full_name = models.CharField(max_length=100,null=True, blank=True)  #to be filled if individual
    company_name = models.CharField(max_length=100, blank=True, null=True) #to be filled if company
    registration_number = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    id_no = models.CharField(max_length=20)
    kra_pin = models.CharField(max_length=20)                           
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    occupation = models.CharField(max_length=100) #represents the details of the person seeking the insurance
    custom_occupation = models.CharField(max_length=100, blank=True, null=True)
    coverage_type = models.CharField(max_length=50) #will bw passed based on the data provided by the frontend(steve)
    entity_type = models.CharField(max_length=20, choices=ENTITY_TYPE_CHOICES)

    def __str__(self):
        return f"{self.full_name} - {self.email}"
    

class GoodsInfo(models.Model):
    good_type = models.CharField(max_length=50) # eg perishable goods
    sub_type = models.CharField(max_length=50) #eg flowers
    quantity = models.CharField(max_length=50) # eg 10
    unit = models.CharField(max_length=50) #eg kg,ltr
    # packaging = models.CharField(max_length=50)
    # packaging_spec = models.CharField(max_length=50)
    # category = models.CharField(max_length=50)
    good_value = models.DecimalField(max_digits=15, decimal_places=2) #value of the goods carried
    description = models.TextField()

    def __str__(self):
        return f"{self.good_type} - {self.sub_type}"
    

    def __str__(self):
        return f"Base Premium: {self.base_premium}, Total Premium: {self.total_premium}"
class ConveyanceInfo(models.Model):
    TRANSPORT_MODE_CHOICES = [
        ('Sea', 'Sea'),
        ('Air', 'Air'),
    ]
    transport_mode = models.CharField(max_length=50, choices=TRANSPORT_MODE_CHOICES)
    carrier_name = models.CharField(max_length=100,null=True, blank=True)
    vessel_type = models.CharField(max_length=100,null=True, blank=True)
    vessel_name = models.CharField(max_length=100,null=True, blank=True)
    voyage_number = models.CharField(max_length=100,null=True, blank=True)
    shipment_date = models.DateField()
    arrival_date = models.DateField()
    tracking_number = models.CharField(max_length=100,null=True,blank=True)
    additional_details = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.vessel_name} - {self.voyage_number}"
class TransitPoint(models.Model):
    country = models.CharField(max_length=50,null=True,blank=True)
    port = models.CharField(max_length=50,null=True,blank=True)
    estimated_days = models.CharField(max_length=50,null=True,blank=True)

    def __str__(self):
        return f"{self.country} - {self.port}"

class RouteInfo(models.Model):
    origin_country = models.CharField(max_length=50) #represents country of origin 
    origin_port = models.CharField(max_length=50)
    destination_country = models.CharField(max_length=50)#represents country of destination
    destination_port = models.CharField(max_length=50)
    transit_points = models.ManyToManyField(TransitPoint) 
    route_notes = models.TextField(null=True, blank=True) #no applicable unless required

    def __str__(self):
        return f"{self.origin_port} to {self.destination_port}"
    

class MarineInsuranceApplication(models.Model):
    STATUS_CHOICES = [
        ('Submitted', 'Submitted'),
        ('Reviewed', 'Reviewed'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Cancelled', 'Cancelled')
    ]
    user =  models.ForeignKey(User, on_delete=models.CASCADE, related_name='marine_applications')
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    basic_info = models.OneToOneField(BasicInfo, on_delete=models.CASCADE, related_name='marine_app')
    goods_info = models.OneToOneField(GoodsInfo, on_delete=models.CASCADE, related_name='marine_appliion')
    conveyance_info = models.OneToOneField(ConveyanceInfo, on_delete=models.CASCADE, related_name='marine_appion')
    route_info = models.OneToOneField(RouteInfo, on_delete=models.CASCADE, related_name='marine_applicion')
    # benefits_info = models.OneToOneField(BenefitsInfo, on_delete=models.CASCADE, related_name='marine_application')
    quote_reference = models.CharField(max_length=50, unique=True)
    submission_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')      

    def gen_reference(self):
        self.quote_reference = generate_marine_reference_number()
        self.save()


    def __str__(self):
        return f"{self.quote_reference} - {self.status}"