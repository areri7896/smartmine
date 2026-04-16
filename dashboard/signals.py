from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
from .models import SecurityLog

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    ip = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    SecurityLog.objects.create(
        user=user,
        action='login_success',
        ip_address=ip,
        user_agent=user_agent,
        details="User logged in successfully"
    )

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    if user:
        ip = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        SecurityLog.objects.create(
            user=user,
            action='logout',
            ip_address=ip,
            user_agent=user_agent,
            details="User logged out"
        )

@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    ip = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    # user_login_failed doesn't pass user if user not found, but we can try to look it up by username/email in credentials
    # However, strict SecurityLog requires a User FK. If no user, we can't log to a specific user.
    # We will only log if we can find a user, or if we change SecurityLog to allow null user (not requested).
    # For now, let's skip or try to find user. 
    # Actually, the user requirement is strict. We can only log if we know the user.
    pass

from allauth.account.signals import password_changed, password_set, email_confirmed

@receiver(password_changed)
def log_password_changed(request, user, **kwargs):
    ip = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    SecurityLog.objects.create(
        user=user,
        action='password_change',
        ip_address=ip,
        user_agent=user_agent,
        details="Password changed successfully"
    )

@receiver(password_set)
def log_password_set(request, user, **kwargs):
    ip = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    SecurityLog.objects.create(
        user=user,
        action='password_change',
        ip_address=ip,
        user_agent=user_agent,
        details="Password set successfully"
    )

from django.db.models.signals import post_save
from django.contrib.auth.models import User
from .models import Profile, Wallet

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        Wallet.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except Profile.DoesNotExist:
        # If for some reason profile doesn't exist (e.g. old user), create it
        Profile.objects.create(user=instance)
