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
    list_display  = ('title', 'type', 'description','created_at', 'updated_at')
    search_fields = ('title', 'type')
    list_filter   = ('type', 'title')

admin.site.register(Insurance, InsuranceAdmin)

class MotorInsuranceAdmin(admin.ModelAdmin):
    list_display  = ('insurance', 'cover_type','price')
    search_fields = ['cover_type']
    list_filter   = ['cover_type']

admin.site.register(MotorInsurance, MotorInsuranceAdmin)

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