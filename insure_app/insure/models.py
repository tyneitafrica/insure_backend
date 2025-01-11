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
    if created and instance.role == User.Role.APPLICANT :
        Applicant.objects.create(user=instance)

class Applicant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='insurance_applicant')
    phoneNumber = models.CharField(max_length=20)
    yob = models.DateField(null=True,blank=True)
    age = models.CharField(max_length=20) #will add a calculator to calculate the age
    occupation = models.CharField(max_length=100)


@receiver(post_save, sender=User)
def create_employer_profile(sender, instance, created, **kwargs):
    if created and instance.role == User.Role.ORGANISATION :
        Organisation.objects.create(user=instance)

class Organisation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organisation')
    companyName = models.CharField(max_length=100)
    phoneNumber = models.CharField(max_length=20)


class Insurance(models.Model):
    duration_choices = [
        ('1 year',  '1 year'),
        ('2 years', '2 years'),
        ('3 years', '3 years'),
        ('4 years', '4 years'),
        ('5 years', '5 years'),
    ]
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, related_name='insurance')
    title = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.CharField(choices=duration_choices, max_length=20)


class Policy(models.Model):
    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE, related_name='applicant')
    insurance = models.ForeignKey(Insurance, on_delete=models.CASCADE, related_name='insurance_policy')
    policy_number = models.CharField(max_length=20)
    start_date = models.DateField()
    end_date = models.DateField() #based on the duration choosen will be calculated from there
    premium = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20)
    isActive = models.BooleanField(default=True) # to be used to check if the policy is active or not
    


