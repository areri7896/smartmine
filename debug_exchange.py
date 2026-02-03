import os
import django
import sys

# Setup Django environment
sys.path.append('d:\\blockchain')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from dashboard.models import Wallet, Trade
from dashboard.views import fetch_pair_conversion, get_portfolio
from django.contrib.auth import get_user_model
from decimal import Decimal
from binance.client import Client

User = get_user_model()

try:
    print("--- Starting Debug ---")
    
    # 1. Get User
    user = User.objects.first()
    print(f"User: {user}")
    
    # 2. Test Wallet Logic
    print("Testing Wallet...")
    wallet = Wallet.objects.filter(user=user).first()
    if wallet:
        print(f"Wallet Balance: {wallet.balance}")
        bal_usd = fetch_pair_conversion('KES', 'USD', float(wallet.balance))
        print(f"Balance USD: {bal_usd}")
    else:
        print("No wallet found")

    # 3. Test Trade/Portfolio Logic (Suspect this)
    print("Testing Trade/Portfolio...")
    portfolio = get_portfolio(user)
    print(f"Portfolio: {portfolio}")
    
    trades = Trade.objects.filter(user=user)
    print(f"Trades count: {trades.count()}")

    # 4. Test Binance Logic
    print("Testing Binance...")
    tokens = []
    try:
        client = Client()
        popular_symbols = ['BTCUSDT', 'ETHUSDT']
        for symbol in popular_symbols:
            ticker = client.get_ticker(symbol=symbol)
            print(f"Fetched {symbol}")
    except Exception as e:
        print(f"Binance Error (Expected if no net/api): {e}")

    print("--- Validation Successful ---")

except Exception as e:
    print("\n!!! CRITICAL ERROR !!!")
    print(e)
    import traceback
    traceback.print_exc()
