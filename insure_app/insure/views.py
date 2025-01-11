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

# Create your views here.



class SignupUser(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        role = User.Role.APPLICANT


        # check if the user is already registered
        try:

            if User.objects.filter(email=email).exists():
                return Response({'error': ' A user with this Email is already registered'}, status=status.HTTP_400_BAD_REQUEST)
            
            if not password:
                return Response({'error': 'Password is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            if not role:
                return Response({'error': 'Role is required'}, status=status.HTTP_400_BAD_REQUEST)

            # proceed with user creation
            serializer = UserSerializer(data={**request.data, "role": role})
            if serializer.is_valid():
                serializer.save()
              
                return Response(
                    {
                    'message': 'User created successfully',
                    'user': serializer.data,
                                
                    }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# -----------------------------------------APPLICANT LOGIN ----------------------------------#

class LoginApplicant(APIView):
    def post(self,request):
        email = request.data['email']
        password = request.data['password']
        
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


# ussd logic 

@csrf_exempt
def ussd_callback(request):
    if request.method == 'POST':
        text = request.POST.get('text', "")  # Default to an empty string for new sessions
        response = process_ussd(text)

        return Response({"response": response})