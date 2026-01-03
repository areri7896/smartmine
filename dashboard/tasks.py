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

import os
import requests
from django.core.cache import cache

def convert_kes_to_usd(amount_kes):
    """
    Converts the given amount in Kenyan Shillings (KES) to US Dollars (USD)
    using the ExchangeRate-API.
    Uses caching to minimize API calls.
    """
    # Cache key for the exchange rate (USD to KES)
    cache_key = "exchange_rate_usd_kes"
    rate = cache.get(cache_key)

    if rate is None:
        try:
            api_key = os.getenv("EXCHANGERATE_API_KEY")
            if not api_key:
                raise ValueError("ExchangeRate-API key not found in environment variables.")
            base_currency = "USD"
            url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{base_currency}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            rate = data["conversion_rates"]["KES"]
            cache.set(cache_key, rate, timeout=60 * 60)  # Cache for 1 hour
        except requests.exceptions.RequestException as req_err:
            print(f"Network error during currency conversion: {req_err}")
            return None
        except (KeyError, ValueError) as e:
            print(f"Currency conversion failed: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error during currency conversion: {e}")
            return None

    # Since rate is USD to KES, use inverse for KES to USD conversion
    return round(amount_kes / rate, 2)