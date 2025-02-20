from django.core.management.base import BaseCommand
import random
from datetime import datetime, timedelta
from insure.models import Policy, Applicant, Insurance  # Adjust import as needed

class Command(BaseCommand):
    help = "Seed the Policy model with a sample policy using the latest applicant and insurance"

    def handle(self, *args, **options):
        # Fetch the latest Applicant and Insurance
        latest_applicant = Applicant.objects.latest("created_at")
        latest_insurance = Insurance.objects.latest("created_at")

        if not latest_applicant or not latest_insurance:
            self.stdout.write(self.style.ERROR("No Applicant or Insurance found. Please add them first."))
            return

        # Generate random policy data
        cover_types = ["Comprehensive", "Third-Party", "Fire & Theft"]
        risk_names = ["Low", "Medium", "High"]
        status_choices = ["PENDING", "ACTIVE", "EXPIRED", "CANCELLED"]

        policy = Policy.objects.create(
            applicant=latest_applicant,
            insurance=latest_insurance,
            cover_type=random.choice(cover_types),
            risk_name=random.choice(risk_names),
            age=random.randint(18, 70),
            policy_number=f"POL-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
            total_amount=round(random.uniform(500, 5000), 2),
            start_date=datetime.now().date(),
            duration=random.randint(6, 24),  # Random duration between 6 and 24 months
            status=random.choice(status_choices),
        )

        policy.save()
        self.stdout.write(self.style.SUCCESS(f"Policy '{policy.policy_number}' created successfully!"))
