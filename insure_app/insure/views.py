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

# ====Function to get user from token=======================================================================                          
def get_user_from_token(request):
    token = request.COOKIES.get('jwt')
    if not token:
        raise AuthenticationFailed("Token not in request header")

    try:
        payload = jwt.decode(token, config("SECRET"), algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        response = Response({'error': 'Unauthenticated user'}, status=status.HTTP_401_UNAUTHORIZED)
        response.delete_cookie('jwt')
        return response

    user = User.objects.filter(id=payload['id']).first()
    if not user:
        response = Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        response.delete_cookie('jwt')
        return response

    return user


# -----------------------------------------------------------------  Signup USER ----------------------------------------------------#
class SignupUser(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        id_no = request.data.get('id_no')
        phone_number = request.data.get('phone_number')
        role = User.Role.APPLICANT

        try:
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
                secure=False,   #to be switched to true in production
                max_age=3600, 
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
                    organisation= Organisation.objects.create(user=user, company_name=companyName, phone_number=phoneNumber)
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


class HealthInsuaranceSession(APIView):
    def post(self, request):
        try:
            data = request.data
            # Basic user information
            name= data.get('name')
            dob= data.get('dob')
            national_id= data.get('national_id')
            occupation= data.get('occupation')
            phone_number= data.get('phone_number')
            gender= data.get('gender')
            coverage_amount= data.get('coverage_amount')
            coverage_type= data.get('coverage_type')
            is_travel_related= data.get('is_travel_related')
            is_covered= data.get('is_covered')

            # HealthLifestyle information
            pre_existing_condition = data.get('pre_existing_condition', False)
            high_risk_activities = data.get('high_risk_activities', False)
            medication = data.get('medication', False)
            mode_of_transport = data.get('mode_of_transport', None)
            smoking = data.get('smoking', False)
            past_claim = data.get('past_claim', False)
            stress_level = data.get('stress_level', False)
            family_history = data.get('family_history', False)
            allergies = data.get('allergies', False)
            mental_health = data.get('mental_health', False)

            if not all([name, dob, national_id, occupation, phone_number,gender,coverage_amount, coverage_type]):
                return Response({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)

            if is_travel_related == 'true':
                is_travel_related = True
            else:
                is_travel_related = False

            if is_covered == 'true':
                is_covered = True
            else:
                is_covered = False

            available_quote= HealthInsuaranceQuoteRequest.objects.filter(national_id=national_id).first()

            if available_quote:
                # available_quote.delete()
                new_quote_request= available_quote
            
            else:            
                # post data        
                new_quote_request= HealthInsuaranceQuoteRequest.objects.create(
                                                                name= name, 
                                                                national_id=national_id, 
                                                                dob=dob, occupation=occupation, 
                                                                phone_number=phone_number, 
                                                                gender=gender, 
                                                                coverage_amount= coverage_amount,
                                                                coverage_type=coverage_type,
                                                                is_travel_related=is_travel_related,
                                                                is_covered=is_covered
                                                            )
                new_quote_request.save()

            if new_quote_request:
                    
                new_lifestyle= HealthLifestyle.objects.create(health_insuarance_quote_request=new_quote_request,
                                                pre_existing_condition=pre_existing_condition,
                                                high_risk_activities=high_risk_activities,
                                                medication=medication,
                                                mode_of_transport=mode_of_transport,
                                                smoking=smoking,
                                                past_claim=past_claim,
                                                stress_level=stress_level,
                                                family_history=family_history,
                                                allergies=allergies,
                                                mental_health=mental_health
                                                )
                new_lifestyle.save()
            
            if new_lifestyle:
                response_data= {
                    "name": name,
                    "national_id": national_id,
                    "dob": dob,
                    "occupation": occupation,
                    "phone_number": phone_number,
                    "gender": gender,
                    "coverage_amount": coverage_amount,
                    "coverage_type": coverage_type,
                    "is_travel_related": is_travel_related,
                    "is_covered": is_covered,
                    "pre_existing_condition": pre_existing_condition,
                    "high_risk_activities": high_risk_activities,
                    "medication": medication,
                    "mode_of_transport": mode_of_transport,
                    "smoking": smoking,
                    "past_claim": past_claim,
                    "stress_level": stress_level,
                    "family_history": family_history,
                    "allergies": allergies,
                    "mental_health": mental_health
                }
                # return the response in a cookie
                payload = {
                'data':response_data,
                'exp':timezone.now() + timezone.timedelta(minutes=60), #token to expire after 1 hour
                'iat':timezone.now()
                }
                # create the token 
                token = jwt.encode(payload,config("SECRET"),algorithm="HS256")

                response = Response()
                response.set_cookie(
                    key='healthsession',
                    value=token,
                    httponly=True,
                    samesite='None',
                    secure=False, # to be switched to true in production
                )
                response.data = {
                    'message': f'Welcome {name} ',
                    'data':response_data
                }
                return response
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# =======================Route to get quotes for authenticated applicants=====================================================
class GetHealthInsuranceQuote(APIView):
    def get(self, request):
        try:
            # Get user from login cookie
            user = get_user_from_token(request)
            if not user:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

            if user.role != User.Role.APPLICANT:
                return Response({'error': 'Unauthorized user'}, status=status.HTTP_401_UNAUTHORIZED)
            
            applicant= Applicant.objects.filter(user=user).first()
            # Get user quote
            user_quote= HealthInsuaranceQuoteRequest.objects.filter(national_id=applicant.id_no).first()
            if not user_quote:
                return Response({'error': 'Quote not found'}, status=status.HTTP_404_NOT_FOUND)
            
            # Get user lifestyle
            user_lifestyle= HealthLifestyle.objects.filter(health_insuarance_quote_request=user_quote).all()

            if not user_lifestyle:
                return Response({'error': 'Lifestyle not found'}, status=status.HTTP_404_NOT_FOUND)
            
            # serialize user lifestyle
            serializer= HealthLifestyleSerializer(user_lifestyle, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)