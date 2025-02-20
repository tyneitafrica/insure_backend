# handle the helper functions
from django.core.signing import Signer, BadSignature
from rest_framework.exceptions import AuthenticationFailed
import random
import string
# import jwt
from decouple import config
# from rest_framework.response import Response
# from rest_framework import status
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.template import loader
from django.template.exceptions import TemplateDoesNotExist


def send_invoice_pay_failure_email(payment):
    invoice_number = payment.invoice_id
    policy= payment.policy
    applicant = payment.policy.applicant
    insurance = payment.policy.insurance

    # Render email template
    context = {
        "invoice_number": invoice_number,
        "applicant_name": applicant.user.get_full_name(),
        # "applicant_email": applicant.user.email,
        # "applicant_phone": applicant.phone_number,
        "policy_name": insurance.title,
        "policy_number": policy.policy_number,
        "policy_type": insurance.type,
        "policy_duration": policy.duration,
        "amount": payment.amount,
        # "benefits": benefits,
        # "transaction_id": payment.transaction_id,
        "payment_date": payment.pay_date.strftime("%Y-%m-%d"),
        "company_name": "Nyloid",
    }
    html_content = None
    try:      
        html_content = render_to_string("emails/failed_payment.html", context)
        # <!-- {% url 'download_invoice' invoice_number %} -->
    except TemplateDoesNotExist as e:
        print(f"Template not found: {e}")

    
    plain_message = ""
    
    send_mail(
        subject=f"Invoice {invoice_number} - Payment Failed",
        message=plain_message,
        from_email=config('EMAIL_HOST_USER'),
        recipient_list=[applicant.user.email],
        html_message=html_content,
    )


def send_invoice_email(payment):
    from .models import Benefit
    invoice_number = payment.invoice_id
    policy= payment.policy
    applicant = payment.policy.applicant
    insurance = payment.policy.insurance
    benefits = Benefit.objects.filter(insurance=insurance).all()
    if not benefits:
        benefits = None

    # Render email template
    context = {
        "invoice_number": invoice_number,
        "applicant_name": applicant.user.get_full_name(),
        "applicant_email": applicant.user.email,
        "applicant_phone": applicant.phone_number,
        "policy_name": insurance.title,
        "policy_number": policy.policy_number,
        "policy_type": insurance.type,
        "policy_duration": policy.duration,
        "amount": payment.amount,
        "benefits": benefits,
        "transaction_id": payment.transaction_id,
        "payment_date": payment.pay_date.strftime("%Y-%m-%d"),
        "company_name": "Nyloid",
    }
    html_content = None
    try:  
        html_content = render_to_string("emails/invoice.html", context)
        # <!-- {% url 'download_invoice' invoice_number %} -->
    except TemplateDoesNotExist as e:
        print(f"Template not found: {e}")

    
    plain_message = ""
    
    send_mail(
        subject=f"Invoice {invoice_number} - Payment Confirmation",
        message=plain_message,
        from_email=config('EMAIL_HOST_USER'),
        recipient_list=[applicant.user.email],
        html_message=html_content,
    )

# Patch policy utility function
def patch_policy(payment):
    from .models import Policy
    policy= payment.policy
    status= payment.status
    current_policy= Policy.objects.filter(id= policy.id).first()
    if not current_policy:
        return None

    if status == 'PAID':
        current_policy.status= 'ACTIVE'
        current_policy.save()
    elif status == 'FAILED':
        current_policy.status= 'CANCELLED'
        current_policy.save()

# import uuid
def generate_otp():
    characters = string.ascii_letters + string.digits
    otp = ''.join(random.choices(characters,k=7))
    # print(otp)
    return otp

# unsign cookie 
def get_user_from_cookie(cookie):
    signer = Signer()
    if not cookie:
        raise AuthenticationFailed('User ID not found in cookies')

    try:
        user_motor_details = signer.unsign(cookie)
        return user_motor_details
    except BadSignature:
        raise AuthenticationFailed('Invalid cookie signature')
    
def create_random_digit():
    res = ''.join(random.choices(string.ascii_uppercase+
                             string.digits, k=7))
    return res

def create_invoice_id():
    digit= random.randint(100000, 999999)
    invoice= f"#NL{digit}"
    return invoice


