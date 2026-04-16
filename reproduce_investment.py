import os
import django
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from dashboard.models import Investment, InvestmentPlan, Wallet
from dashboard.cron import process_daily_profits

User = get_user_model()

def run_test():
    print("Starting Investment Logic Verification...")
    
    # 1. Setup Test User and Wallet
    username = "test_investor_adv"
    user, created = User.objects.get_or_create(username=username)
    if created:
        user.set_password("password123")
        user.save()
        print(f"Created test user: {username}")
    
    wallet, w_created = Wallet.objects.get_or_create(user=user)
    # Ensure sufficient balance
    wallet.balance = Decimal("100000.00") # Plenty of KES
    wallet.save()
    print(f"Wallet balance set to: {wallet.balance}")
    
    # 2. Setup Investment Plan
    # Plan: 5 days, 10% daily interest, Price $10 (approx 1290 KES)
    plan_name = "Test Plan Logic"
    plan, p_created = InvestmentPlan.objects.get_or_create(
        name=plan_name,
        defaults={
            "price": Decimal("10.00"),
            "daily_interest_rate": Decimal("10.00"),
            "cycle_days": 5,
            "description": "Test Plan"
        }
    )
    if not p_created:
        # Reset values just in case
        plan.price = Decimal("10.00")
        plan.daily_interest_rate = Decimal("10.00")
        plan.cycle_days = 5
        plan.save()
    print(f"Plan '{plan.name}' ready. Cost: ${plan.price}, ROI: {plan.daily_interest_rate}%/day for {plan.cycle_days} days.")
    
    # 3. Create Investment
    # Ensure no previous active investments for this test
    Investment.objects.filter(user=user, plan=plan, status="active").delete()
    
    try:
        investment = Investment.create_investment(user, plan)
        print(f"Investment created. ID: {investment.id}, Status: {investment.status}")
        print(f"Principal: {investment.principal_amount}, Daily Profit: {investment.expected_daily_profit}")
    except Exception as e:
        print(f"Failed to create investment: {e}")
        return

    # 4. Simulate Passing of Time and Processing Profits
    # We will manually adjust start_date and last_profit_date to simulate days passing
    
    wallet.refresh_from_db() # Fix: Refresh to get balance AFTER investment deduction
    initial_balance = wallet.balance
    expected_daily_profit_usd = investment.expected_daily_profit
    # Hardcoded rate matching models.py verification
    rate = Decimal('129.0')
    expected_daily_profit_kes = expected_daily_profit_usd * rate
    
    print(f"Initial Balance after investment: {initial_balance}")
    print(f"Expected Daily Profit (KES): {expected_daily_profit_kes}")
    
    current_balance = initial_balance
    
    for day in range(1, plan.cycle_days + 1):
        print(f"\n--- Simulating Day {day} ---")
        
        # Move start date back to ensure 'today' is valid for processing
        investment.start_date = timezone.now() - timedelta(days=day)
        # Reset last_profit_date so it thinks it hasn't been paid today yet
        investment.last_profit_date = timezone.now().date() - timedelta(days=1)
        investment.save()
        
        # Run Profit Processing
        process_daily_profits()
        
        # Verify
        investment.refresh_from_db()
        wallet.refresh_from_db()
        
        print(f"Profits Paid: {investment.days_profit_paid}/{plan.cycle_days}")
        print(f"Total Profit Paid: {investment.total_profit_paid}")
        print(f"Wallet Balance: {wallet.balance}")
        
        current_balance += expected_daily_profit_kes
        
        # On the last day, completion happens automatically in the same transaction/process
        if day == plan.cycle_days:
             principal_kes = investment.principal_amount * rate
             current_balance += principal_kes
             print(f" (Last Day: Adding Principal {principal_kes} to expected balance)")
        
        if wallet.balance == current_balance:
             print("SUCCESS: Balance matches expectations.")
        else:
             print(f"FAILURE: Balance {wallet.balance} != Expected {current_balance}")

    # 5. Check Completion
    print(f"\n--- Verification of Completion ---")
    investment.refresh_from_db()
    wallet.refresh_from_db()
    
    if investment.status == "completed":
        print("SUCCESS: Investment marked as completed.")
        
        # Principal Verification
        principal_kes = investment.principal_amount * rate
        # expected_final_balance = current_balance + principal_kes 
        # current_balance already tracked principal return in the loop
        expected_final_balance = current_balance
        
        print(f"Principal (USD): {investment.principal_amount}")
        print(f"Principal (KES): {principal_kes}")
        print(f"Wallet Balance Final: {wallet.balance}")
        
        if wallet.balance == expected_final_balance:
            print("SUCCESS: Principal returned correctly in KES.")
        else:
            print(f"FAILURE: Final Balance {wallet.balance} != Expected {expected_final_balance}")
            
    else:
        print(f"FAILURE: Investment status is {investment.status}")


if __name__ == "__main__":
    run_test()
