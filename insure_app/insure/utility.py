# handle the helper functions
import random
import string

# import uuid
def generate_otp():
    characters = string.ascii_letters + string.digits
    otp = ''.join(random.choices(characters,k=7))
    # print(otp)
    return otp