from django.conf import settings
from django.db import transaction
from decimal import Decimal
from .models import Referral, ReferralReward, ReferralCode
from django.contrib.auth import get_user_model

User = get_user_model()

def apply_referral_logic(referred_user, code):
    """
    Called after a user signs up with a referral code.
    Creates multi-level referral relationships.
    """
    try:
        referral_code_obj = ReferralCode.objects.get(code=code, is_active=True)
        referrer = referral_code_obj.user
        
        if referrer == referred_user:
            return False # No self-referral

        # Level 1 Referral
        Referral.objects.create(referrer=referrer, referred=referred_user, level=1)
        
        # Check if referrer was also referred (to create Level 2)
        try:
            parent_referral = Referral.objects.get(referred=referrer, level=1)
            Referral.objects.create(referrer=parent_referral.referrer, referred=referred_user, level=2)
            
            # Check for Level 3
            try:
                grandparent_referral = Referral.objects.get(referred=parent_referral.referrer, level=1)
                Referral.objects.create(referrer=grandparent_referral.referrer, referred=referred_user, level=3)
            except Referral.DoesNotExist:
                pass
        except Referral.DoesNotExist:
            pass
            
        return True
    except ReferralCode.DoesNotExist:
        return False

def process_referral_rewards(user, amount, reward_type, transaction_id=None):
    """
    Process rewards for a given user activity (deposit, trade, etc.)
    Credits all referrers in the chain based on the level commission.
    """
    config = getattr(settings, 'REFERRAL_CONFIG', {})
    if not config.get('ENABLED', False):
        return False

    if reward_type not in config.get('REWARD_TRIGGERS', []):
        return False

    commissions = config.get('LEVEL_COMMISSIONS', {})
    referrals = Referral.objects.filter(referred=user)

    for referral in referrals:
        rate = commissions.get(referral.level)
        if rate:
            reward_amount = Decimal(amount) * Decimal(rate)
            if reward_amount > 0:
                with transaction.atomic():
                    # Create reward record
                    reward = ReferralReward.objects.create(
                        referrer=referral.referrer,
                        referred=user,
                        reward_type=reward_type,
                        amount=reward_amount,
                        level=referral.level,
                        transaction_id=transaction_id,
                        status='approved' # Auto-approve for now
                    )
                    
                    # Credit Referrer's Wallet
                    try:
                        from dashboard.models import Wallet
                        wallet, _ = Wallet.objects.get_or_create(user=referral.referrer)
                        wallet.balance += reward_amount
                        wallet.save()
                        
                        reward.status = 'paid'
                        reward.save()
                    except ImportError:
                        pass # Dashboard app not found or Wallet model move
                    except Exception as e:
                        print(f"Error crediting wallet: {e}")
    
    return True
