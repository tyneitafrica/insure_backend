from django.contrib import admin
from .models import *

admin.site.site_header = "INSURE DASHBOARD "
admin.site.site_title = "INSURE"
admin.site.index_title = "Welcome to Your your Dashboard"


class UserAdmin(admin.ModelAdmin):
    list_display= ('email', 'role',)
    search_fields= ('email',)

admin.site.register(User, UserAdmin)

class OrganisationAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'phone_number', 'created_at', 'updated_at')
    search_fields = ('company_name', 'phone_number')
    list_filter = ('created_at', 'updated_at')


admin.site.register(Organisation, OrganisationAdmin)

class ApplicantAdmin(admin.ModelAdmin):
    list_display  = ('user', 'phone_number','yob','age','id_no','created_at', 'updated_at')
    search_fields = ('user', 'phone_number')
    list_filter   = ('yob', 'id_no')

admin.site.register(Applicant, ApplicantAdmin)

class InsuranceAdmin(admin.ModelAdmin):
    list_display  = ('organisation','title', 'company_name', 'type', 'description','created_at', 'updated_at')
    search_fields = ('title', 'type','company_name','insurance_image','organisation')
    list_filter   = ('type', 'title')

admin.site.register(Insurance, InsuranceAdmin)

class MotorInsuranceAdmin(admin.ModelAdmin):
    list_display  = ('insurance', 'cover_type')
    search_fields = ['cover_type']
    list_filter   = ['cover_type']

admin.site.register(MotorInsurance, MotorInsuranceAdmin)

class VehicleTypeAdmin(admin.ModelAdmin):
    list_display  = ('vehicle_category', 'created_at', 'updated_at')
    search_fields = ('vehicle_category',)
    list_filter   = ('created_at', 'updated_at')
admin.site.register(VehicleType, VehicleTypeAdmin)

class RiskTypeAdmin(admin.ModelAdmin):
    list_display  = ('vehicle_type', 'risk_name', 'created_at', 'updated_at')
    search_fields = ('vehicle_type', 'risk_name')
    list_filter   = ('created_at', 'updated_at')

admin.site.register(RiskType, RiskTypeAdmin)

class RateRangesAdmin(admin.ModelAdmin):
    list_display  = ('get_cover_type', "risk_type",'max_car_age','min_value','max_value', 'rate','min_sum_assured')
    search_fields = ('motor_insurance', 'max_age','min_value','max_value')
    list_filter   = ('motor_insurance', 'rate')

    def get_cover_type(self, obj):
        return obj.motor_insurance.cover_type  # Access cover_type directly

    get_cover_type.short_description = "Cover Type"  # Change column title in the admin panel

admin.site.register(RateRange, RateRangesAdmin)

class ExtrachargesAdmin(admin.ModelAdmin):
    list_display  = ('motor_insurance', 'limit_of_liability', 'excess_rate', 'min_price', 'description', 'created_at', 'updated_at')
    search_fields = ('motor_insurance', 'limit_of_liability')
    list_filter   = ('limit_of_liability', 'updated_at')

admin.site.register(ExcessCharges, ExtrachargesAdmin)

class PolicyAdmin(admin.ModelAdmin):
    list_display  = ('applicant', 'insurance', 'start_date', 'end_date', 'duration', 'created_at', 'updated_at')
    search_fields = ('applicant', 'insurance')
    list_filter   = ('created_at', 'updated_at')

admin.site.register(Policy, PolicyAdmin)

class BenefitsAdmin(admin.ModelAdmin):
    list_display  = ('insurance', 'limit_of_liability', 'rate', 'price')
    search_fields = ('insurance', 'lmit_of_liability')
    list_filter   = ('created_at', 'updated_at')

admin.site.register(Benefit, BenefitsAdmin)


# class MarineInsuranceTempAdmin(admin.ModelAdmin):
#     list_display = ("first_name","coverage_type")
#     search_fields = ("is_evaluated","coverage_type")
#     list_filter = search_fields

# admin.site.register(MarineInsuranceTempData,MarineInsuranceTempAdmin)

# class MarineInsuraneAdmin(admin.ModelAdmin):
#     list_display = ("insurance","vessel_type")
#     search_fields = ("vessel_type","coverage_type")
#     list_filter = search_fields

# admin.site.register(MarineInsurance,MarineInsuraneAdmin)