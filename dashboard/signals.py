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
        action='login',
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
