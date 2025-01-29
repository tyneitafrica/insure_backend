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
    class Meta:
        model = Organisation
        fields = ['id', 'user', 'companyName', 'phoneNumber', 'created_at', 'updated_at']


class InsuranceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Insurance
        fields = ['id', 'organisation', 'insurance_image','title', 'type', 'description','created_at', 'updated_at']
        read_only_fields = ('created_at', 'updated_at')


class MotorInsuranceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MotorInsurance
        fields = [
            'id', 'organisation', 'title', 'price', 'vehicle_type', 'vehicle_make', 'vehicle_model', 'vehicle_year',
            'cover_start_date', 'vehicle_registration_number', 'cover_type', 'evaluated', 'vehicle_value', 'created_at', 'updated_at'
        ]


class HealthInsuranceSerializer(serializers.ModelSerializer):
    insuarance= InsuranceSerializer(read_only=True)
    class Meta:
        model = HealthInsurance
        fields = [
            'id', 'high_range', 'low_range','cover_type', 'price','created_at', 'updated_at'
        ]
        read_only_fields = ('created_at', 'updated_at')


class BenefitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Benefit
        fields = ['id', 'insurance', 'limit_of_liability', 'rate', 'price', 'description', 'created_at', 'updated_at']


class PolicySerializer(serializers.ModelSerializer):
    end_date = serializers.DateField(read_only=True)

    class Meta:
        model = Policy
        fields = [
            'id', 'applicant', 'insurance', 'benefits', 'policy_number', 'start_date', 'end_date', 'duration', 'status', 'created_at', 'updated_at'
        ]

    def create(self, validated_data):
        benefits = validated_data.pop('benefits', [])
        policy = Policy.objects.create(**validated_data)
        policy.benefits.set(benefits)
        return policy

    def update(self, instance, validated_data):
        benefits = validated_data.pop('benefits', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if benefits is not None:
            instance.benefits.set(benefits)
        instance.save()
        return instance

class HealthInsuranceQuoteRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthInsuaranceQuoteRequest
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class HealthLifestyleSerializer(serializers.ModelSerializer):
    health_insuarance_quote_request = HealthInsuranceQuoteRequestSerializer()  # Nested serializer

    class Meta:
        model = HealthLifestyle
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

    def create(self, validated_data):
        # Handle nested serializer creation for HealthInsuranceQuoteRequest
        quote_request_data = validated_data.pop('health_insurance_quote_request')
        quote_request = HealthInsuaranceQuoteRequest.objects.create(**quote_request_data)
        health_lifestyle = HealthLifestyle.objects.create(
            health_insurance_quote_request=quote_request,
            **validated_data
        )
        return health_lifestyle

    def update(self, instance, validated_data):
        # Handle nested serializer update for HealthInsuranceQuoteRequest
        quote_request_data = validated_data.pop('health_insurance_quote_request', None)
        if quote_request_data:
            for key, value in quote_request_data.items():
                setattr(instance.health_insurance_quote_request, key, value)
            instance.health_insurance_quote_request.save()

        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance


