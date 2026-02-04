from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from referrals.models import ReferralCode

User = get_user_model()

class Command(BaseCommand):
    help = 'Generates referral codes for existing users who do not have one.'

    def handle(self, *args, **options):
        users = User.objects.filter(referral_code__isnull=True)
        count = 0
        for user in users:
            ReferralCode.objects.get_or_create(user=user)
            count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Successfully generated referral codes for {count} users.'))
