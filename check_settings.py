import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

print(f"DEBUG: {settings.DEBUG}")
print(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
print(f"SECURE_SSL_REDIRECT: {getattr(settings, 'SECURE_SSL_REDIRECT', 'Not Set')}")
