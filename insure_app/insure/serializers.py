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


class MotorInsuranceTempDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = MotorInsuranceTempData
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class BasicInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BasicInfo
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class GoodsInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsInfo
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class ConveyanceInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConveyanceInfo
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class TransitPointSerializer(serializers.ModelSerializer):

    class Meta:
        model = TransitPoint
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class RouteInfoSerializer(serializers.ModelSerializer):
    transit_points = TransitPointSerializer(many=True, read_only=True)  # Include nested transit points
    class Meta:
        model = RouteInfo
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class MarineInsuranceApplicationSerializer(serializers.ModelSerializer):
    basic_info = BasicInformationSerializer()  
    conveyance_info = ConveyanceInfoSerializer()  
    route_info = RouteInfoSerializer()  
    goods_info = GoodsInfoSerializer(many=True)  
    class Meta:
        model = MarineInsuranceApplication
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
