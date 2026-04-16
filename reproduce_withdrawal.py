import os
import django
from decimal import Decimal

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from dashboard.models import Withdrawal, Wallet

User = get_user_model()

def run_test():
    print("Starting Withdrawal Logic Verification...")
    
    # 1. Setup Test User and Wallet
    username = "test_withdrawal_user"
    user, created = User.objects.get_or_create(username=username)
    if created:
        user.set_password("password123")
        user.save()
        print(f"Created test user: {username}")
    
    wallet, w_created = Wallet.objects.get_or_create(user=user)
    # Set initial balance
    wallet.balance = Decimal("1000.00")
    wallet.save()
    print(f"Initial Wallet Balance: {wallet.balance} KES")
    
    # 2. Test 1: Create Withdrawal Request (Should deduct immediately in real flow)
    # Since we're testing the model layer, we'll simulate the view's deduction
    print("\n--- Test 1: Creating Withdrawal Request ---")
    
    # Simulate what the view does
    withdrawal_amount = Decimal("200.00")
    wallet.balance -= withdrawal_amount
    wallet.save()
    
    withdrawal = Withdrawal.objects.create(
        user=user,
        phone_number="0111439382",
        amount=withdrawal_amount,
        status='pending'
    )
    
    wallet.refresh_from_db()
    expected_balance = Decimal("800.00")
    print(f"Withdrawal created. ID: {withdrawal.id}, Amount: {withdrawal.amount}, Status: {withdrawal.status}")
    print(f"Wallet Balance after deduction: {wallet.balance} KES")
    
    if wallet.balance == expected_balance:
        print("SUCCESS: Balance deducted correctly.")
    else:
        print(f"FAILURE: Expected {expected_balance}, got {wallet.balance}")
    
    # 3. Test 2: Cancel Withdrawal (Should refund automatically)
    print("\n--- Test 2: Cancelling Withdrawal (Refund Test) ---")
    
    withdrawal.status = 'cancelled'
    withdrawal.save()
    
    wallet.refresh_from_db()
    expected_balance_after_refund = Decimal("1000.00")
    print(f"Withdrawal status changed to: {withdrawal.status}")
    print(f"Wallet Balance after refund: {wallet.balance} KES")
    
    if wallet.balance == expected_balance_after_refund:
        print("SUCCESS: Balance refunded correctly on cancellation.")
    else:
        print(f"FAILURE: Expected {expected_balance_after_refund}, got {wallet.balance}")
    
    # 4. Test 3: Create Another Withdrawal and Complete It (Should NOT refund)
    print("\n--- Test 3: Completing Withdrawal (No Refund Test) ---")
    
    # Simulate deduction again
    withdrawal_amount2 = Decimal("300.00")
    wallet.balance -= withdrawal_amount2
    wallet.save()
    
    withdrawal2 = Withdrawal.objects.create(
        user=user,
        phone_number="0111439382",
        amount=withdrawal_amount2,
        status='pending'
    )
    
    wallet.refresh_from_db()
    balance_after_deduction = wallet.balance
    print(f"Second withdrawal created. Amount: {withdrawal2.amount}")
    print(f"Wallet Balance after deduction: {balance_after_deduction} KES")
    
    # Mark as completed
    withdrawal2.status = 'completed'
    withdrawal2.save()
    
    wallet.refresh_from_db()
    print(f"Withdrawal status changed to: {withdrawal2.status}")
    print(f"Wallet Balance (should remain same): {wallet.balance} KES")
    
    if wallet.balance == balance_after_deduction:
        print("SUCCESS: No refund on completion (correct behavior).")
    else:
        print(f"FAILURE: Balance changed unexpectedly. Expected {balance_after_deduction}, got {wallet.balance}")
    
    # 5. Test 4: Test Failed Status (Should refund)
    print("\n--- Test 4: Failing Withdrawal (Refund Test) ---")
    
    # Simulate deduction
    withdrawal_amount3 = Decimal("150.00")
    wallet.balance -= withdrawal_amount3
    wallet.save()
    
    withdrawal3 = Withdrawal.objects.create(
        user=user,
        phone_number="0111439382",
        amount=withdrawal_amount3,
        status='pending'
    )
    
    balance_before_fail = wallet.balance
    print(f"Third withdrawal created. Amount: {withdrawal3.amount}")
    print(f"Wallet Balance after deduction: {balance_before_fail} KES")
    
    # Mark as failed
    withdrawal3.status = 'failed'
    withdrawal3.save()
    
    wallet.refresh_from_db()
    expected_balance_after_fail_refund = balance_before_fail + withdrawal_amount3
    print(f"Withdrawal status changed to: {withdrawal3.status}")
    print(f"Wallet Balance after refund: {wallet.balance} KES")
    
    if wallet.balance == expected_balance_after_fail_refund:
        print("SUCCESS: Balance refunded correctly on failure.")
    else:
        print(f"FAILURE: Expected {expected_balance_after_fail_refund}, got {wallet.balance}")
    
    print("\n=== All Tests Completed ===")

if __name__ == "__main__":
    run_test()
