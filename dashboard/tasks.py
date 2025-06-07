# tasks.py
from celery import shared_task
from .models import Investment

@shared_task
def process_expired_investments():
    from django.utils import timezone
    investments = Investment.objects.filter(is_active=True)
    for investment in investments:
        investment.process_completion()


# myapp/tasks.py
import requests
from celery import shared_task
from django.core.cache import cache

@shared_task
def update_exchange_rate_kes_usd():
    """
    Fetch and cache the KES to USD exchange rate.
    """
    try:
        url = "https://api.frankfurter.app/latest"
        params = {"amount": 1, "from": "KES", "to": "USD"}
        response = requests.get(url, params=params)
        response.raise_for_status()
        rate = response.json()["rates"]["USD"]
        cache.set("exchange_rate_kes_usd", rate, timeout=60 * 60)  # 1 hour
        return rate
    except Exception as e:
        print(f"Failed to update exchange rate: {e}")
        return None
