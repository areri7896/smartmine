# utils/coingecko.py
import requests

def get_token_data(symbols):
    result = []
    
    # Get all available coins from CoinGecko
    coins_list_url = "https://api.coingecko.com/api/v3/coins/list"
    coins = requests.get(coins_list_url).json()

    for symbol in symbols:
        symbol = symbol.lower()
        # Match symbol to CoinGecko coin id
        coin_id = next((coin['id'] for coin in coins if coin['symbol'] == symbol), None)
        if not coin_id:
            continue

        # Fetch coin details (logo and price)
        coin_data_url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
        response = requests.get(coin_data_url)
        if response.status_code != 200:
            continue

        data = response.json()
        result.append({
            'symbol': symbol.upper(),
            'logo': data.get('image', {}).get('small'),
            'price': data.get('market_data', {}).get('current_price', {}).get('usd')
        })

    return result
