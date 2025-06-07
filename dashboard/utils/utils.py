# myapp/utils.py
import requests
from django.core.cache import cache

def convert_kes_to_usd(amount_kes):
    """
    Converts the given amount in KES to USD using the Frankfurter API.
    Uses caching to minimize API calls.
    """
    # Cache key for the exchange rate
    cache_key = "exchange_rate_kes_usd"
    rate = cache.get(cache_key)

    if rate is None:
        try:
            url = "https://api.frankfurter.app/latest"
            params = {"amount": 1, "from": "KES", "to": "USD"}
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            rate = data["rates"]["USD"]
            cache.set(cache_key, rate, timeout=60 * 60)  # cache for 1 hour
        except requests.exceptions.RequestException as req_err:
            print(f"Network error: {req_err}")
            return None
        except KeyError:
            print("Currency conversion failed: USD rate not found.")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None

    return round(rate * amount_kes, 2)
