# will contain configuration for the api keys 
from datetime import timedelta
from django.http import JsonResponse
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from django.utils.dateparse import parse_datetime




class ApiKeyMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the request is for a protected route
        if request.path.startswith('/api/v1.0/'):
            api_key = request.headers.get('x-api-key')

            # Check if the API key matches the expected value
            if api_key != settings.API_KEY:
                return JsonResponse({'error': 'Unauthorized user please use correct key'}, status=401) #change response once in production 

        response = self.get_response(request)
        return response
    
class SessionTimeoutMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response
        # Set timeout duration to 20 minutes
        self.timeout_duration = timedelta(minutes=20)

    def __call__(self, request):
        if request.user.is_authenticated:
            # Retrieve last activity from session
            last_activity_str = request.session.get('last_activity')
            
            if last_activity_str:
                # Convert last activity back to a datetime object
                last_activity = parse_datetime(last_activity_str)
                
                if last_activity:
                    elapsed_time = timezone.now() - last_activity
                    # Check if elapsed time exceeds the timeout duration
                    if elapsed_time > self.timeout_duration:
                        # Log out the user if inactive for too long
                        request.session.flush()
            
            # Update last activity to current time
            request.session['last_activity'] = timezone.now().isoformat()

        # Proceed with the request
        response = self.get_response(request)
        return response