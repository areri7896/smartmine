from django.utils.timezone import now
from django.core.mail import send_mail
from .models import Investment, Wallet
from decimal import Decimal
from datetime import timedelta

def daily_profit():
    today = now().date()

    # All active investments that still have days left
    investments = Investment.objects.filter(status="active")

    for inv in investments:

        # Prevent double payment on the same day
        if inv.last_profit_date == today:
            continue

        # Stop if investment reached total days
        if inv.days_paid >= inv.total_days:
            inv.status = "completed"
            inv.save()
            continue

        # DAILY PROFIT CALCULATION
        daily_profit = (inv.plan.price * inv.plan.roi_percent / Decimal('100')) / inv.total_days

        # Add to wallet
        wallet = Wallet.objects.filter(user=inv.user).first()
        if wallet:
            wallet.balance += daily_profit
            wallet.save()

        # Update investment tracking
        inv.days_paid += 1
        inv.last_profit_date = today
        inv.profit_amount += daily_profit
        inv.save()

        # OPTIONAL: Send small daily email notification
        # (Most platforms disable this to avoid spamming)