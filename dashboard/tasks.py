# tasks.py
from celery import shared_task
from .models import Investment

# @shared_task
# def process_expired_investments():
#     from django.utils import timezone
#     investments = Investment.objects.filter(is_active=True)
#     for investment in investments:
#         investment.process_completion()


import requests
from django.core.cache import cache
from celery import shared_task
from django.utils import timezone
from django.db import transaction
import logging
from .models import Investment

logger = logging.getLogger(__name__)

@shared_task
def process_expired_investments():
    """
    Check all active investments and process those that have expired.
    """
    try:
        # Filter investments that are not completed and have passed their end_date
        investments = Investment.objects.filter(
            is_completed=False,
            status="active",
            db_end_date__lte=timezone.now()
        ).select_related("user", "plan")  # Optimize query with related fields

        logger.info(f"Found {investments.count()} investments to process")

        for investment in investments:
            try:
                with transaction.atomic():
                    investment.process_completion()
                    logger.info(f"Processed investment {investment.id} for user {investment.user}")
            except Exception as e:
                logger.error(f"Error processing investment {investment.id}: {str(e)}")
                continue

    except Exception as e:
        logger.error(f"Error in process_expired_investments task: {str(e)}")


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
