# contains the serialized data
from .models import *
from rest_framework import serializers
from django.utils.timezone import now

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email','password','role']

        extra_kwargs = {
            'password': {"write_only":True},
            'role':{"required": True}
        }
    def create(self,validated_data):
        password = validated_data.pop('password',None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        
        instance.save()
        return instance

class ApplicantSerializer(serializers.ModelSerializer):
    age = serializers.SerializerMethodField()

    def get_age(self, obj):
        if obj.yob:
            today = now().date()
            born = obj.yob
            return today.year - born.year - ((today.month, today.day) < (born.month, born.day))
        return None

    class Meta:
        model = Applicant
        fields = [
            'id', 'user', 'phone_number', 'yob', 'id_no', 'age', 'occupation', 'gender', 'created_at', 'updated_at'
        ]


class OrganisationSerializer(serializers.ModelSerializer):
    user= UserSerializer(read_only=True)
    class Meta:
        model = Organisation
        fields = ['id', 'user', 'company_name', 'phone_number', 'created_at', 'updated_at']


class InsuranceSerializer(serializers.ModelSerializer):
    organisation= OrganisationSerializer(read_only=True)
    class Meta:
        model = Insurance
        fields = ['id', 'organisation', 'company_name','insurance_image','title', 'type', 'description','created_at', 'updated_at']
        read_only_fields = ('created_at', 'updated_at')

class VehicleTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleType
        fields = ['id','vehicle_category']
        read_only_fields = ('created_at', 'updated_at')


class RiskTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiskType
        fields = ['id','vehicle_type','risk_name']
        read_only_fields = ('created_at', 'updated_at')


class RateRangeSerializer(serializers.ModelSerializer):
    vehicle_type = serializers.SerializerMethodField()  # Custom method to get vehicle type
    risk_type = RiskTypeSerializer(read_only=True)  # Nested RiskType serializer

    class Meta:
        model = RateRange
        fields = ['id','motor_insurance','vehicle_type','risk_type','usage_category','weight_category','max_car_age','min_value','max_value','rate','min_sum_assured']
        read_only_fields = ('created_at', 'updated_at')


    def get_vehicle_type(self, obj):
        # Get the vehicle type from the related RiskType
        return obj.risk_type.vehicle_type.vehicle_category

class ExcessChargesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExcessCharges
        fields = ['id','limit_of_liability','excess_rate','min_price','description']
        read_only_fields = ('created_at', 'updated_at')

class MotorInsuranceSerializer(serializers.ModelSerializer):
    rate_ranges = RateRangeSerializer(many=True)  # Allow write operations
    excess_charges = ExcessChargesSerializer(many=True)  # Allow write operations

    class Meta:
        model = MotorInsurance
        fields = ['id', 'insurance', 'cover_type', 'rate_ranges', 'excess_charges']
        read_only_fields = ('created_at', 'updated_at')

    def update(self, instance, validated_data):
        # Extract nested data
        rate_ranges_data = validated_data.pop('rate_ranges', None)
        excess_charges_data = validated_data.pop('excess_charges', None)

        # Update the MotorInsurance instance
        instance = super().update(instance, validated_data)

        # Update or create nested RateRange objects
        if rate_ranges_data is not None:
            self.update_rate_ranges(instance, rate_ranges_data)

        # Update or create nested ExcessCharges objects
        if excess_charges_data is not None:
            self.update_excess_charges(instance, excess_charges_data)

        return instance

    def update_rate_ranges(self, instance, rate_ranges_data):
        print ("initiated")

        print("incoming requet",{rate_range_data})
        # Get existing rate ranges for the motor insurance
        existing_rate_ranges = {rate_range.id: rate_range for rate_range in instance.rate_ranges.all()}
        
        print(existing_rate_ranges)

        for rate_range_data in rate_ranges_data:
            rate_range_id = rate_range_data.get('id',None)
            print(rate_range_id)

            if rate_range_id and rate_range_id in existing_rate_ranges:
                # Update existing RateRange
                rate_range = existing_rate_ranges[rate_range_id]
                for key, value in rate_range_data.items():
                    setattr(rate_range, key, value)
                rate_range.save()
            else:
                # Create new RateRange
                RateRange.objects.create(motor_insurance=instance, **rate_range_data)

        # Delete RateRanges that were not included in the update
        updated_rate_range_ids = [rate_range_data.get('id') for rate_range_data in rate_ranges_data if rate_range_data.get('id')]
        for rate_range_id, rate_range in existing_rate_ranges.items():
            if rate_range_id not in updated_rate_range_ids:
                rate_range.delete()

    def update_excess_charges(self, instance, excess_charges_data):
        # Get existing excess charges for the motor insurance
        existing_excess_charges = {excess_charge.id: excess_charge for excess_charge in instance.excess_charges.all()}
        # print("incoming requet", {existing_excess_charges})

        for excess_charge_data in excess_charges_data:
            excess_charge_id = excess_charge_data.get('id', None)

            if excess_charge_id and excess_charge_id in existing_excess_charges:
                # Update existing ExcessCharges
                excess_charge = existing_excess_charges[excess_charge_id]
                for key, value in excess_charge_data.items():
                    setattr(excess_charge, key, value)
                excess_charge.save()
            else:
                # Create new ExcessCharges
                ExcessCharges.objects.create(motor_insurance=instance, **excess_charge_data)

        # Delete ExcessCharges that were not included in the update
        updated_excess_charge_ids = [excess_charge_data.get('id') for excess_charge_data in excess_charges_data if excess_charge_data.get('id')]
        for excess_charge_id, excess_charge in existing_excess_charges.items():
            if excess_charge_id not in updated_excess_charge_ids:
                excess_charge.delete()
    

class AdditionalChargesSerializer(serializers.ModelSerializer):
    class Meta:
        model = OptionalExcessCharge
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')




class HealthInsuranceSerializer(serializers.ModelSerializer):
    insuarance= InsuranceSerializer(read_only=True)
    class Meta:
        model = HealthInsurance
        fields = [
            'id', 'high_range', 'low_range','cover_type', 'price','insuarance','created_at', 'updated_at'
        ]
        read_only_fields = ('created_at', 'updated_at')




class PolicySerializer(serializers.ModelSerializer):
    end_date = serializers.DateField(read_only=True)
    insurance= InsuranceSerializer(read_only=True)
    applicant= ApplicantSerializer(read_only=True)

    class Meta:
        model = Policy
        fields = [
            'id', 'applicant', 'insurance', 'cover_type', 'risk_name', 'age', 'policy_number', 'total_amount' ,'start_date', 'end_date', 'duration', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ('created_at', 'updated_at')

class HealthInsuranceQuoteRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthInsuaranceQuoteRequest
        fields = ['first_name','last_name','dob','national_id','occupation','phone_number','gender','coverage_amount','coverage_type','is_travel_related','is_covered']
        read_only_fields = ('created_at', 'updated_at')

class HealthLifestyleSerializer(serializers.ModelSerializer):
    health_insuarance_quote_request = HealthInsuranceQuoteRequestSerializer()  # Nested serializer

    class Meta:
        model = HealthLifestyle
        fields = ['pre_existing_condition','high_risk_activities','medication',
                  'mode_of_transport','smoking','past_claim',
                  'stress_level','family_history','allergies','mental_health', 'health_insuarance_quote_request',]
        read_only_fields = ('created_at', 'updated_at', 'health_insurance_quote_request')

    # def create(self, validated_data):
    #     # Handle nested serializer creation for HealthInsuranceQuoteRequest
    #     quote_request_data = validated_data.pop('health_insurance_quote_request')
    #     quote_request = HealthInsuaranceQuoteRequest.objects.create(**quote_request_data)
    #     health_lifestyle = HealthLifestyle.objects.create(
    #         health_insurance_quote_request=quote_request,
    #         **validated_data
    #     )
    #     return health_lifestyle

    # def update(self, instance, validated_data):
    #     # Handle nested serializer update for HealthInsuranceQuoteRequest
    #     quote_request_data = validated_data.pop('health_insurance_quote_request', None)
    #     if quote_request_data:
    #         for key, value in quote_request_data.items():
    #             setattr(instance.health_insurance_quote_request, key, value)
    #         instance.health_insurance_quote_request.save()

    #     for key, value in validated_data.items():
    #         setattr(instance, key, value)
    #     instance.save()
    #     return instance

class BenefitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Benefit
        fields = ['id', 'limit_of_liability', 'rate', 'price', 'description']




class MarineInsuranceSerializer(serializers.ModelSerializer):
    insurance = InsuranceSerializer(read_only=True)
    benefits = BenefitSerializer(source='insurance.benefits', many=True, read_only=True)  # Fix here

    class Meta:
        model = MarineInsurance
        fields = ['insurance','vessel_type','cargo_type','voyage_type','coverage_type','price','benefits']
        read_only_fields = ('created_at', 'updated_at')


class PaymentSerializer(serializers.ModelSerializer):
    policy= PolicySerializer(read_only=True)

    class Meta:
        model = Payment
        fields = ['id', 'policy','invoice_id','api_ref_id', 'transaction_id', 'merchant_request_id', 'checkout_request_id','amount','phone_number','pay_date','pay_method','description', 'status','result_desc','created_at', 'updated_at']
        read_only_fields = ('created_at', 'updated_at')


class ApplicantKYCSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicantKYC
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at') 
