from django.shortcuts import render
from django.contrib.auth.decorators import login_not_required
from django.views.decorators.csrf import csrf_exempt
import os
import pandas as pd
from binance.client import Client
import requests
import json
import datetime
from django.http import JsonResponse
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import Subscriber
from django.core.mail import send_mail


# import pandas as pd
# from dotenv import load_dotenv
# load_dotenv()
# import os

# Create your views here.

@login_not_required
def index(request): 
    api_key = os.environ.get('BINANCE_API_KEY')
    api_secret = os.environ.get('BINANCE_SECRET_KEY')

    if not api_key or not api_secret:
        return render(request, "index.html", {"error": "Missing Binance API credentials"})

    client = Client(api_key, api_secret, testnet=False)

    # Fetch tickers from Binance API
    tickers = client.get_all_tickers()

    # Filter tickers with price > 100.10
    tickers = [ticker for ticker in tickers if float(ticker['price']) > 0.10]

    # Define reference assets
    reference_assets = [
        'ETHBTC', 'LTCBTC', 'BNBETH', 'ETHUSDT', 'BTCUSDT', 'BNBUSDT', 'NEOUSDT',
        'LTCUSDT', 'QTUMUSDT', 'XRPUSDT', 'BTCTUSD', 'ETHTUSD', 'ETCUSDT', 'BNBTUSD',
        'XRPTUSD', 'BNBUSDC', 'BTCUSDC', 'ETHUSDC', 'XRPUSDC', 'EOSUSDC', 'XLMUSDC',
        'USDCUSDT', 'ADATUSD', 'LINKUSDT', 'LINKTUSD', 'LINKUSDC', 'WAVESUSDT',
        'LTCTUSD', 'LTCUSDC', 'TRXUSDC'
    ]

    # Extract only the relevant tickers
    extracted_data = [
        {'symbol': entry['symbol'], 'price': float(entry['price'])}
        for entry in tickers if entry['symbol'] in reference_assets
    ]

    # Sort extracted_data by price (highest to lowest)
    extracted_data = sorted(extracted_data, key=lambda x: x['price'], reverse=True)

    return render(request, 'src/landing/index.html', {"tickers": extracted_data})

    # current_year = datetime.now().year
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

# def get_crypto_price(request, symbol):
#     api_key = os.environ['BINANCE_API_KEY']
#     api_secret = os.environ['BINANCE_SECRET_KEY']
#     client = Client(api_key, api_secret, testnet=True)

#     # Fetch tickers from Binance API
#     tickers = client.get_all_tickers()
#     assets = ['BTCUSDT','ETHUDT','BNBUSDT']
#     extracted_data = []
#     for entry in tickers:
#         if entry['symbol'] in assets:
#             symbol = entry['symbol']
#             price= float(entry['price'])
#             extracted_data.append({'symbol': symbol, 'price':price})
    
@csrf_exempt
@login_not_required
def get_crypto_price(request, symbol):
    try:
        api_key = os.environ.get('BINANCE_API_KEY')
        api_secret = os.environ.get('BINANCE_SECRET_KEY')
        
        if not api_key or not api_secret:
            return JsonResponse({"error": "Missing API keys"}, status=500)

        client = Client(api_key, api_secret, testnet=True)

        # Fetch tickers from Binance API
        tickers = client.get_all_tickers()
        assets = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']  # Fixed ETHUSDT typo
        extracted_data = {entry['symbol']: float(entry['price']) for entry in tickers if entry['symbol'] in assets}

        if symbol in extracted_data:
            return JsonResponse({"symbol": symbol, "price": extracted_data[symbol]})
        else:
            return JsonResponse({"error": "Invalid symbol"}, status=400)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_not_required
def subscribe(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip()

        # Validate email
        try:
            validate_email(email)
        except ValidationError:
            return JsonResponse({"error": "Invalid email format"}, status=400)

        # Check if email already exists
        if Subscriber.objects.filter(email=email).exists():
            return JsonResponse({"error": "Email already subscribed"}, status=400)

        # Save email to database
        Subscriber.objects.create(email=email)

        # Send confirmation email
        subject = "Thank You for Subscribing! To Smartmine"
        message = f"Hello,\n\nThank you for subscribing to our updates. You'll now receive the latest news about our exchange and products.\n\nBest Regards,\nYour Company Team"
        send_mail(subject, message, "your-email@gmail.com", [email])

        return JsonResponse({"success": "Subscribed successfully!"})

    return JsonResponse({"error": "Invalid request"}, status=400)

# def company(request):
#     return render(request, 'src/landing/company.html', {})

# def blog(request):
#     return render(request, 'src/landing/blog.html', {})