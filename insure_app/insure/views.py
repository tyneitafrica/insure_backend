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
    
def get_user_from_token(request):
    token = request.COOKIES.get('jwt')
    if not token:
        raise AuthenticationFailed("Token is missing from the request.")

    try:
        payload = jwt.decode(token, config("SECRET"), algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed("Token has expired.")
    except jwt.InvalidTokenError:
        raise AuthenticationFailed("Invalid token.")

    user = User.objects.filter(id=payload['id']).first()
    if not user:
        raise AuthenticationFailed("User not found.")

    return user

def get_organisation_from_user(user):
    organisation = Organisation.objects.filter(user=user).first()
    if not organisation:
        raise ValueError("Organisation not found.")
    return organisation
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
        raise ValueError("Organisation not found.")
    return organisation


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

# ----------------------------------------------------------------- GET QUOTE health Insurance----------------------------------------------------#
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
        
# ----------------------------------------------------------------- Upload insurance policy ----------------------------------------------------#
class UploadMotorInsurance(APIView):
    def post(self, request):
        data = request.data
        type = 'Motor'
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
                key='insurance',
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

# upload step 2 
class MotorInsuranceDetails(APIView):
    def post(self,request):
        data = request.data
        cover_type = data.get('cover_type')
        price = data.get("price")
        vehicle_type = data.get("vehicle_type")
        
        try:
            get_insurance_id = request.COOKIES.get('insurance')
            if not get_insurance_id:
                return Response({'error': 'Insurance cookie not found'}, status=status.HTTP_400_BAD_REQUEST)

            # query insurance
            insurance = Insurance.objects.get(id=get_insurance_id)


            upload = MotorInsurance.objects.create(
                insurance=insurance,
                cover_type=cover_type,
                price=price,
                vehicle_type=vehicle_type
            )

            response = Response({
                'message': 'Insurance created successfully',
                'data': {
                    'id': upload.id,
                    'cover_type': upload.cover_type,
                    'price': upload.price
                }
            }, status=status.HTTP_201_CREATED)

            return response
        
        except Insurance.DoesNotExist:
            return Response({'error': 'Insurance not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class MotorInsuranceBenefits(APIView):
    def post (self,request):
        data = request.data
        limit_of_liability = data.get('limit_of_liability')
        rate = data.get('rate')
        price = data.get('price')  
        description = data.get('description') 

        try:
            get_insurance_id = request.COOKIES.get('insurance')
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
        try:
            # Retrieve and decode the cookie
            signed_data = request.COOKIES.get('user_motor_details')
            if not signed_data:
                return Response({'error': 'No session data found in cookies'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Unsigned and deserialize the cookie data
            sign = Signer()
            user_details_json = sign.unsign(signed_data)
            user_details = json.loads(user_details_json)
            
            # Extract filter parameters from the cookie
            vehicle_type = user_details.get('vehicle_type')
            cover_type = user_details.get('cover_type')
            insurance_type = "Motor"  # We're filtering for motor insurance
            
            # Step 1: Query the Insurance model for the relevant policies
            insurance_queryset = Insurance.objects.filter(type=insurance_type)
            
            if not insurance_queryset.exists():
                return Response({'message': 'No insurance policies found for the given type'}, status=status.HTTP_404_NOT_FOUND)
            
            # Step 2: Query the MotorInsurance model for the specific details
            motor_queryset = MotorInsurance.objects.filter(insurance__in=insurance_queryset)
            
            # Apply additional filters
            if vehicle_type:
                motor_queryset = motor_queryset.filter(vehicle_type=vehicle_type)
            if cover_type:
                motor_queryset = motor_queryset.filter(cover_type=cover_type)
            
            if not motor_queryset.exists():
                return Response({'message': 'No motor insurance policies match the given filters'}, status=status.HTTP_404_NOT_FOUND)
            
            # Step 3: Serialize the results
            policies_data = [
                {
                    'id': motor_policy.id,
                    'vehicle_type': motor_policy.vehicle_type,
                    'cover_type': motor_policy.cover_type,
                    'price': motor_policy.price,
                    'insurance_title': motor_policy.insurance.title,
                    'organisation_name': motor_policy.insurance.organisation.company_name,
                }
                for motor_policy in motor_queryset
            ]
            
            # Return the filtered results
            return Response({
                'message': 'Filtered motor insurance policies retrieved successfully',
                'data': policies_data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)