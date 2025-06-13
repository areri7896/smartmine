import requests
from django.conf import settings
from decouple import config

def fetch_pair_conversion(base_currency, target_currency, amount):
    """
    Fetch exchange rate or converted amount between two currencies using the Pair Conversion API.
    
    Args:
        base_currency (str): The base currency code (e.g., 'USD')
        target_currency (str): The target currency code (e.g., 'EUR')
        amount (float, optional): Amount to convert (in base currency)
    
    Returns:
        dict: Contains base currency, target currency, conversion rate, and (if provided) converted amount
    
    Raises:
        Exception: If the API request fails or returns an error
    """
    api_key = config('EXCHANGERATE_API_KEY')
    url = f'https://v6.exchangerate-api.com/v6/{api_key}/pair/{base_currency}/{target_currency}'
    if amount is not None:
        url += f'/{amount}'
    
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        data = response.json()
        
        if data.get('result') == 'success':
            result = {
                'base': data['base_code'],
                'target': data['target_code'],
                'conversion_rate': data['conversion_rate'],
                'last_update': data['time_last_update_utc']
            }
            if amount is not None:
                result['converted_amount'] = data['conversion_result']
            return result
        else:
            error_type = data.get('error-type', 'API request failed')
            raise Exception(f'API error: {error_type}')
            
    except requests.RequestException as e:
        raise Exception(f'Error fetching pair conversion: {str(e)}')

# Example usage in a Django view:
"""
from django.http import JsonResponse

def pair_conversion_view(request):
    base_currency = request.GET.get('base', 'USD')
    target_currency = request.GET.get('target', 'EUR')
    amount = request.GET.get('amount')  # Optional amount as string
    
    try:
        amount = float(amount) if amount else None
        conversion_data = fetch_pair_conversion(base_currency, target_currency, amount)
        return JsonResponse({
            'status': 'success',
            'base': conversion_data['base'],
            'target': conversion_data['target'],
            'conversion_rate': conversion_data['conversion_rate'],
            'last_update': conversion_data['last_update'],
            **({'converted_amount': conversion_data['converted_amount']} if amount else {})
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
"""