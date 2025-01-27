from django.shortcuts import render,get_object_or_404
from .models import *
from .serializers import *
from decouple import config
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import jwt
from django.views.decorators.csrf import csrf_exempt
from .ussd import *
import json
from django.core.signing import Signer, BadSignature
from .utility import *

# Create your views here.

#------------------------- sign up orgnisation-----------------------------------#
class SignupOrganisation(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        companyName= request.data.get('companyName')
        phoneNumber= request.data.get('phoneNumber')
        role = User.Role.ORGANISATION

        # check if the user is already registered
        try:
            if User.objects.filter(email=email).exists():
                return Response({'error': 'A user with this Email is already registered'}, status=status.HTTP_400_BAD_REQUEST)
            
            if not password:
                return Response({'error': 'Password is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            if not role:
                return Response({'error': 'Role is required'}, status=status.HTTP_400_BAD_REQUEST)

            # proceed with user creation
            serializer = UserSerializer(data={**request.data, "role": role})
            if serializer.is_valid():
                user= serializer.save()
                if user:
                    organisation= Organisation.objects.create(user=user, companyName=companyName, phoneNumber=phoneNumber)
                    organisation.save()                    
              
                return Response(
                    {
                    'message': 'User created successfully',
                    'user': serializer.data,
                                
                    }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# ------------------------------Log in organisation-----------------------------------#
class LoginOrganisation(APIView):
    def post(self, request):
        data= request.data
        email = data.get('email')
        password = data.get('password')
        try:
            # check if the user exists
            user = User.objects.filter(email=email, role=User.Role.ORGANISATION).first()
            if not user:
                return Response({'error': 'User not found, Check email and try again'}, status=status.HTTP_404_NOT_FOUND)
            
            if not user.check_password(password):
                return Response({'error': 'Incorrect Password'}, status=status.HTTP_400_BAD_REQUEST)
            
            # create a payload to contain the token
            payload = {
                'id':user.id,
                'exp':timezone.now() + timezone.timedelta(minutes=60), #token to expire after 1 hour
                'iat':timezone.now()
            }

            # create the token
            token = jwt.encode(payload, config("SECRET"), algorithm="HS256")
            # return the token as a cookie
            response = Response()
            response.set_cookie(
                key='jwt',
                value=token,
                httponly=True,
                samesite='None',
                secure=False, # to be switched to true in production
            )
            response.data = {
                'message': f'Welcome {user.first_name} ',
                'jwt':token
            }
            return response
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# ----------------------------------------------------------------- GET QUOTE for Motor Insurance----------------------------------------------------#


class CreateMotorInsuranceSession(APIView):
    def post(self, request):
        data = request.data
        # Basic user information
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        yob = data.get('yob')
        occupation = data.get('occupation')
        gender = data.get('gender')
        id_no = data.get('id')
        phoneNumber = data.get('phoneNumber')
        
        # Vehicle information
        vehicle_type = data.get('vehicle_type')
        vehicle_make = data.get('vehicle_make')
        vehicle_model = data.get('vehicle_model')
        vehicle_year = data.get('vehicle_year')
        vehicle_registration_number = data.get('vehicle_registration_number')
        cover_type = data.get('cover_type')
        evaluated = data.get('evaluated')
        vehicle_value = data.get('vehicle_value')
        cover_start_date = data.get('cover_start_date')

        try:
            # Correctly construct the dictionary
            user_details = {
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "yob": yob,
                "id_no": id_no,
                "occupation": occupation,
                "gender": gender,
                "phoneNumber": phoneNumber,
                "vehicle_type": vehicle_type,
                "vehicle_make": vehicle_make,
                "vehicle_model": vehicle_model,
                "vehicle_year": vehicle_year,
                "vehicle_registration_number": vehicle_registration_number,
                "cover_type": cover_type,
                "evaluated": evaluated,
                "vehicle_value": vehicle_value,
                "cover_start_date": cover_start_date,
            }
            
            # Serialize the dictionary to JSON
            user_details_json = json.dumps(user_details)
            sign = Signer()
            signed_data = sign.sign(user_details_json)
            # Create the response and set the cookie
            response = Response({"message": "Insurance session created successfully"}, status=status.HTTP_201_CREATED)
            response.set_cookie(
                key="user_motor_details",
                value=signed_data,
                httponly=True,
                samesite='None',
                secure=False,  # Set to True in production
                max_age=3600,  # 1 hour
            )
            # print(yob)

            return response
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)



# ----------------------------------------------------------------- GET QUOTE for personal Insurance----------------------------------------------------#

class CreatePersonalInsuranceSession(APIView):
    def post(self,request):
        data = request.data
        # Basic user information
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        yob = data.get('yob')
        occupation = data.get('occupation')
        gender = data.get('gender')
        id_no = data.get('id')
        phoneNumber = data.get('phoneNumber')
        # health details



# ----------------------------------------------------------------- Motor  Insurance Temp Data ----------------------------------------------------#

class MotorTempData(APIView):
    def post(self,request):
        data = request.data
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        phone_number = data.get('phone_number')
        id_no = data.get('id_no')
        vehicle_category = data.get('vehicle_category')
        vehicle_type = data.get('vehicle_type')
        vehicle_model = data.get('vehicle_model')
        vehicle_year = data.get('vehicle_year')
        vehicle_value = data.get('vehicle_value')
        insurance_type = data.get('insurance_type')
        is_evaluated = data.get('is_evaluated')
        evaluated_price = data.get('evaluated_price')
        vehicle_registration_number = data.get('registration_number')
        cover_start_date = data.get('cover_start_date')


        # update the fields respectively
        try:
            new_quote = MotorInsuranceTempData.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone_number=phone_number,
                id_no=id_no,
                vehicle_category=vehicle_category,
                vehicle_type=vehicle_type,
                vehicle_model=vehicle_model,
                vehicle_year=vehicle_year,
                vehicle_value=vehicle_value,
                insurance_type=insurance_type,
                is_evaluated=is_evaluated,
                evaluated_price=evaluated_price,
                vehicle_registration_number=vehicle_registration_number,
                cover_start_date=cover_start_date,
            )
            serializer = MotorInsuranceSeriliazerTemp(new_quote)

            response = Response(
                {
                "message": "Motor Insurance quote created successfully",
                "data":serializer.data  
                 },
                 
                  status=status.HTTP_201_CREATED)
            
            return response
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
# -----------------------------------------------------------------  Signup USER ----------------------------------------------------#
class SignupUser(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        role = User.Role.APPLICANT

        # Validate inputs
        if not email or not password:
            return Response({"error": "Email and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Check if email exists in the temporary data model
            temp_data = MotorInsuranceTempData.objects.filter(email=email).first()

            if temp_data:
                # If email exists in temporary data, retrieve details
                user_data = {
                    "first_name": temp_data.first_name,
                    "last_name": temp_data.last_name,
                    "email": temp_data.email,
                    "role": User.Role.APPLICANT
                }

                # Check if a user already exists with this email
                if User.objects.filter(email=email).exists():
                    return Response({"error": "A user with this email already exists, Proceed to login"}, status=status.HTTP_400_BAD_REQUEST)

                # Add password and create the user with the retrieved details
                user_data["password"] = password
                serializer = UserSerializer(data=user_data)

                if serializer.is_valid():
                    user = serializer.save()

                    # Add additional details to Applicant model
                    new_applicant = Applicant.objects.get(user=user)
                    new_applicant.id_no = temp_data.id_no
                    new_applicant.phone_number = temp_data.phone_number
                    new_applicant.save()

                    # Delete temporary data after successful account creation
                    # temp_data.delete()

                    return Response(
                        {
                            "message": "Account created successfully",
                            "user": serializer.data,
                        },
                        status=status.HTTP_201_CREATED,
                    )
                return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

            else:
                # Direct sign-up (no temporary data found)
                data = request.data
                id_no = data.get('id_no')
                phone_number = data.get('phone_number')

                # Validate direct sign-up fields
                if not email or not password:
                    return Response({"error": "Email and password are required"}, status=status.HTTP_400_BAD_REQUEST)

                # Check if user already exists
                existing_user = User.objects.filter(email=email).first()
                if existing_user:
                    return Response({"error": "User already registered, Please login."}, status=status.HTTP_400_BAD_REQUEST)

                # Create new user if not found
                serializer = UserSerializer(data={**request.data, "role": role})
                if serializer.is_valid():
                    user = serializer.save()

                    # Add details to the Applicant model
                    new_applicant = Applicant.objects.get(user=user)
                    new_applicant.id_no = id_no
                    new_applicant.phone_number = phone_number
                    new_applicant.save()

                    return Response(
                        {
                            "message": "Account created successfully",
                            "user": serializer.data,
                        },
                        status=status.HTTP_201_CREATED,
                    )

                return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# -----------------------------------------APPLICANT LOGIN ----------------------------------#

class LoginApplicant(APIView):
    def post(self,request):
        email = request.data['email']
        password = request.data['password']
        
        try:
        # check if the user exists
            user = User.objects.filter(email=email, role=User.Role.APPLICANT).first()
            if not user:
                return Response({'error': 'User not found, Check email and try again'}, status=status.HTTP_404_NOT_FOUND)
            

            if not user.check_password(password):
                return Response({'error': 'Incorrect Password'}, status=status.HTTP_400_BAD_REQUEST)
            
            # create a payload to contain the token
            payload = {
                'id':user.id,
                'exp':timezone.now() + timezone.timedelta(minutes=60), #token to expire after 1 hour
                'iat':timezone.now()
            }

            # create the token 
            token = jwt.encode(payload,config("SECRET"),algorithm="HS256")
            
            # return the token as a cookie
            response = Response()
            response.set_cookie(
                key='jwt',
                value=token,
                httponly=True,
                samesite='None',
                secure=False, # to be switched to true in production
            )
            response.data = {
                'message': f'Welcome {user.first_name} ',
                'jwt':token
            }
            return response
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# -----------------------------------------APPLICANT LOGOUT ----------------------------------#

class LogoutApplicant(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message': 'Logged out successfully'
        }
        return response



