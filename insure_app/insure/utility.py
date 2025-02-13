# handle the helper functions
from django.core.signing import Signer, BadSignature
from rest_framework.exceptions import AuthenticationFailed
import random
import string
# import jwt
# from decouple import config
# from rest_framework.response import Response
# from rest_framework import status
import uuid

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



