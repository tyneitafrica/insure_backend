

import cloudinary_storage.storage
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="HealthInsuaranceQuoteRequest",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("first_name", models.CharField(blank=True, max_length=100, null=True)),
                ("last_name", models.CharField(blank=True, max_length=100, null=True)),
                ("dob", models.DateField(blank=True, null=True)),
                ("national_id", models.BigIntegerField()),
                ("occupation", models.CharField(blank=True, max_length=200, null=True)),
                (
                    "phone_number",
                    models.CharField(blank=True, max_length=20, null=True),
                ),
                (
                    "gender",
                    models.CharField(
                        choices=[
                            ("MALE", "Male"),
                            ("FEMALE", "Female"),
                            ("OTHER", "Other"),
                        ],
                        default="MALE",
                        max_length=20,
                    ),
                ),
                (
                    "coverage_amount",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=10, null=True
                    ),
                ),
                (
                    "coverage_type",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                (
                    "is_travel_related",
                    models.BooleanField(blank=True, default=False, null=True),
                ),
                (
                    "is_covered",
                    models.BooleanField(blank=True, default=False, null=True),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="Insurance",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "company_name",
                    models.CharField(blank=True, max_length=200, null=True),
                ),
                (
                    "insurance_image",
                    models.ImageField(
                        blank=True,
                        null=True,
                        storage=cloudinary_storage.storage.RawMediaCloudinaryStorage(),
                        upload_to="insurance_images/",
                    ),
                ),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("Motor", "Motor"),
                            ("Health", "Health"),
                            ("Personal Accident", "Personal Accident"),
                            ("Life", "Life"),
                            ("Marine", "Marine"),
                            ("Professional Indemnity", "Professional Indemnity"),
                        ],
                        max_length=50,
                    ),
                ),
                ("title", models.CharField(max_length=100)),
                ("description", models.TextField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="MarineInsuranceTempData",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("first_name", models.CharField(max_length=50)),
                ("last_name", models.CharField(max_length=50)),
                ("email", models.EmailField(max_length=254)),
                ("phone_number", models.CharField(max_length=20)),
                ("id_no", models.CharField(max_length=20)),
                ("vessel_type", models.CharField(max_length=100)),
                (
                    "coverage_type",
                    models.CharField(
                        choices=[
                            ("Hull Insurance", "Hull Insurance"),
                            ("Cargo Insurance", "Cargo Insurance"),
                            ("Freight Insurance", "Freight Insurance"),
                        ],
                        max_length=100,
                    ),
                ),
                ("is_evaluated", models.BooleanField(default=False)),
                (
                    "evaluated_price",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=100, null=True
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="MotorInsuranceTempData",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("first_name", models.CharField(max_length=50)),
                ("last_name", models.CharField(max_length=50)),
                ("email", models.EmailField(max_length=254)),
                ("phone_number", models.CharField(max_length=20)),
                ("id_no", models.CharField(max_length=20)),
                ("yob", models.DateField()),
                ("age", models.IntegerField(default=0)),
                (
                    "vehicle_category",
                    models.CharField(
                        choices=[
                            ("Private", "Private"),
                            ("Commercial", "Commercial"),
                            ("Public Service", "Public Service"),
                        ],
                        max_length=100,
                    ),
                ),
                ("vehicle_type", models.CharField(max_length=100)),
                ("vehicle_model", models.CharField(max_length=100)),
                ("vehicle_year", models.IntegerField()),
                ("vehicle_age", models.IntegerField()),
                (
                    "vehicle_value",
                    models.DecimalField(decimal_places=2, max_digits=100),
                ),
                ("cover_start_date", models.DateField()),
                (
                    "evaluated_price",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=100, null=True
                    ),
                ),
                ("vehicle_registration_number", models.CharField(max_length=100)),
                (
                    "insurance_type",
                    models.CharField(
                        choices=[
                            ("comprehensive", "Comprehensive"),
                            ("third_party", "Third Party"),
                        ],
                        max_length=50,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="RiskType",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "risk_name",
                    models.CharField(
                        choices=[
                            ("Motor_Private", "Motor_Private"),
                            ("General_Cortage", "General_Cortage"),
                            ("Institutional_Vehicles", "Institutional_Vehicles"),
                            ("Online_Taxis", "Online_Taxis"),
                            ("Own_Goods", "Own_Goods"),
                            ("Chaffer_Driven", "Chaffer_Driven"),
                            ("Chaffer_driven_taxi", "Chaffer_driven_taxi"),
                            ("Motor_Psv", "Motor_Psv"),
                        ],
                        max_length=100,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="VehicleType",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "vehicle_category",
                    models.CharField(
                        choices=[
                            ("Private", "Private"),
                            ("Commercial", "Commercial"),
                            ("Public_Service", "Public_Service"),
                        ],
                        max_length=100,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="first name"
                    ),
                ),
                (
                    "last_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="last name"
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
                (
                    "role",
                    models.CharField(
                        choices=[
                            ("ADMIN", "Admin"),
                            ("ORGANISATION", "Organisation"),
                            ("APPLICANT", "Applicant"),
                        ],
                        default="APPLICANT",
                        max_length=20,
                    ),
                ),
                ("otp", models.CharField(blank=True, max_length=7, null=True)),
                ("otp_expiration", models.DateTimeField(blank=True, null=True)),
                ("email", models.EmailField(max_length=254, unique=True)),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "verbose_name": "user",
                "verbose_name_plural": "users",
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Applicant",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("phone_number", models.CharField(max_length=20)),
                ("yob", models.DateField(blank=True, null=True)),
                ("id_no", models.CharField(max_length=20, unique=True)),
                ("occupation", models.CharField(max_length=100)),
                (
                    "gender",
                    models.CharField(
                        choices=[("Male", "Male"), ("Female", "Female")], max_length=10
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="applicant_profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ApplicantKYC",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "national_id",
                    models.ImageField(
                        blank=True,
                        null=True,
                        storage=cloudinary_storage.storage.RawMediaCloudinaryStorage(),
                        upload_to="national_id_images/",
                    ),
                ),
                (
                    "driving_license",
                    models.ImageField(
                        blank=True,
                        null=True,
                        storage=cloudinary_storage.storage.RawMediaCloudinaryStorage(),
                        upload_to="driving_license_images/",
                    ),
                ),
                (
                    "valuation_report",
                    models.ImageField(
                        blank=True,
                        null=True,
                        storage=cloudinary_storage.storage.RawMediaCloudinaryStorage(),
                        upload_to="valuation_report_images/",
                    ),
                ),
                (
                    "kra_pin_certificate",
                    models.ImageField(
                        blank=True,
                        null=True,
                        storage=cloudinary_storage.storage.RawMediaCloudinaryStorage(),
                        upload_to="kra_pin_certificate_images/",
                    ),
                ),
                (
                    "log_book",
                    models.ImageField(
                        blank=True,
                        null=True,
                        storage=cloudinary_storage.storage.RawMediaCloudinaryStorage(),
                        upload_to="log_book_images/",
                    ),
                ),
                ("is_uploded", models.BooleanField(default=False)),
                (
                    "applicant",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="kyc_details",
                        to="insure.applicant",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="HealthLifestyle",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("pre_existing_condition", models.BooleanField(default=False)),
                ("high_risk_activities", models.BooleanField(default=False)),
                ("medication", models.BooleanField(default=False)),
                (
                    "mode_of_transport",
                    models.CharField(blank=True, max_length=200, null=True),
                ),
                ("smoking", models.BooleanField(default=False)),
                ("past_claim", models.BooleanField(default=False)),
                ("stress_level", models.BooleanField(default=False)),
                ("family_history", models.BooleanField(default=False)),
                ("allergies", models.BooleanField(default=False)),
                ("mental_health", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "health_insuarance_quote_request",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="health_lifestyle",
                        to="insure.healthinsuarancequoterequest",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="HealthInsurance",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("high_range", models.IntegerField()),
                ("low_range", models.IntegerField()),
                ("cover_type", models.CharField(max_length=100)),
                ("price", models.DecimalField(decimal_places=2, max_digits=10)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "insurance",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="health_details",
                        to="insure.insurance",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Benefit",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("limit_of_liability", models.CharField(max_length=100)),
                ("rate", models.DecimalField(decimal_places=2, max_digits=5)),
                ("price", models.DecimalField(decimal_places=2, max_digits=10)),
                ("description", models.TextField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "insurance",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="benefits",
                        to="insure.insurance",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="MarineInsurance",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "vessel_type",
                    models.CharField(
                        choices=[
                            ("Fishing Boat", "Fishing Boat"),
                            ("Cargo", "Cargo"),
                            ("Yacht", "Yacht"),
                        ],
                        max_length=100,
                    ),
                ),
                ("cargo_type", models.CharField(blank=True, max_length=100, null=True)),
                (
                    "voyage_type",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                (
                    "coverage_type",
                    models.CharField(
                        choices=[
                            ("Hull Insurance", "Hull Insurance"),
                            ("Cargo Insurance", "Cargo Insurance"),
                            ("Freight Insurance", "Freight Insurance"),
                        ],
                        max_length=100,
                    ),
                ),
                ("price", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "insurance",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="marine_details",
                        to="insure.insurance",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="MotorInsurance",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "cover_type",
                    models.CharField(
                        choices=[
                            ("Comprehensive", "Comprehensive"),
                            ("Third Party Only", "Third Party Only"),
                            (
                                "Third Party Fire and Theft",
                                "Third Party Fire and Theft",
                            ),
                        ],
                        max_length=100,
                    ),
                ),
                (
                    "insurance",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="motor_details",
                        to="insure.insurance",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ExcessCharges",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("limit_of_liability", models.CharField(max_length=100)),
                ("excess_rate", models.DecimalField(decimal_places=2, max_digits=5)),
                ("min_price", models.DecimalField(decimal_places=2, max_digits=10)),
                ("description", models.TextField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "motor_insurance",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="excess_charges",
                        to="insure.motorinsurance",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="OptionalExcessCharge",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "under_21_age_charge",
                    models.DecimalField(decimal_places=2, default=0.0, max_digits=12),
                ),
                (
                    "under_1_year_experience_charge",
                    models.DecimalField(decimal_places=2, default=0.0, max_digits=12),
                ),
                (
                    "insurance",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="optional_excess_charges",
                        to="insure.insurance",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Organisation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("company_name", models.CharField(max_length=100)),
                ("phone_number", models.CharField(max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="organisation_profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="insurance",
            name="organisation",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="insurances",
                to="insure.organisation",
            ),
        ),
        migrations.CreateModel(
            name="Policy",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("cover_type", models.CharField(blank=True, max_length=100, null=True)),
                ("risk_name", models.CharField(blank=True, max_length=100, null=True)),
                ("age", models.IntegerField(blank=True, null=True)),
                ("policy_number", models.CharField(max_length=200, unique=True)),
                ("total_amount", models.FloatField(blank=True, null=True)),
                ("start_date", models.DateField()),
                ("end_date", models.DateField(blank=True, null=True)),
                ("duration", models.PositiveIntegerField(default=12)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("PENDING", "Pending"),
                            ("ACTIVE", "Active"),
                            ("EXPIRED", "Expired"),
                            ("CANCELLED", "Cancelled"),
                        ],
                        default="PENDING",
                        max_length=20,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "applicant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="policies",
                        to="insure.applicant",
                    ),
                ),
                (
                    "insurance",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="policies",
                        to="insure.insurance",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Payment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "invoice_id",
                    models.CharField(
                        blank=True, max_length=100, null=True, unique=True
                    ),
                ),
                (
                    "api_ref_id",
                    models.CharField(
                        blank=True, max_length=100, null=True, unique=True
                    ),
                ),
                (
                    "transaction_id",
                    models.CharField(
                        blank=True, max_length=100, null=True, unique=True
                    ),
                ),
                (
                    "merchant_request_id",
                    models.CharField(
                        blank=True, max_length=100, null=True, unique=True
                    ),
                ),
                (
                    "checkout_request_id",
                    models.CharField(
                        blank=True, max_length=100, null=True, unique=True
                    ),
                ),
                ("amount", models.FloatField(blank=True, max_length=100, null=True)),
                (
                    "phone_number",
                    models.CharField(blank=True, max_length=20, null=True),
                ),
                ("pay_method", models.CharField(blank=True, max_length=250, null=True)),
                ("pay_date", models.DateTimeField(default=django.utils.timezone.now)),
                ("description", models.TextField(blank=True, null=True)),
                ("status", models.CharField(default="PENDING", max_length=20)),
                ("result_desc", models.TextField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "policy",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="payments",
                        to="insure.policy",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="RateRange",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "usage_category",
                    models.CharField(
                        blank=True,
                        choices=[("Fleet", "Fleet"), ("Standard", "Standard")],
                        max_length=50,
                        null=True,
                    ),
                ),
                (
                    "weight_category",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("Up to 3 tons", "Up to 3 tons"),
                            ("3 tons – 8 tons", "3 tons – 8 tons"),
                            ("Over 8 tons", "Over 8 tons"),
                            ("8 tons-20 tons", "8 tons- 20 tons"),
                            ("20 tons -30 tons", "20 tons -30 tons"),
                            ("Prime mover", "Prime mover"),
                        ],
                        max_length=50,
                        null=True,
                    ),
                ),
                ("max_car_age", models.IntegerField()),
                (
                    "min_value",
                    models.DecimalField(db_index=True, decimal_places=2, max_digits=15),
                ),
                (
                    "max_value",
                    models.DecimalField(db_index=True, decimal_places=2, max_digits=15),
                ),
                (
                    "rate",
                    models.DecimalField(db_index=True, decimal_places=2, max_digits=5),
                ),
                (
                    "min_sum_assured",
                    models.DecimalField(decimal_places=2, max_digits=15),
                ),
                (
                    "motor_insurance",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="rate_ranges",
                        to="insure.motorinsurance",
                    ),
                ),
                (
                    "risk_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="insure.risktype",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="risktype",
            name="vehicle_type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="risk_type",
                to="insure.vehicletype",
            ),
        ),
    ]
