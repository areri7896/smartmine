import os
import django
import sys

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from dashboard.models import Profile, Wallet
from django.urls import reverse

def verify_new_user():
    username = "testuser_verification_01"
    email = "test_verification_01@example.com"
    password = "password123"

    # Cleanup existing
    User.objects.filter(username=username).delete()

    print(f"Creating user: {username}")
    user = User.objects.create_user(username=username, email=email, password=password)

    # Check Profile
    try:
        profile = Profile.objects.get(user=user)
        print(f"[PASS] Profile created for {username}")
        print(f"       - is_complete: {profile.is_complete}")
        print(f"       - show_terms_modal: {profile.show_terms_modal}")
    except Profile.DoesNotExist:
        print(f"[FAIL] Profile NOT created for {username}")
        profile = None

    # Check Wallet
    try:
        wallet = Wallet.objects.get(user=user)
        print(f"[PASS] Wallet created for {username}")
        print(f"       - balance: {wallet.balance}")
    except Wallet.DoesNotExist:
        print(f"[FAIL] Wallet NOT created for {username}")

    if profile and not profile.is_complete:
        print("\nAnalysis: Profile.is_complete is False.")
        print("          Middleware WILL redirect to 'profile' page.")
    else:
        print("\nAnalysis: Profile.is_complete is True.")
        print("          Middleware WILL NOT redirect.")

if __name__ == "__main__":
    verify_new_user()
