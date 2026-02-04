from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Referral, ReferralReward, ReferralCode
from django.db.models import Sum, Count

@login_required
def referral_dashboard(request):
    user = request.user
    referral_code, _ = ReferralCode.objects.get_or_create(user=user)
    
    # Stats
    total_referrals = Referral.objects.filter(referrer=user).count()
    total_earnings = ReferralReward.objects.filter(referrer=user, status='paid').aggregate(total=Sum('amount'))['total'] or 0
    pending_earnings = ReferralReward.objects.filter(referrer=user, status='pending').aggregate(total=Sum('amount'))['total'] or 0
    
    # Tables
    referrals = Referral.objects.filter(referrer=user).select_related('referred').order_by('-created_at')
    recent_rewards = ReferralReward.objects.filter(referrer=user).order_by('-created_at')[:10]
    
    context = {
        'referral_code': referral_code.code,
        'referral_link': request.build_absolute_uri(f"/accounts/signup/?ref={referral_code.code}"),
        'total_referrals': total_referrals,
        'total_earnings': total_earnings,
        'pending_earnings': pending_earnings,
        'referrals': referrals,
        'recent_rewards': recent_rewards,
    }
    
    return render(request, 'referrals/dashboard.html', context)
