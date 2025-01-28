"""
URL configuration for insure_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from insure.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/v1.0/applicant/signup/", SignupUser.as_view(),name="signup user"),
    # login applicant
    path("api/v1.0/applicant/login/", LoginApplicant.as_view(), name="login applicant"),

    path("api/v1.0/applicant/motor_session/", CreateMotorInsuranceSession.as_view(), name="create insurance session"),
    path("api/v1.0/applicant/temp_motor_insurance/", MotorTempData.as_view(), name="create temporary_motorinsurance"),
   

]
