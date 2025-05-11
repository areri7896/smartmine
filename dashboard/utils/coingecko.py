import requests
import time

# In-memory cache
coin_list_cache = None
coin_data_cache = {}

def get_token_data(symbols):
    global coin_list_cache, coin_data_cache
    result = []

    # Cache coin list
    if coin_list_cache is None:
        coins_list_url = "https://api.coingecko.com/api/v3/coins/list"
        response = requests.get(coins_list_url)
        if response.status_code != 200:
            return result
        coin_list_cache = response.json()

    for symbol in symbols:
        symbol = symbol.lower()
        # Match symbol to CoinGecko coin id
        coin_id = next((coin['id'] for coin in coin_list_cache if coin['symbol'] == symbol), None)
        if not coin_id:
            continue

        # Use cache if available
        if coin_id in coin_data_cache:
            data = coin_data_cache[coin_id]
        else:
            # Fetch coin details
            coin_data_url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
            response = requests.get(coin_data_url)
            if response.status_code != 200:
                continue
            try:
                data = response.json()
                if not isinstance(data, dict):
                    continue
                coin_data_cache[coin_id] = data  # cache it
                time.sleep(1)  # optional: avoid rate limits
            except ValueError:
                continue

        result.append({
            'symbol': symbol.upper(),
            'logo': data.get('image', {}).get('small'),
            'price': data.get('market_data', {}).get('current_price', {}).get('usd')
        })

    return result
