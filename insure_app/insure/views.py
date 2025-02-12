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
import datetime
from django.db import transaction


# Create your views here.
# unsign cookie 
# ====Function to get user from token=======================================================================                          
from rest_framework.exceptions import AuthenticationFailed
import jwt
from django.core.signing import Signer, BadSignature
from decouple import config
from .models import User, Organisation

# Load secret key from environment variables
SECRET_KEY = config("SECRET")

def get_user_from_token(request):
    token = request.COOKIES.get('jwt')
    if not token:
        raise AuthenticationFailed("Token not in request header")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed("Token has expired. Please log in again.")
    except jwt.InvalidTokenError:
        raise AuthenticationFailed("Invalid token.")

    user = User.objects.filter(id=payload.get('id')).first()
    if not user:
        raise AuthenticationFailed("User not found.")

    return user

def get_user_from_cookie(cookie):
    signer = Signer()
    
    if not cookie:
        raise AuthenticationFailed('User ID not found in cookies')

    try:
        user_motor_details = signer.unsign(cookie)
        return user_motor_details
    except BadSignature:
        raise AuthenticationFailed('Invalid cookie signature')

def get_organisation_from_user(user):
    organisation = Organisation.objects.filter(user=user).first()
    if not organisation:
        raise AuthenticationFailed("Organisation not found.")

    return organisation

def get_applicant_from_user(user):
    applicant = Applicant.objects.filter(user=user).first()
    if not applicant:
        raise AuthenticationFailed("User not found.")

    return applicant



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
                'jwt':token,
                'user': UserSerializer(user).data
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
        yob = data.get('yob') #2016-2-13
        occupation = data.get('occupation')
        gender = data.get('gender')
        id_no = data.get('id')
        phoneNumber = data.get('phoneNumber')
        
        # Vehicle information
        vehicle_type = data.get('vehicle_type') #saloon,bus,commercial etc...
        vehicle_make = data.get('vehicle_make') # hachback et
        vehicle_model = data.get('vehicle_model') # probox,n-series,f-series
        vehicle_year = data.get('vehicle_year') # 2017,2016 
        vehicle_registration_number = data.get('vehicle_registration_number')
        cover_type = data.get('cover_type') #comprehesive,thirdparty ,thirdparty and fire
        vehicle_value = data.get('vehicle_value') #according to the recent evaluation 
        cover_start_date = data.get('cover_start_date')
        experience = data.get('experience')

        def calculate_user_age(yob):
            if isinstance(yob, str):  # Check if yob is a string
                yob = datetime.datetime.strptime(yob, "%Y-%m-%d").year  # Convert to datetime and extract year
            
            current_year = datetime.datetime.now().year
            age = current_year - yob
            # print(age) 21
            return age
        
        def car_age(vehicle_year):
            if isinstance(vehicle_year, str):  # Check if yob is a string
                vehicle_year = datetime.datetime.strptime(vehicle_year, "%Y-%m-%d").year  # Convert to datetime and extract year

            current_year = datetime.datetime.now().year
            car_age = current_year - vehicle_year
            # print(car_age)
            return car_age
        
        try:
            # Correctly construct the dictionary
            user_details = {
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "age": calculate_user_age(yob) ,
                "id_no": id_no,
                "occupation": occupation,
                "gender": gender,
                "phoneNumber": phoneNumber,
                "vehicle_type": vehicle_type,
                "vehicle_make": vehicle_make,
                "vehicle_model": vehicle_model,
                "vehicle_year": vehicle_year,
                "vehicle_age": car_age(vehicle_year),
                "vehicle_registration_number": vehicle_registration_number,
                "cover_type": cover_type,
                "vehicle_value": vehicle_value,
                "cover_start_date": cover_start_date,
                "experience": experience
            }
            
            # Serialize the dictionary to JSON
            user_details_json = json.dumps(user_details)
            sign = Signer()
            signed_data = sign.sign(user_details_json)
            # Create the response and set the cookie
            response = Response({"message": "Motor Insurance session created successfully",
                                 }, status=status.HTTP_201_CREATED)
            response.set_cookie(
                key="user_motor_details",
                value=signed_data,
                httponly=True,
                samesite='None',
                secure=True,  # Set to True in production
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

# ----------------------------------------------------------------- GET QUOTE health Insurance----------------------------------------------------#
class HealthInsuaranceSession(APIView):
    def get(self, request):
        try:
            user= get_user_from_token(request)
            if not user:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            
            if user.role != user.Role.ORGANISATION:
                return Response({'error': 'You are not authorized to access this page'}, status=status.HTTP_401_UNAUTHORIZED)
            
            health_insurance_quote= HealthLifestyle.objects.all()
            if not health_insurance_quote:
                return Response({'error': 'No quotes found'}, status=status.HTTP_404_NOT_FOUND)
            
            serializer= HealthLifestyleSerializer(health_insurance_quote, many=True)
            
            return Response(serializer.data, status=status.HTTP_200_OK)             

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def post(self, request):
        try:
            data = request.data
            # Basic user information
            firstname= data.get('firstname')
            lastname= data.get('lastname')
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

            if not all([firstname, dob, national_id, occupation, phone_number,gender,coverage_amount, coverage_type]):
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
                                                                first_name= firstname, 
                                                                last_name=lastname,
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
                    "firstname": firstname,
                    "lastname": lastname,                    "national_id": national_id,
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
                    'message': f'Welcome {firstname} ',
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
        
# ----------------------------------------------------------------- Upload insurance policy ----------------------------------------------------#
class UploadMotorInsurance(APIView):
    
    def get(self, request):
        try:
            user = get_user_from_token(request)
            if not user:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

            # # Retrieve organisation associated with the user
            organisation = get_organisation_from_user(user)
            print(organisation)
            
            # Query Insurance for Motor type
            insurance_queryset = Insurance.objects.filter(organisation=organisation, type='Motor')
            if not insurance_queryset.exists():
                return Response({'message': 'No Motor insurance policies found'}, status=status.HTTP_404_NOT_FOUND)
            
            
            # # Query MotorInsurance and related data
            motor_insurances = MotorInsurance.objects.filter(insurance__in=insurance_queryset).select_related('insurance')
            if not motor_insurances.exists():
                return Response({'message': 'No Motor insurance details found'}, status=status.HTTP_404_NOT_FOUND)
            
            
            serializer = MotorInsuranceSerializer(motor_insurances, many=True)
            
            # Return the response
            return Response({
                'message': 'Motor insurance policies retrieved successfully',
                'data': serializer.data,
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    
    def post(self, request):
        data = request.data
        type = 'Motor'
        title = data.get('title')
        description = data.get('description')
        company_name = data.get("company_name")

        try:
            # Retrieve user from token
            user = get_user_from_token(request)

            # Retrieve organisation associated with the user
            organisation = get_organisation_from_user(user)

            # Create a new insurance entry
            new_insurance = Insurance.objects.create(
                organisation=organisation,
                type=type,
                title=title,
                description=description,
                company_name=company_name
            )

            response = Response({
                'message': 'Insurance created successfully',
                'data': {
                    'id': new_insurance.id,
                    "company":new_insurance.company_name,
                    'type': new_insurance.type,
                    'title': new_insurance.title,
                    'description': new_insurance.description
                }
            }, status=status.HTTP_201_CREATED)

            response.set_cookie(
                key='motor_insurance',
                value=new_insurance.id,
                httponly=True,
                samesite='None',
                secure=False,
                max_age=3600  # 1 hour
            )
            return response
        except AuthenticationFailed as e:
            return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class MotorInsuranceDetails(APIView):
    def post(self, request):
        data = request.data
        cover_type = data.get('cover_type') #comprehensive 

        # List of rate ranges
        rate_ranges = data.get("rate_ranges", [])  # Expecting a list of dictionaries
        excess_charges = data.get("excess_charges", [])  # Expecting a list of dictionaries

        try:
            get_insurance_id = request.COOKIES.get('motor_insurance')
            if not get_insurance_id:
                return Response({'error': 'Insurance cookie not found'}, status=status.HTTP_400_BAD_REQUEST)

            insurance = Insurance.objects.get(id=get_insurance_id)

            with transaction.atomic():
                # Create motor insurance
                upload = MotorInsurance.objects.create(
                    insurance=insurance,
                    cover_type=cover_type,
                )

                # Create rate ranges
                for rate_data in rate_ranges:
                    RateRange.objects.create(
                        motor_insurance=upload,
                        min_value=rate_data.get("min_value"), #2m
                        max_value=rate_data.get("max_value"), #4m
                        min_year=rate_data.get("min_year"), #below 5 yrs
                        max_year=rate_data.get("max_year"), #below 16 yrs
                        min_premium=rate_data.get("min_premium"),
                        vehicle_type=rate_data.get("vehicle_type"), #saloon ,bus ,
                        rate=rate_data.get("rate"), #2.5
                    )

                # Create excess charges
                for excess_data in excess_charges:
                    ExcessCharges.objects.create(
                        motor_insurance=upload,
                        limit_of_liability=excess_data.get("limit_of_liability"), #breakdown , 
                        excess_rate=excess_data.get("excess_rate"),
                        min_price=excess_data.get("min_price"), #1000
                        description=excess_data.get("description"),
                    )

            # Return the created data
            response_data = MotorInsuranceSerializer(upload).data
            return Response(response_data, status=status.HTTP_201_CREATED)

        except Insurance.DoesNotExist:
            return Response({'error': 'Insurance not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
# step3
# additional charges where applicable
class Additionalcharge(APIView):
    
    def get(self,request):
        try:
            get_insurance_id = request.COOKIES.get('motor_insurance')
            if not get_insurance_id:
                return Response({'error': 'Insurance cookie not found'}, status=status.HTTP_400_BAD_REQUEST)

            insurance = Insurance.objects.get(id=get_insurance_id)

            # Retrieve additional charges for the insurance
            additional_charges = OptionalExcessCharge.objects.filter(insurance=insurance)

            # Serialize the additional charges
            serializer = AdditionalChargesSerializer(additional_charges, many=True)

            return Response({
                "message": "Additional charges retrieved successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        except Insurance.DoesNotExist:
            return Response({'error': 'Insurance not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post (self,request):
        data = request.data
        is_under_21 = data.get('is_under_21')
        is_unexperienced = data.get('is_unexperienced')
        try:
            get_insurance_id = request.COOKIES.get('motor_insurance')
            
            if not get_insurance_id:
                return Response({'error': 'Insurance cookie not found'}, status=status.HTTP_400_BAD_REQUEST)

            insurance = Insurance.objects.get(id=get_insurance_id)


            new_charge = OptionalExcessCharge.objects.create(
                insurance = insurance,
                under_21_age_charge=is_under_21,
                under_1_year_experience_charge=is_unexperienced
            )

            serializer = AdditionalChargesSerializer(new_charge)

            return Response({
                "message":"Additional charge created successfully",
                "data":serializer.data
            }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            


 

# step4
class MotorInsuranceBenefits(APIView):
    def post (self,request):
        data = request.data
        limit_of_liability = data.get('limit_of_liability')
        rate = data.get('rate')
        price = data.get('price')  
        description = data.get('description') 

        try:
            get_insurance_id = request.COOKIES.get('motor_insurance')
            if not get_insurance_id:
                return Response({'error': 'Insurance cookie not found'}, status=status.HTTP_400_BAD_REQUEST)

            # query insurance
            insurance = Insurance.objects.get(id=get_insurance_id)

            new_benefit = Benefit.objects.create(
                insurance=insurance,
                limit_of_liability=limit_of_liability,
                rate=rate,
                price=price,
                description=description 
            )

            return Response({
                "message":"Benefits created successfully",
                "data":{
                    "id":new_benefit.id,
                    "limit_of_liability":new_benefit.limit_of_liability,
                    "rate":new_benefit.rate,
                    "price":new_benefit.price,
                    "description":new_benefit.description
                }
            })      
        except Insurance.DoesNotExist:
            return Response({'error': 'Insurance not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class FilterMotorInsurance(APIView):
    def get(self, request):
        # try:
        # Retrieve and decode the cookie
        signed_data = request.COOKIES.get('user_motor_details')  # Retrieves the user data previously stored in the cookie
        if not signed_data:
            return Response({'error': 'No session data found in cookies'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Unsigned and deserialize the cookie data
        sign = Signer()
        user_details_json = sign.unsign(signed_data)
        user_details = json.loads(user_details_json)
        
        # Extract filter parameters from the cookie
        vehicle_type = user_details.get('vehicle_type')  # e.g., saloon, bus
        vehicle_model = user_details.get('vehicle_model')  # e.g., Probox, Sienta
        cover_type = user_details.get('cover_type')  # e.g., comprehensive
        vehicle_value = user_details.get('vehicle_value')  # e.g., 4.5m
        vehicle_age = user_details.get('vehicle_age')  # e.g., 3 years
        age = user_details.get('age')  # e.g., 25 years
        insurance_type = "Motor"  # We're filtering for motor insurance
        experience = user_details.get('experience')

        print(vehicle_value)
        print(vehicle_type)
        print(age)
        print(cover_type)

        # Step 1: Query the Insurance model for the relevant policies
        insurance_queryset = Insurance.objects.filter(type=insurance_type)
        
        if not insurance_queryset.exists():
            return Response({'message': 'No insurance policies found for the given type'}, status=status.HTTP_404_NOT_FOUND)
        
        # Step 2: Query the MotorInsurance model for the specific details
        motor_insurances = MotorInsurance.objects.filter(insurance__in=insurance_queryset, cover_type=cover_type)
        # print(motor_insurances)
        
        # Step 3: Filter and calculate premiums
        filtered_insurances_with_premiums = []
        for insurance in motor_insurances:
            rate_ranges = RateRange.objects.filter(motor_insurance=insurance)
            for rate_range in rate_ranges:
                if (rate_range.min_value <= vehicle_value <= rate_range.max_value and
                    rate_range.vehicle_type == vehicle_type):
                    # rate_range.min_year <= vehicle_age <= rate_range.max_year):
                    
                    # Calculate base premium
                    base_premium = vehicle_value * (rate_range.rate / 100)
                    
                    # Retrieve additional charges
                    additional_charges = OptionalExcessCharge.objects.filter(insurance=insurance.insurance)
                    under_21_charge = 0
                    under_1_year_charge = 0

                    for charge in additional_charges:
                        if age < 21:
                            under_21_charge = charge.under_21_age_charge
                        if experience < 1:  # Assuming this is driver experience
                            under_1_year_charge = charge.under_1_year_experience_charge

                    # Calculate total premium
                    total_premium = base_premium + under_21_charge + under_1_year_charge

                    # Append the insurance details with the calculated premium
                    filtered_insurances_with_premiums.append({
                        'insurance_id': insurance.id,
                        'company_name': insurance.insurance.company_name,
                        'cover_type': insurance.cover_type,
                        'vehicle_type': rate_range.vehicle_type,
                        'base_premium': base_premium,
                        'under_21_charge': under_21_charge,
                        'under_1_year_charge': under_1_year_charge,
                        'total_premium': total_premium,
                    })
                    break  # Stop checking other rate ranges for this insurance

        if not filtered_insurances_with_premiums:
            return Response({'message': 'No matching insurance policies found'}, status=status.HTTP_404_NOT_FOUND)

        return Response({
            'message': 'Filtered motor insurance policies retrieved successfully',
            'data': filtered_insurances_with_premiums,
        }, status=status.HTTP_200_OK)

        # except Exception as e:
        #     return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class EditMotorInsurance(APIView):
    def get_object(self, id):
        
        try:
            return MotorInsurance.objects.get(id=id)
        except MotorInsurance.DoesNotExist:
            return Response(
                {'error': 'MotorInsurance not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    def get(self, request, id):
        motor_insurance = self.get_object(id)
        if isinstance(motor_insurance, Response):  # If the object was not found
            return motor_insurance

        serializer = MotorInsuranceSerializer(motor_insurance)
        return Response({
            'message': 'MotorInsurance retrieved successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    def patch(self, request, id):

        motor_insurance = self.get_object(id)
        if isinstance(motor_insurance, Response):  # If the object was not found
            return motor_insurance

        # Serialize the instance with the incoming data
        serializer = MotorInsuranceSerializer(motor_insurance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'MotorInsurance updated successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self,request,id):
        try:
            user = get_user_from_token(request)
            if not user:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

            # # Retrieve organisation associated with the user
            organisation = get_organisation_from_user(user)
            print(organisation)
            
            # Query Insurance for Motor type
            insurance_queryset = Insurance.objects.filter(organisation=organisation, type='Motor',id=id)
            if not insurance_queryset.exists():
                return Response({'message': 'No Motor insurance policies found'}, status=status.HTTP_404_NOT_FOUND)
            
            insurance_queryset.delete()
            return Response({'message': 'Motor insurance deleted successfully'}, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

# ----------------------------------------------------------------- Upload Marine insurance policy ----------------------------------------------------#
# step 1
class MarineInsuranceUpload(APIView):
    
    def get(self, request):
        try:
            user = get_user_from_token(request)
            if not user:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

            # # Retrieve organisation associated with the user
            organisation = get_organisation_from_user(user)
            print(organisation)
            
            # Query Insurance for Motor type
            insurance_queryset = Insurance.objects.filter(organisation=organisation, type='Marine')
            if not insurance_queryset.exists():
                return Response({'message': 'No Marine insurance policies found'}, status=status.HTTP_404_NOT_FOUND)
            
            
            # # Query MotorInsurance and related data
            marine_insurances = MarineInsurance.objects.filter(insurance__in=insurance_queryset).select_related('insurance')
            if not marine_insurances.exists():
                return Response({'message': 'No Marine insurance details found'}, status=status.HTTP_404_NOT_FOUND)
            
            
            serializer = MarineInsuranceSerializer(marine_insurances, many=True)
            
            # Return the response
            return Response({
                'message': 'Marine insurance policies retrieved successfully',
                'data': serializer.data,
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

    def post(self,request):
        data = request.data
        type = 'Marine'
        title = data.get('title')
        description = data.get('description')

        try:
            # Retrieve user from token
            user = get_user_from_token(request)

            # Retrieve organisation associated with the user
            organisation = get_organisation_from_user(user)

            # Create a new insurance entry
            new_insurance = Insurance.objects.create(
                organisation=organisation,
                type=type,
                title=title,
                description=description
            )

            response = Response({
                'message': 'Insurance created successfully',
                'data': {
                    'id': new_insurance.id,
                    'type': new_insurance.type,
                    'title': new_insurance.title,
                    'description': new_insurance.description
                }
            }, status=status.HTTP_201_CREATED)

            response.set_cookie(
                key='marine_insurance',
                value=new_insurance.id,
                httponly=True,
                samesite='None',
                secure=False,
                max_age=3600  # 1 hour
            )
            return response
        except AuthenticationFailed as e:
            return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# step 2 
class MarineInsuranceDetails(APIView):
    def post(self, request):
        data = request.data
        vessel_type = data.get('vessel_type')
        cargo_type = data.get('cargo_type')
        voyage_type = data.get('voyage_type')
        coverage_type = data.get('coverage_type')
        price = data.get('price')

        try:
            get_insurance_id = request.COOKIES.get('marine_insurance')
            if not get_insurance_id:
                return Response({'error': 'Insurance cookie not found'}, status=status.HTTP_400_BAD_REQUEST)

            # query insurance
            insurance = Insurance.objects.get(id=get_insurance_id)

            upload = MarineInsurance.objects.create(
                insurance=insurance,
                vessel_type=vessel_type,
                cargo_type=cargo_type,
                voyage_type=voyage_type,
                coverage_type=coverage_type,
                price=price
            )

            response = Response({
                'message': 'Insurance created successfully',
                'data': {
                    'id': upload.id,
                    'vessel_type': upload.vessel_type,
                    'cargo_type': upload.cargo_type,
                    'voyage_type': upload.voyage_type,
                    'coverage_type': upload.coverage_type,
                    'price': upload.price
                }
            }, status=status.HTTP_201_CREATED)

            return response

        except Insurance.DoesNotExist:
            return Response({'error': 'Insurance not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

# step3
class MarineInsuranceBenefits(APIView):
    def post(self, request):
        data = request.data
        limit_of_liability = data.get('limit_of_liability')
        rate = data.get('rate')
        price = data.get('price')
        description = data.get('description')

        try:
            get_insurance_id = request.COOKIES.get('marine_insurance')
            if not get_insurance_id:
                return Response({'error': 'Insurance cookie not found'}, status=status.HTTP_400_BAD_REQUEST)

            # query insurance
            insurance = Insurance.objects.get(id=get_insurance_id)

            new_benefit = Benefit.objects.create(
                insurance=insurance,
                limit_of_liability=limit_of_liability,
                rate=rate,
                price=price,
                description=description
            )

            return Response({
                "message": "Benefits created successfully",
                "data": {
                    "id": new_benefit.id,
                    "limit_of_liability": new_benefit.limit_of_liability,
                    "rate": new_benefit.rate,
                    "price": new_benefit.price,
                    "description": new_benefit.description
                }
            })
        except Insurance.DoesNotExist:
            return Response({'error': 'Insurance not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ----------------------------------------------------------------- GET QUOTE for Marine Insurance----------------------------------------------------#


class CreateMarineInsuranceSession(APIView):
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
        vessel_type = data.get('vessel_type')
        coverage_type = data.get('coverage_type')


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
                "vessel_type": vessel_type,
                "coverage_type": coverage_type,
            }
            
            # Serialize the dictionary to JSON
            user_details_json = json.dumps(user_details)
            sign = Signer()
            signed_data = sign.sign(user_details_json)
            # Create the response and set the cookie
            response = Response({"message": "Marine Insurance session created successfully"}, status=status.HTTP_201_CREATED)
            response.set_cookie(
                key="user_marine_details",
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
        

# ----------------------------------------------------------------- GET QUOTE for Marine Insurance----------------------------------------------------#

class FilterMarineInsurance(APIView):
    def get(self, request):
        try:
            # Retrieve and decode the cookie
            signed_data = request.COOKIES.get('user_marine_details')
            if not signed_data:
                return Response({'error': 'No session data found in cookies'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Unsigned and deserialize the cookie data
            sign = Signer()
            user_details_json = sign.unsign(signed_data)
            user_details = json.loads(user_details_json)
            
            # Extract filter parameters from the cookie
            vessel_type = user_details.get('vessel_type')
            coverage_type = user_details.get('coverage_type')
            insurance_type = "Marine"  # We're filtering for marine insurance
            
            # Step 1: Query the Insurance model for the relevant policies
            insurance_queryset = Insurance.objects.filter(type=insurance_type)
            
            if not insurance_queryset.exists():
                return Response({'message': 'No insurance policies found for the given type'}, status=status.HTTP_404_NOT_FOUND)
            
            marine_queryset = MarineInsurance.objects.filter(insurance__in=insurance_queryset)
            # Step 2: Query the MotorInsurance model for the specific details
            
            # Apply additional filters
            if vessel_type:
                marine_queryset = marine_queryset.filter(vessel_type=vessel_type)
            if coverage_type:
                marine_queryset = marine_queryset.filter(coverage_type=coverage_type)
            
            if not marine_queryset.exists():
                return Response({'message': 'No marine insurance policies match the given filters'}, status=status.HTTP_404_NOT_FOUND)
            
# Step 3: Serialize the results
            policies_data = []
            for marine_policy in marine_queryset:
                # Get the associated benefits for this insurance policy
                benefits = Benefit.objects.filter(insurance=marine_policy.insurance)
                benefits_data = [
                    {
                        'limit_of_liability': benefit.limit_of_liability,
                        'rate': benefit.rate,
                        'price': benefit.price,
                        'description': benefit.description,
                    }
                    for benefit in benefits
                ]
                
                # Add the marine policy and its benefits to the response
                policies_data.append({
                    'id': marine_policy.id,
                    'vessel_type': marine_policy.vessel_type,
                    'coverage_type': marine_policy.coverage_type,
                    'price': marine_policy.price,
                    'insurance_title': marine_policy.insurance.title,
                    'organisation_name': marine_policy.insurance.organisation.company_name,
                    'benefits': benefits_data,  # Include benefits in the response
                })
            
            # Return the filtered results
            return Response({
                'message': 'Filtered marine insurance policies retrieved successfully',
                'data': policies_data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)



#=============================Upload health insuarance policy---------------------------------------------------------------------------
class UploadHealthInsurance(APIView):
    def post(self, request):
        data = request.data
        type = 'Health'
        title = data.get('title')
        description = data.get('description')
        image= data.get('image')
        company_name= data.get('company_name')

        try:
            # Retrieve user from token
            user = get_user_from_token(request)

            # Retrieve organisation associated with the user
            organisation = get_organisation_from_user(user)

            # Create a new insurance entry
            new_insurance = Insurance.objects.create(
                organisation=organisation,
                company_name= company_name,
                type=type,
                title=title,
                description=description,
                insurance_image=image
            )

            response = Response({
                'message': 'Insurance created successfully',
                'data': {
                    'id': new_insurance.id,
                    'type': new_insurance.type,
                    'title': new_insurance.title,
                    'description': new_insurance.description
                }
            }, status=status.HTTP_201_CREATED)

            response.set_cookie(
                key='healthinsurance',
                value=new_insurance.id,
                httponly=True,
                samesite='None',
                secure=False,
                max_age=3600  # 1 hour
            )
            return response
        except AuthenticationFailed as e:
            return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# PATCH/DELETE/GET pass Insuarance ID
class EditHealthInsurance(APIView):
    def get(self, request, id):
        try:
            user= get_user_from_token(request)
            if not user:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

            if user.role != user.Role.ORGANISATION:
                return Response({'error': 'You are not authorized to access this page'}, status=status.HTTP_401_UNAUTHORIZED)
            
            type= "Health"
            insuarance= Insurance.objects.filter(id=id, type=type).first()
            if not insuarance:
                return Response({'error': 'Insurance not found'}, status=status.HTTP_404_NOT_FOUND)

            health_insure= HealthInsurance.objects.filter(insurance=insuarance).first()
            if not health_insure:
                return Response({'error': 'Health insurance not found'}, status=status.HTTP_404_NOT_FOUND)
            
            benefits= Benefit.objects.filter(insurance=insuarance).all()
            if not benefits:
                return Response({'error': 'Benefits not found'}, status=status.HTTP_404_NOT_FOUND)

            response_data= {
                "insurance": InsuranceSerializer(insuarance).data,
                "health_insurance": HealthInsuranceSerializer(health_insure).data,
                "benefits": BenefitSerializer(benefits, many=True).data
            }

            return Response({'data': response_data}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, id):
        try:
            user= get_user_from_token(request)
            if not user:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

            if user.role != user.Role.ORGANISATION:
                return Response({'error': 'You are not authorized to access this page'}, status=status.HTTP_401_UNAUTHORIZED)
            
            type= "Health"
            insuarance= Insurance.objects.filter(id=id, type=type).first()
            if not insuarance:
                return Response({'error': 'Insurance not found'}, status=status.HTTP_404_NOT_FOUND)

            data = request.data
            title = data.get('title')
            description = data.get('description')
            image= data.FILES('image')
            company_name= data.get('company_name')

            if title:
                insuarance.title= title
            elif description:
                insuarance.description= description
            elif image:
                insuarance.insurance_image= image
            elif company_name:
                insuarance.company_name= company_name
            insuarance.save()

            return Response({'message': 'Insurance updated successfully'}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        try:
            user= get_user_from_token(request)
            if not user:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

            if user.role != user.Role.ORGANISATION:
                return Response({'error': 'You are not authorized to access this page'}, status=status.HTTP_401_UNAUTHORIZED)
            
            type= "Health"
            insuarance= Insurance.objects.filter(id=id, type=type).first()
            if not insuarance:
                return Response({'error': 'Insurance not found'}, status=status.HTTP_404_NOT_FOUND)

            insuarance.delete()
            return Response({'message': 'Insurance deleted successfully'}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Health details----------------------------------------------------------------------------------------------------------------
class HealthInsuranceDetails(APIView):
    def get(self, request):
        pass

    def post(self, request):
        data = request.data
        cover_type = data.get('cover_type')
        price = data.get("price")
        high_range = data.get("highrange")
        low_range = data.get("lowrange")

        try:
            get_insurance_id = request.COOKIES.get('healthinsurance')
            if not get_insurance_id:
                return Response({'error': 'Insurance cookie not found'}, status=status.HTTP_400_BAD_REQUEST)

            # query insurance
            insurance = Insurance.objects.get(id=get_insurance_id)


            upload = HealthInsurance.objects.create(
                insurance=insurance,
                cover_type=cover_type,
                price=price,
                high_range=high_range,
                low_range=low_range
            )

            response = Response({
                'message': 'Insurance created successfully',
                'data': {
                    'id': upload.id,
                    'cover_type': upload.cover_type,
                    'price': upload.price,
                    'high_range': upload.high_range,
                    'low_range': upload.low_range
                }
            }, status=status.HTTP_201_CREATED)

            return response

        except Insurance.DoesNotExist:
            return Response({'error': 'Insurance not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Health benefites-----------------------------------------------------------------
class HealthInsuranceBenefits(APIView):
    def post (self, request):
        data = request.data
        limit_of_liability = data.get('limit_of_liability')
        rate = data.get('rate')
        description = data.get('description')

        try:
            get_insurance_id = request.COOKIES.get('healthinsurance')
            if not get_insurance_id:
                return Response({'error': 'Insurance cookie not found'}, status=status.HTTP_400_BAD_REQUEST)

            # query insurance
            insurance = Insurance.objects.get(id=get_insurance_id)

            health_insuarance= HealthInsurance.objects.get(insurance=insurance)
            price= health_insuarance.price*rate/100

            new_benefit = Benefit.objects.create(
                insurance=insurance,
                limit_of_liability=limit_of_liability,
                rate=rate,
                price=price,
                description=description
            )

            return Response({
                "message":"Benefits created successfully",
                "data":{
                    "id":new_benefit.id,
                    "limit_of_liability":new_benefit.limit_of_liability,
                    "rate":new_benefit.rate,
                    "price":new_benefit.price,
                    "description":new_benefit.description
                }
            })
        except Insurance.DoesNotExist:
            return Response({'error': 'Insurance not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class FilterHealthInsurance(APIView):
    def get(self, request):
        try:
            # Retrieve and decode the cookie
            signed_data = request.COOKIES.get('healthsession')
            if not signed_data:
                return Response({'error': 'No session data found in cookies'}, status=status.HTTP_400_BAD_REQUEST)

            # Get data from jwt token
            try:
                user_details = jwt.decode(signed_data, config("SECRET"), algorithms=['HS256'])
                if not user_details:
                    return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
            except jwt.ExpiredSignatureError:
                return Response({'error': 'Token has expired'}, status=status.HTTP_400_BAD_REQUEST)


            # Extract filter parameters from the cookie
            cover_type = user_details.get('coverage_type')
            insurance_type = "Health"  # We're filtering for health insurance

            # Step 1: Query the Insurance model for the relevant policies
            insurance_queryset = Insurance.objects.filter(type=insurance_type)

            if not insurance_queryset.exists():
                return Response({'message': 'No insurance policies found for the given type'}, status=status.HTTP_404_NOT_FOUND)

            # Step 2: Query the HealthInsurance model for the specific details
            health_queryset = HealthInsurance.objects.filter(insurance__in=insurance_queryset)

            # Apply additional filters
            if cover_type:
                health_queryset = health_queryset.filter(cover_type=cover_type)

            if not health_queryset.exists():
                return Response({'message': 'No health insurance policies match the given filters'}, status=status.HTTP_404_NOT_FOUND)

            # Step 3: Serialize the results
            policies_data = [
                {
                    'id': health_policy.id,
                    'cover_type': health_policy.cover_type,
                    'price': health_policy.price,
                    'insurance_title': health_policy.insurance.title,
                    'organisation_name': health_policy.insurance.organisation.company_name,
                }
                for health_policy in health_queryset
            ]

            # Return the filtered results
            return Response({
                'message': 'Filtered health insurance policies retrieved successfully',
                'data': policies_data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

#----------------------------------------------------------------------- patch and delete marine insurance --------------------------------------------------# 

class UpdateMarineInsurance(APIView):
    def delete(self,request,id):
        try:
            user = get_user_from_token(request)
            if not user:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

            # # Retrieve organisation associated with the user
            organisation = get_organisation_from_user(user)
            print(organisation)
            
            # Query Insurance for Motor type
            insurance_queryset = Insurance.objects.filter(organisation=organisation, type='Marine',id=id)
            if not insurance_queryset.exists():
                return Response({'message': 'No Marine insurance policies found'}, status=status.HTTP_404_NOT_FOUND)
            
            insurance_queryset.delete()
            return Response({'message': 'Marine insurance deleted successfully'}, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
#----------------------------------------------------------------------- KYC FOR MOTOR INSURACE  --------------------------------------------------# 

class ApplicantkycUpload(APIView):
    def post(self, request):
        data = request.FILES 
        # Motor insurane
        national_id = data.get('national_id')
        driving_license = data.get('driving_license')
        valuation_report = data.get('valuation_report')
        kra_pin_certificate = data.get('kra_pin_certificate')
        log_book = data.get('log_book')

        try:
            user = get_user_from_token(request)
            if not user:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

            # # Retrieve organisation associated with the user
            applicant = get_applicant_from_user(user)
            print(applicant)

            ApplicantKYC.objects.create(
                applicant=applicant,
                national_id=national_id,
                driving_license=driving_license,
                valuation_report=valuation_report,
                kra_pin_certificate=kra_pin_certificate,
                log_book=log_book
            )

            response = Response({
                'message': 'KYC created successfully',
            }, status=status.HTTP_201_CREATED)

            return response

        except Applicant.DoesNotExist:
            return Response({'error': 'Applicant not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
