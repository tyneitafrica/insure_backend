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
    # sign up org
    path("api/v1.0/organisation/signup/", SignupOrganisation.as_view(), name="login org"),

    # login org
    path("api/v1.0/organisation/login/", LoginOrganisation.as_view(), name="login org"),


    path("api/v1.0/applicant/motor_session/", CreateMotorInsuranceSession.as_view(), name="create insurance session"),   

    
    path("api/v1.0/applicant/motor_session/", CreateMotorInsuranceSession.as_view(), name="create insurance session"),

    # Health
    path("api/v1.0/health-insuarance-session/", HealthInsuaranceSession.as_view(), name="create health insurance session"),
    path("api/v1.0/get-auth-quotes/", GetHealthInsuranceQuote.as_view(), name="get user quotes"),
    path("api/v1.0/health-insuarance-session/", HealthInsuaranceSession.as_view(), name="create health insurance session"),
    path("api/v1.0/health-insuarance-session/upload/", UploadHealthInsurance.as_view(), name="create health insurance session"),
    path("api/v1.0/health-insuarance-session/details/", HealthInsuranceDetails.as_view(), name="create health insurance session"),
    path("api/v1.0/health-insuarance-session/benefits/", HealthInsuranceBenefits.as_view(), name="create health insurance session"),
    path("api/v1.0/health-insurance/filter/", FilterHealthInsurance.as_view(), name="filter health insurance"),

    # Motor
    path("api/v1.0/motorinsurance/upload/",UploadMotorInsurance.as_view(), name="create health insurance step1"),
    path("api/v1.0/motorinsurance/details/",MotorInsuranceDetails.as_view(), name="create health insurance step2"),
    path("api/v1.0/motorinsurance/benefits/",MotorInsuranceBenefits.as_view(), name="create health insurance step3"),
    path("api/v1.0/motor-insurance/filter/",FilterMotorInsurance.as_view(), name="filter motor insurance"),


]
