from django.db import models
from django.contrib.auth.models import AbstractUser
from .manager import CustomUserManager
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import timedelta
from django.utils import timezone
from .utility import generate_otp

# Create your models here.

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        ORGANISATION = "ORGANISATION", "ORGANISATION"
        APPLICANT = "APPLICANT", "APPLICANT"


    role = models.CharField(max_length=20, choices=Role.choices ,default=Role.APPLICANT)
    otp = models.CharField(max_length=7, null=True, blank=True)
    otp_expiration = models.DateTimeField(null=True, blank=True)
    email = models.EmailField(unique=True)
    
    username=None
    USERNAME_FIELD = "email"
   
    REQUIRED_FIELDS=[]

    objects=CustomUserManager()

    def set_otp(self):
        self.otp = str(generate_otp())
        self.otp_expiration = timezone.now()
        self.save()

    def is_otp_valid(self):
        if self.otp_expiration:
            return timezone.now() < self.otp_expiration + timedelta(minutes=2)
        return False

    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.email},{self.first_name},{self.last_name},{self.role}"

# set up the receivor 
@receiver(post_save, sender=User)
def create_employer_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == User.Role.APPLICANT:
            Applicant.objects.create(user=instance)
        elif instance.role == User.Role.ORGANISATION :
            Organisation.objects.create(user=instance)

class Applicant(models.Model):
    gender_choices = [
        ( "Male","Male"),
        ("Female","Female")
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='insurance_applicant')
    phoneNumber = models.CharField(max_length=20)
    yob = models.DateField(null=True,blank=True)
    id_no = models.CharField(max_length=20,unique=True)
    age = models.CharField(max_length=20) #will add a calculator to calculate the age
    occupation = models.CharField(max_length=100)
    gender = models.CharField(choices=gender_choices,max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_age(self):
        today = timezone.now().date()
        born = self.yob
        age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
        return age

    def __str__(self):
        return f"{self.user},{self.phoneNumber},{self.yob},{self.id_no},{self.age},{self.occupation},{self.gender}"



class Organisation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organisation')
    companyName = models.CharField(max_length=100)
    phoneNumber = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.companyName},{self.phoneNumber}"


class Insurance(models.Model):
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, related_name='insurance',null=True,blank=True)
    insurance_type = models.CharField(max_length=100) #can be either motor,health,etc..
    title = models.CharField(max_length=100)
    cover_type = models.CharField(max_length=100) #can be comprehensive,third_party,etc...
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title},{self.insurance_type},{self.cover_type},{self.description},{self.price}"


class Benefit(models.Model):
    insurance = models.ForeignKey(Insurance, on_delete=models.CASCADE, related_name="benefits")
    limit_of_liability = models.CharField(max_length=100)
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.limit_of_liability} - {self.price}"

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
    policy_number = models.CharField(max_length=100, unique=True)  #will autogenerate a policy number for easy tracking
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    duration = models.IntegerField(default=12)  # Duration in months
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.end_date:
            self.end_date = self.start_date + timedelta(days=self.duration * 30)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.policy_number} - {self.status}"

# proceed to payment
class Payment(models.Model):
    policy = models.ForeignKey(Policy,on_delete=models.CASCADE)
    # to add the other details below 