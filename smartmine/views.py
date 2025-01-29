from django.shortcuts import render
from django.contrib.auth.decorators import login_not_required
import os
import pandas as pd
from binance.client import Client
import requests
import json
import datetime
from django.http import JsonResponse

# import pandas as pd
# from dotenv import load_dotenv
# load_dotenv()
# import os

# Create your views here.

@login_not_required
def index(request): 
    api_key = os.environ['BINANCE_API_KEY']
    api_secret = os.environ['BINANCE_SECRET_KEY']
    client = Client(api_key, api_secret, testnet=False)

    # Fetch tickers from Binance API
    tickers = client.get_all_tickers()
    
    tickers = [ticker for ticker in tickers if float(ticker['price']) > 100.10]

    # Sort tickers by price (highest to lowest)
    tickers = sorted(tickers, key=lambda x: float(x['price']), reverse=True)

    # current_year = datetime.now().year
    # reference_assets = ['ETHBTC', 'LTCBTC', 'BNBETH', 'ETHUSDT', 'BTCUSDT', 'BNBUSDT', 'NEOUSDT','LTCUSDT','QTUMUSDT','XRPUSDT','BTCTUSD','ETHTUSD','ETCUSDT','BNBTUSD','XRPTUSD','BNBUSDC','BTCUSDC','ETHUSDC','XRPUSDC','EOSUSDC','XLMUSDC','USDCUSDT','ADATUSD','LINKUSDT','LINKTUSD','LINKUSDC','WAVESUSDT','LTCTUSD','LTCUSDC','TRXUSDC']
    # extracted_data = []
    # for entry in tickers:
    #     if entry['symbol'] in reference_assets:
    #         symbol = entry['symbol']
    #         price = float(entry['price'])
    #         extracted_data.append({'symbol': symbol, 'price': price})

    # Create a DataFrame for additional manipulation (if needed)
    # df = pd.DataFrame(tickers)

    # Extract and format ticker data
    # combined_tickers = [(ticker['symbol'], ticker['price']) for ticker in tickers]

    # Pass context to the template
    context = {'tickers': tickers}
    return render(request, 'src/landing/index.html', context)

def prices(request):
    api_key = os.environ['BINANCE_API_KEY']
    api_secret = os.environ['BINANCE_SECRET_KEY']
    client = Client(api_key, api_secret, testnet=False)

    # Fetch tickers from Binance API
    tickers = client.get_all_tickers()

    # Create a DataFrame for additional manipulation (if needed)
    df = pd.DataFrame(tickers)

    # Extract and format ticker data
    combined_tickers = [(ticker['symbol'], ticker['price']) for ticker in tickers]

    # Pass context to the template
    context = {'tks': combined_tickers}
    
    return render(request, 'src/landing/partials/components/_cards.html', context)
#     return render(request, 'src/landing/login.html', {})

def get_crypto_price(request, symbol):
    api_key = os.environ['BINANCE_API_KEY']
    api_secret = os.environ['BINANCE_SECRET_KEY']
    client = Client(api_key, api_secret, testnet=False)

    # Fetch tickers from Binance API
    tickers = client.get_all_tickers()
    assets = ['BTCUSDT','ETHUDT','BNBUSDT']
    extracted_data = []
    for entry in tickers:
        if entry['symbol'] in assets:
            symbol = entry['symbol']
            price= float(entry['price'])
            extracted_data.append({'symbol': symbol, 'price':price})
    response = extracted_data
    data = response.json()
    
    if "price" in data:
        return JsonResponse({"symbol": symbol, "price": data["price"]})
    else:
        return JsonResponse({"error": "Invalid symbol"}, status=400)

# def company(request):
#     return render(request, 'src/landing/company.html', {})

# def blog(request):
#     return render(request, 'src/landing/blog.html', {})