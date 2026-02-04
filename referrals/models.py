import random
import string
from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

class ReferralCode(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='referral_code')
    code = models.CharField(max_length=20, unique=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_unique_code()
        super().save(*args, **kwargs)

    def generate_unique_code(self):
        length = getattr(settings, 'REFERRAL_CONFIG', {}).get('CODE_LENGTH', 8)
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
            if not ReferralCode.objects.filter(code=code).exists():
                return code

    def __str__(self):
        return f"{self.user.username} - {self.code}"

class Referral(models.Model):
    referrer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referrals_made')
    referred = models.OneToOneField(User, on_delete=models.CASCADE, related_name='referred_by')
    level = models.PositiveIntegerField(default=1)  # 1 for direct, 2 for second level, etc.
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.referrer.username} -> {self.referred.username} (Level {self.level})"

class ReferralReward(models.Model):
    REWARD_TYPES = (
        ('signup', 'Signup Bonus'),
        ('deposit', 'Deposit Commission'),
        ('trade', 'Trading Commission'),
        ('investment', 'Investment Commission'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    )

    referrer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referral_rewards')
    referred = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rewards_generated')
    reward_type = models.CharField(max_length=20, choices=REWARD_TYPES)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    level = models.PositiveIntegerField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.referrer.username} - {self.reward_type} - {self.amount}"
