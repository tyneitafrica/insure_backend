from django.contrib import admin
from .models import *

admin.site.site_header = "INSURE DASHBOARD "
admin.site.site_title = "INSURE"
admin.site.index_title = "Welcome to Your your Dashboard"


class OrganisationAdmin(admin.ModelAdmin):
    list_display = ('companyName', 'phoneNumber', 'created_at', 'updated_at')
    search_fields = ('companyName', 'phoneNumber')
    list_filter = ('created_at', 'updated_at')


admin.site.register(Organisation, OrganisationAdmin)

class ApplicantAdmin(admin.ModelAdmin):
    list_display  = ('user', 'phoneNumber','yob','age','id_no','created_at', 'updated_at')
    search_fields = ('user', 'phoneNumber')
    list_filter   = ('yob', 'id_no')

admin.site.register(Applicant, ApplicantAdmin)

# class InsuranceAdmin(admin.ModelAdmin):
#     list_display  = ('title', 'insurance_type', 'cover_type', 'description', 'price', 'created_at', 'updated_at')
#     search_fields = ('title', 'insurance_type')
#     list_filter   = ('insurance_type', 'cover_type')

# admin.site.register(Insurance, InsuranceAdmin)

class PolicyAdmin(admin.ModelAdmin):
    list_display  = ('applicant', 'insurance', 'start_date', 'end_date', 'duration', 'created_at', 'updated_at')
    search_fields = ('applicant', 'insurance')
    list_filter   = ('created_at', 'updated_at')

admin.site.register(Policy, PolicyAdmin)

class BenefitsAdmin(admin.ModelAdmin):
    list_display  = ('insurance', 'limit_of_liability', 'rate', 'price', 'created_at', 'updated_at')
    search_fields = ('insurance', 'lmit_of_liability')
    list_filter   = ('created_at', 'updated_at')

admin.site.register(Benefit, BenefitsAdmin)