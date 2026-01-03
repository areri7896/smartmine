from django.shortcuts import render, redirect,  get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from allauth.socialaccount.forms import SignupForm
from .forms import ProfileUpdateForm
from django import forms
from django.http import HttpResponse
from django.core.mail import send_mail
from django_daraja.mpesa.core import MpesaClient
from binance.exceptions import BinanceAPIException
from django.shortcuts import render
from .utils.exchange_rate import fetch_pair_conversion

from .utils.coingecko import get_token_data
from .models import Transaction
from decimal import Decimal

import os
import pandas as pd
from binance.client import Client
import requests
import json
import datetime
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from .functions import *
from django.http import JsonResponse
from .models import *
from .forms import *
from dotenv import load_dotenv
from django.utils.timezone import now

load_dotenv()

from binance.client import Client
from binance.exceptions import BinanceAPIException
from django.core.management.base import BaseCommand
# from dashboard.views import update_investment_status
from django.contrib.admin.views.decorators import staff_member_required

import requests
from django.core.cache import cache
    
from .models import Investment
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from django.shortcuts import render
from django.http import JsonResponse
from .utils.exchange_rate import fetch_pair_conversion
from .models import Wallet

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.core.cache import cache
import pandas as pd
from binance.client import Client  # Adjust if using ccxt
import os
from datetime import datetime

api_key = os.environ['BINANCE_API_KEY']
api_secret = os.environ['BINANCE_SECRET_KEY']

@login_required
@csrf_exempt  # Only use this if CSRF token isn't working properly
def hide_terms_modal(request):
    if request.method == 'POST':
        user = request.user
        user.show_terms_modal = False
        user.save()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=400)

from django.utils.timezone import now
from .models import Investment

def check_investments():
    current_time = now()
    investments = Investment.objects.filter(status="active", end_date__lte=current_time)

    for invest in investments:
        invest.status = "completed"
        invest.save()



def investment_detail(request, investment_id):
    investment = Investment.objects.get(id=investment_id, user=request.user)
    investment.check_and_update_status()  # Check on access
    return render(request, 'investment_detail.html', {'investment': investment})

def investment_plans(request):
    if not request.user.is_authenticated:
        return redirect('login')
    plans = InvestmentPlan.objects.all()
    investments = Investment.objects.filter(user=request.user).select_related("plan")

    # print("Investments being passed to template:", investments)

    context = {
        'investments': investments,
        'plans': plans
    }
    return render(request, 'src/dashboard/market.html', context)



# def invest(request, plan_id):
#     # Retrieve the investment plan or raise 404 if not found
#     plan = get_object_or_404(InvestmentPlan, id=plan_id)
    
#     # Get the user's wallet
#     wallet = Wallet.objects.filter(user=request.user).first()
    
#     # Check if user has a wallet
#     if not wallet:
#         messages.error(request, 'No wallet found. Please create a wallet first.')
#         return redirect('wallet')
    
#     # Check if wallet balance is sufficient
#     if wallet.balance < plan.price:
#         messages.error(request, 'Your balance is insufficient. Please deposit funds!')
#         return redirect('wallet')
    
#     # Handle POST request to create investment
#     if request.method == 'POST':
#         try:
#             with transaction.atomic():
#                 # Create investment
#                 end_date = datetime.now() + timedelta(days=plan.cycle_days)
#                 investment = Investment.objects.create(
#                     user=request.user,
#                     plan=plan,
#                     end_date=end_date,
#                     status="active"
#                 )
                
#                 # Deduct plan price from wallet balance
#                 wallet.balance -= plan.price
#                 wallet.save()
                
#                 messages.success(request, 'Investment in {plan.name} created successfully!')
#                 return redirect('market/')
#         except Exception as e:
#             messages.error(request, 'An error occurred while processing your investment. Please try again.')
#             return redirect('wallet')
    
#     # Render the template for GET request
#     return render(request, 'src/dashboard/market.html', {'pl': plan})

# client = get_binance_client()
# if client:
#     # safe to use client
#     try:
#         balance = client.get_account()

#         # checking server status
#         client.ping()  # returns {} on success

#         res = client.get_server_time()
#         ts = res['serverTime'] / 1000
#         print(f"Binance server time (timestamp): {ts}")

#     except Exception as e:
#         print("Error while using Binance client:", e)
# else:
#     print("Failed to connect to Binance.")



#https://www.youtube.com/redirect?event=video_description&redir_token=QUFFLUhqbTR2cHBLOV9rN0lvTUJNVWJRMGE5bWd6RzBuQXxBQ3Jtc0tuTW85WUdYcVdXMEdNdXVwczZzeUthbEhRWUpRX3AzRnI3eWNBZUdONDdvYURfOFZyMVVuNlh6Y0VSNlpYWi13LUQzemxTaWJ5dlpyNHMwWkRndUVqcy0tVkRFZzNXYkx3aXR0WWlEb1U3NGZLRTJtVQ&q=https%3A%2F%2Fgithub.com%2Fsevenisalie%2Fdjango_alpha_vantage&v=3OOD9bFdBOQ


# Initialize Binance client
def get_binance_client():
    api_key = os.environ.get('BINANCE_API_KEY')
    api_secret = os.environ.get('BINANCE_SECRET_KEY')
    if not api_key or not api_secret:
        print("Binance API key or secret not set.")
        return None
    try:
        client = Client(api_key, api_secret, testnet=False)
        client.API_URL = 'https://api.binance.com'
        client.ping()
        server_time = client.get_server_time()
        client.time_offset = server_time['serverTime'] - int(time.time() * 1000)
        return client
    except BinanceAPIException as e:
        print(f"Binance API error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error in get_binance_client: {e}")
        return None

@csrf_exempt
def get_ticker_data(request):
    client = get_binance_client()
    if not client:
        return JsonResponse({"error": "Failed to connect to Binance API"}, status=503)

    try:
        # Check cache first
        cache_key = 'all_tickers'
        tickers = cache.get(cache_key)
        if not tickers:
            tickers = client.get_all_tickers()
            cache.set(cache_key, tickers, 300)  # Cache for 5 minutes

        # Process tickers into DataFrame
        df = pd.DataFrame(tickers)
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
        # Ensure symbol remains a string
        df['symbol'] = df['symbol'].astype(str)
        # Filter out rows with invalid prices
        df = df.dropna(subset=['price'])
        
        return JsonResponse(df.to_dict(orient='records'), safe=False)
    except BinanceAPIException as e:
        return JsonResponse({"error": f"Binance API error: {str(e)}"}, status=500)
    except Exception as e:
        return JsonResponse({"error": f"Unexpected error: {str(e)}"}, status=500)



# from django.shortcuts import render
# from .models import Wallet
# import requests

# def convert_kes_to_usd(amount_kes):
#     """
#     Converts the given amount in Kenyan Shillings (KES) to US Dollars (USD)
#     using the Frankfurter API.
#     """
#     try:
#         url = "https://api.frankfurter.app/latest"
#         params = {"amount": amount_kes, "from": "KES", "to": "USD"}
#         response = requests.get(url, params=params)
#         response.raise_for_status()
#         data = response.json()
#         usd_amount = data["rates"]["USD"]
#         return usd_amount
#     except Exception as e:
#         print(f"Currency conversion error: {e}")
#         return None

# def wallet_view(request):
#     # Assuming the user is authenticated
#     wallet = Wallet.objects.get(user=request.user)
#     balance_kes = wallet.balance
#     balance_usd = fetch_exchange_rates(base_currency='KES',target_currency='USD',float(balance_kes)) 

#     context = {
#         'balance_kes': balance_kes,
#         'balance_usd': balance_usd if balance_usd is not None else "Conversion unavailable",
#     }
#     return render(request, 'src/dashboard/wallet.html', context)

def wallet_view(request):
    """
    Display user's wallet balance in KES and converted USD.
    
    Args:
        request: HTTP request object
    
    Returns:
        Rendered template with wallet balance in KES and USD
    """
    # Assuming the user is authenticated
    try:
        wallet = Wallet.objects.get(user=request.user)
        balance_kes = wallet.balance
        
        # Convert KES balance to USD
        conversion_data = fetch_pair_conversion(
            base_currency='KES',
            target_currency='USD',
            amount=float(balance_kes)
        )
        balance_usd = conversion_data['converted_amount']
        
        context = {
            'balance_kes': balance_kes,
            'balance_usd': round(balance_usd, 2),  # Round to 2 decimal places for display
            'last_update': conversion_data['last_update']
        }
    except Wallet.DoesNotExist:
        context = {
            'balance_kes': 0,
            'balance_usd': 'Wallet not found',
            'last_update': None
        }
    except Exception as e:
        context = {
            'balance_kes': balance_kes if 'balance_kes' in locals() else 0,
            'balance_usd': 'Conversion unavailable',
            'last_update': None,
            'error': str(e)
        }
    
    return render(request, 'src/dashboard/wallet.html', context)

# def crypto_assets_view(request):
#     tickers = ['btc', 'eth', 'bnb', 'ada', 'doge']
#     tokens = get_token_data(tickers)
#     return render(request, 'your_template.html', {'tokens': tokens})

# views.py
def active_investments(request):
    investments = Investment.objects.filter(user=request.user, is_active=True)
    for inv in investments:
        inv.process_completion()  # ensures expired investments are updated
    return render(request, 'src/dashboard/market.html', {'investments': investments})

def completed_investments(request):
    investments = Investment.objects.filter(user=request.user, is_completed=True)
    return render(request, 'src/dashboard/market.html', {'investments': investments})


@login_required
def dashboard(request):
    wallet_bal = Wallet.objects.filter(user=request.user).first()
    wallet_bal_usd = 0
    if wallet_bal:
        wallet_bal = wallet_bal.balance
        wallet_bal_usd = fetch_pair_conversion('KES', 'USD', float(wallet_bal))
    else:
        wallet_bal = 0

        # print(wallet_bal_usd)
 
    api_key = os.environ['BINANCE_API_KEY']
    api_secret = os.environ['BINANCE_SECRET_KEY']
    client = Client(api_key, api_secret, testnet=False)
    tickers = client.get_all_tickers()
    df = pd.DataFrame(tickers)
    df.head()

    tics = ['btc', 'eth', 'bnb', 'ada', 'doge']
    tokens = get_token_data(tics)
    # tick_symbol = [ticker['symbol'] for ticker in tickers]
    # tick_price = [ticker['price'] for ticker in tickers]
    combined_tickers = [(ticker['symbol'], ticker['price']) for ticker in tickers]
    context = {'tks': combined_tickers, 'df':df, 'tickers': tickers, 'tokens': tokens,'bal': wallet_bal,
            'bal_usd': wallet_bal_usd,}

    # context = {'tick_symbol':tick_symbol, 'tick_price':tick_price}
    return render(request, 'src/dashboard/dashboard.html', context)


def account(request):
    client = get_binance_client()
    if not client:
        return HttpResponse("Failed to connect to Binance", status=503)

    try:
        info = client.get_account()
        return JsonResponse(info)
    except Exception as e:
        return HttpResponse(f"Error: {e}", status=500)


def asset_balance(request):
    client = get_binance_client()
    if not client:
        return HttpResponse("Failed to connect to Binance", status=503)

    try:
        asset_balance = client.get_asset_balance(asset='USDT')  # Replace 'USDT' as needed
        asset_details = client.get_asset_details()
        context = {'asset_balance': asset_balance, 'asset_details': asset_details}
        return render(request, 'src/dashboard/wallet.html', context)
    except Exception as e:
        return HttpResponse(f"Error: {e}", status=500)


def withdraw(request):
    if request.method == 'POST':
        try:
            phone_number = request.POST.get('wphone')
            amount = int(request.POST.get('wamount'))
            user = request.user
            # print(amount, phone_number, user)

            # Save withdrawal request to the Withdrawal model
            Withdrawal.objects.create(
                user=user,
                amount=amount,
                phone_number=phone_number,
                status='Pending'
            )
            # Email the received data to ssmartmine@gmail.com
            subject = f"New Withdrawal Request for customer "
            message = f"Mpesa Transaction Code: {phone_number}\nAmount: {amount}\nUser: f'{user.first_name} + {user.last_name}'"
            send_mail(
                subject,
                message,
                'noreply@ssmartmine.com',
                ['ssmartmine@gmail.com'],
                fail_silently=False,
            )
            messages.success(request, 'Thank you. Your withdrawal request was Successfully sent. Please the request will be completed in less than 10 minutes.!')
            return redirect('wallet')  # or some other valid view name
        except Exception as e:
            # print(f"An error occurred: {e}")
            messages.error(request, 'An error occurred during sharing your with your withdrwal request!!')
            return redirect('wallet')
    else:
        return redirect('wallet')  # or redirect somewhere
            # return JsonResponse({'error': str(e)}, status=400)

from django.contrib import admin

@admin.action(description="Approve selected withdrawals")
def approve_selected_withdrawals(modeladmin, request, queryset):
    queryset.update(status='Approved', is_cancelled=False)
    messages.success(request, f"{queryset.count()} withdrawals approved successfully.")

# class WithdrawalAdmin(admin.ModelAdmin):
#     list_display = ('user', 'phone_number', 'amount', 'status', 'is_cancelled')
#     actions = [approve_selected_withdrawals]

# admin.site.register(Withdrawal, WithdrawalAdmin)


def verif(request):
    if request.method == 'POST':
        try:
            phone_number = request.POST.get('transaction')
            amount = int(request.POST.get('amnt'))
            user = request.user

            # Save verification request to the Verification model
            Depo_Verification.objects.create(
                user=user,
                amount=amount,
                verification_code=phone_number,
                is_completed=0
            )


            subject = f"New Verification Request for user "
            message = f"Mpesa Transaction Code: {phone_number}\nAmount: {amount}\nUser: {user.username} \n Please take a moment and update the record"
            send_mail(
                subject,
                message,
                'noreply@ssmartmine.com',
                ['ssmartmine@gmail.com'],
                fail_silently=False,
            )
            messages.success(request, 'Thank you. Transaction code was sent for verification Successfully!')
            print(list(messages.get_messages(request)))
            return redirect('wallet')  # or some other valid view name
        except Exception as e:
            print(f"An error occurred: {e}")
            messages.error(request, 'An error occurred during sharing your Transaction code!!')
            return redirect('wallet')
    else:
        # Optionally handle non-POST requests
        return redirect('wallet')  # or redirect somewhere
            # return JsonResponse({'error': str(e)}, status=400)

            
# def wallet(request):
#     try:
#         # Fetch Binance API keys from environment variables
#         api_key = os.environ.get('BINANCE_API_KEY')
#         api_secret = os.environ.get('BINANCE_SECRET_KEY')
        
#         if not api_key or not api_secret:
#             raise ValueError("Binance API key or secret not found in environment variables.")

#         # Initialize Binance client
#         client = Client(api_key, api_secret)

#         # Synchronize time with Binance server
#         server_time = client.get_server_time()
#         time_offset = server_time['serverTime'] - int(time.time() * 1000)
#         client.time_offset = time_offset

#         # Test the connection
#         client.ping()

#         # Fetch account information
#         account_info = client.get_account()
#         balances = account_info['balances']

#         # Define reference assets and extract relevant data
#         reference_assets = ['BTC', 'ETH', 'XRP', 'USDT']
#         extracted_data = []
#         total_balance = 0
#         total_balance_usd = 0

#         for entry in balances:
#             asset = entry['asset']
#             free = float(entry['free'])
#             locked = float(entry['locked'])

#             if asset in reference_assets:
#                 extracted_data.append({'asset': asset, 'free': free, 'locked': locked})

#             if free > 0:
#                 try:
#                     symbol = f"{asset}USDT"
#                     avg_price_info = client.get_avg_price(symbol=symbol)
#                     price = float(avg_price_info['price'])
#                     total_balance += free * price
#                 except BinanceAPIException as e:
#                     print(f"Error fetching price for {symbol}: {e}")

#         # Convert total balance to USD if applicable
#         if total_balance > 0:
#             total_balance_usd = fetch_pair_conversion('KES', 'USD', float(total_balance))
        
#         # Fetch wallet balance
#         wallet_bal = Wallet.objects.filter(user=request.user).first()
#         wallet_bal_usd = 0
#         if wallet_bal:
#             wallet_bal = wallet_bal.balance
#             wallet_bal_usd = fetch_pair_conversion('KES', 'USD', float(wallet_bal))
#         else:
#             wallet_bal = 0

#         # print(wallet_bal_usd)


#         # Fetch withdrawal and deposit history
#         withdrawals = Withdrawal.objects.filter(user=request.user).order_by('-id')
#         depos = Depo_Verification.objects.filter(user=request.user).order_by('-id')
        
#         # Prepare context for rendering the template
#         context = {
#             'total_balance': total_balance,
#             'total_balance_usd': total_balance_usd,
#             'extracted_data': extracted_data,
#             'bal': wallet_bal,
#             'bal_usd': wallet_bal_usd,
#             'withdrawals': withdrawals,
#             'depos': depos,
#         }

#         # Handle POST request for M-Pesa STK Push
#         if request.method == 'POST':
#             try:
#                 # Try retrieving data from request body (in case of JSON)
#                 try:
#                     data = json.loads(request.body.decode('utf-8'))
#                     phone_number = data.get('phone')
#                     amount = int(data.get('amount'))
#                 except json.JSONDecodeError:
#                     # Fallback to form data (if request is not JSON)
#                     phone_number = request.POST.get('phone')
#                     amount = int(request.POST.get('amount'))

#                 # Format phone number if it starts with "0"
#                 if phone_number.startswith("0"):
#                     phone_number = "254" + phone_number[1:]

#                 # Create deposit transaction
#                 DepositTransaction.objects.create(
#                     user=request.user,
#                     amount=amount,
#                     phone_number=phone_number,
#                     transaction_id=f"TXN{int(time.time())}",
#                     status='Pending'
#                 )

#                 # Initialize M-Pesa client and initiate STK Push
#                 cl = MpesaClient()
#                 account_reference = 'reference'
#                 transaction_desc = 'Description'
#                 callback_url = 'https://www.smrtmine.com/dashboard/api/mpesa/callback/'
#                 response = cl.stk_push(phone_number, amount, account_reference, transaction_desc, callback_url)

#                 # Decode response data
#                 response_data = json.loads(response.text)
#                 result_code = response_data.get('ResultCode', '')

#                 # Handle different response scenarios
#                 if result_code == '0':
#                     messages.success(request, "Transaction successful ✅")
#                 elif result_code == '1032':
#                     messages.error(request, "Transaction canceled by user ❌")
#                 elif result_code == '1037':
#                     messages.error(request, "STK Push timed out ⏳")
#                 else:
#                     messages.error(request, f"Unknown response: {response_data.get('ResultDesc', 'No description')}")

#                 # Save the response to the database
#                 MpesaResponse.objects.create(
#                     merchant_request_id=response_data.get('MerchantRequestID'),
#                     checkout_request_id=response_data.get('CheckoutRequestID'),
#                     response_code=response_data.get('ResponseCode'),
#                     response_description=response_data.get('ResponseDescription'),
#                     customer_message=response_data.get('CustomerMessage')
#                 )

#                 # Return JSON response based on STK Push result
#                 if response.status_code == 200:
#                     messages.success(request, 'Your deposit was initiated successfully! Please check your phone and enter your pin to complete the transaction.')
#                     return redirect('wallet')
#                 else:
#                     messages.error(request, f"M-Pesa STK Push failed: {response.text}")
#                     return JsonResponse({
#                         'error': f"M-Pesa STK Push failed: {response.text}"
#                     }, status=400)

#             except Exception as e:
#                 print(f"An error occurred during STK Push: {e}")
#                 messages.error(request, 'There was an error in your deposit!')
#                 return JsonResponse({'error': str(e)}, status=400)

#         # Render the wallet page
#         return render(request, 'src/dashboard/wallet.html', context)

#     except BinanceAPIException as e:
#         print(f"Binance API Error: {e}")
#         messages.error(request, f"Binance API Error: {e}")
#         return redirect('wallet')
#     except Exception as e:
#         print(f"An error occurred: {e}")
#         messages.error(request, f"An error occurred: {e}")
#         return redirect('wallet')
    

def wallet(request):
    try:
        # Fetch Binance API keys from environment variables
        # api_key = os.environ.get('BINANCE_API_KEY')
        # api_secret = os.environ.get('BINANCE_SECRET_KEY')
        
        # if not api_key or not api_secret:
        #     raise ValueError("Binance API key or secret not found in environment variables.")

        # # Initialize Binance client
        # client = Client(api_key, api_secret)

        # # Synchronize time with Binance server
        # server_time = client.get_server_time()
        # time_offset = server_time['serverTime'] - int(time.time() * 1000)
        # client.time_offset = time_offset

        # # Test the connection
        # client.ping()

        # # Fetch account information
        # account_info = client.get_account()
        # balances = account_info['balances']

        # # Define reference assets and extract relevant data with icon mapping
        # reference_assets = ['BTC', 'ETH', 'XRP', 'USDT']
        # asset_icons = {
        #     'BTC': 'static/assets/media/images/crypto-coins-1.png',
        #     'ETH': 'static/assets/media/images/crypto-coins-2.png',
        #     'XRP': 'static/assets/media/images/crypto-coins-3.png',
        #     'USDT': 'static/assets/media/images/crypto-coins-4.png'
        # }
        # extracted_data = []
        total_balance = 0
        total_balance_usd = 0

        # for entry in balances:
        #     asset = entry['asset']
        #     free = float(entry['free'])
        #     locked = float(entry['locked'])

        #     if asset in reference_assets:
        #         extracted_data.append({
        #             'asset': asset,
        #             'free': free,
        #             'locked': locked,
        #             'icon': asset_icons.get(asset, 'default.svg')
        #         })

        #     if free > 0:
        #         try:
        #             symbol = f"{asset}USDT"
        #             avg_price_info = client.get_avg_price(symbol=symbol)
        #             price = float(avg_price_info['price'])
        #             total_balance += free * price
        #         except BinanceAPIException as e:
        #             print(f"Error fetching price for {symbol}: {e}")

        # Convert total balance to USD if applicable
        if total_balance > 0:
            total_balance_usd = fetch_pair_conversion('KES', 'USD', float(total_balance))
        
        # Fetch wallet balance
        wallet_bal = Wallet.objects.filter(user=request.user).first()
        wallet_bal_usd = 0
        if wallet_bal:
            wallet_bal = wallet_bal.balance
            wallet_bal_usd = fetch_pair_conversion('KES', 'USD', float(wallet_bal))
        else:
            wallet_bal = 0

        # Fetch withdrawal and deposit history
        withdrawals = Withdrawal.objects.filter(user=request.user).order_by('-id')
        depos = Depo_Verification.objects.filter(user=request.user).order_by('-id')
        
        # Prepare context for rendering the template
        context = {
            'total_balance': total_balance,
            'total_balance_usd': total_balance_usd,
            # 'extracted_data': extracted_data,
            'bal': wallet_bal,
            'bal_usd': wallet_bal_usd,
            'withdrawals': withdrawals,
            'depos': depos,
        }

        # Handle POST request for M-Pesa STK Push
        if request.method == 'POST':
            try:
                # Try retrieving data from request body (in case of JSON)
                try:
                    data = json.loads(request.body.decode('utf-8'))
                    phone_number = data.get('phone')
                    amount = int(data.get('amount'))
                except json.JSONDecodeError:
                    # Fallback to form data (if request is not JSON)
                    phone_number = request.POST.get('phone')
                    amount = int(request.POST.get('amount'))

                # Format phone number if it starts with "0"
                if phone_number.startswith("0"):
                    phone_number = "254" + phone_number[1:]

                # Create deposit transaction
                DepositTransaction.objects.create(
                    user=request.user,
                    amount=amount,
                    phone_number=phone_number,
                    transaction_id=f"TXN{int(time.time())}",
                    status='Pending'
                )

                # Initialize M-Pesa client and initiate STK Push
                cl = MpesaClient()
                account_reference = 'reference'
                transaction_desc = 'Description'
                callback_url = 'https://www.smrtmine.com/dashboard/api/mpesa/callback/'
                response = cl.stk_push(phone_number, amount, account_reference, transaction_desc, callback_url)

                # Decode response data
                response_data = json.loads(response.text)
                result_code = response_data.get('ResultCode', '')

                # Handle different response scenarios
                if result_code == '0':
                    messages.success(request, "Transaction successful ✅")
                elif result_code == '1032':
                    messages.error(request, "Transaction canceled by user ❌")
                elif result_code == '1037':
                    messages.error(request, "STK Push timed out ⏳")
                else:
                    messages.error(request, f"Unknown response: {response_data.get('ResultDesc', 'No description')}")

                # Save the response to the database
                MpesaResponse.objects.create(
                    merchant_request_id=response_data.get('MerchantRequestID'),
                    checkout_request_id=response_data.get('CheckoutRequestID'),
                    response_code=response_data.get('ResponseCode'),
                    response_description=response_data.get('ResponseDescription'),
                    customer_message=response_data.get('CustomerMessage')
                )

                # Return JSON response based on STK Push result
                if response.status_code == 200:
                    messages.success(request, 'Your deposit was initiated successfully! Please check your phone and enter your pin to complete the transaction.')
                    return redirect('wallet')
                else:
                    messages.error(request, f"M-Pesa STK Push failed: {response.text}")
                    return JsonResponse({
                        'error': f"M-Pesa STK Push failed: {response.text}"
                    }, status=400)

            except Exception as e:
                print(f"An error occurred during STK Push: {e}")
                messages.error(request, 'There was an error in your deposit!')
                return JsonResponse({'error': str(e)}, status=400)

        # Render the wallet page
        return render(request, 'src/dashboard/wallet.html', context)

    except BinanceAPIException as e:
        print(f"Binance API Error: {e}")
        messages.error(request, f"Binance API Error: {e}")
        return redirect('wallet')
    except Exception as e:
        print(f"An error occurred: {e}")
        messages.error(request, f"An error occurred: {e}")
        return redirect('wallet')
    

@csrf_exempt
def mpesa_callback(request):
    """
    Validate M-Pesa payment and update wallet balance.
    """
    try:
        # Parse the incoming JSON data
        data = json.loads(request.body.decode('utf-8'))
        
        # Extract transaction details from the callback
        body = data.get('Body', {}).get('stkCallback', {})
        result_code = body.get('ResultCode')
        metadata = body.get('CallbackMetadata', {}).get('Item', [])
        transaction_id = None
        amount = None
        phone_number = None

        # Extract metadata fields
        for item in metadata:
            if item['Name'] == 'MpesaReceiptNumber':
                transaction_id = item['Value']
            elif item['Name'] == 'Amount':
                amount = float(item['Value'])
            elif item['Name'] == 'PhoneNumber':
                phone_number = str(item['Value'])

        # Check if the transaction was successful
        if result_code == 0:  # Successful transaction
            try:
                # Retrieve the pending transaction
                transaction = DepositTransaction.objects.get(
                    phone_number=phone_number, 
                    transaction_id = transaction_id,
                    status='Pending'
                )
                # Update the transaction details
                transaction.transaction_id = transaction_id
                transaction.status = 'Completed'
                transaction.save()

                # Update the wallet balance
                wallet, _ = Wallet.objects.get_or_create(user=transaction.user)
                wallet.balance += amount
                wallet.save()

                # Return success response
                return JsonResponse({'success': True, 'message': 'Deposit validated successfully.'}, status=200)
            except DepositTransaction.DoesNotExist:
                # Handle case where the transaction is not found
                return JsonResponse({'error': 'Transaction not found.'}, status=404)
        else:
            # Handle failed transaction
            return JsonResponse({'error': 'M-Pesa transaction failed.'}, status=400)

    except json.JSONDecodeError:
        # Handle JSON parsing errors
        return JsonResponse({'error': 'Invalid JSON data received.'}, status=400)
    except Exception as e:
        # Handle any other exceptions
        return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)


# def exchange(request):
#     api_key = os.environ['BINANCE_API_KEY']
#     api_secret = os.environ['BINANCE_SECRET_KEY']
#     client = Client(api_key, api_secret, testnet=False)
#     tickers = client.get_all_tickers()
#     df = pd.DataFrame(tickers)
#     df.head()

#     tics = ['btc', 'eth', 'bnb', 'ada', 'doge']
#     tokens = get_token_data(tics)
#     combined_tickers = [(ticker['symbol'], ticker['price']) for ticker in tickers]
#     context = {'tks': combined_tickers, 'df':df, 'tickers': tickers}

#     return render(request, 'src/dashboard/exchange.html', context)


def mkt_data(request):
    market_depth = client.get_order_book(symbol = 'BTCBUSD')
    bids = pd.DataFrame(market_depth['bids'])
    bids.column = ['price', 'bids']
    asks = pd.DataFrame(market_depth['asks'])
    asks.columns =['price', 'asks']
    df = pd.concat([bids,asks]).fillna(0)
    context ={'df':df}
    return render(request, 'src/dashboard/exchange.html', context )

def recent_trades(request):
    recent_trade= client.get_recent_trades(symbol='BTCBUSD')
    df = pd.DataFrame(recent_trade)
    df.head()
    context = {'trades': recent_trade}
    print('recent trade: ', context)
    # return render(request, ,context)

import requests
from django.shortcuts import render

def fetch_crypto_data():
    # Base URLs for APIs
    binance_url = "https://api.binance.com/api/v3/ticker/24hr"
    coingecko_url = "https://api.coingecko.com/api/v3/simple/price"
    
    # List of assets and their symbols
    assets = ["BTC", "ETH", "BNB", "XRP", "USDT"]
    asset_details = {
        "BTC": "Bitcoin",
        "ETH": "Ethereum",
        "BNB": "Binance Coin",
        "XRP": "XRP",
        "USDT": "Tether"
    }
    
    # Data structure for holding the response
    crypto_data = []

    # Query Binance data
    try:
        binance_response = requests.get(binance_url)
        if binance_response.status_code == 200:
            binance_data = binance_response.json()
            for item in binance_data:
                if item["symbol"][:-4] in assets:  # Match asset
                    crypto_data.append({
                        "symbol": item["symbol"][:-4],
                        "name": asset_details[item["symbol"][:-4]],
                        "on_orders": f"USD {float(item['askPrice']):,.2f}",
                        "available_balance": f"USD {float(item['bidPrice']):,.2f}",
                        "total_balance": f"USD {float(item['askPrice']) + float(item['bidPrice']):,.2f}",
                        "market_change": f"{item['priceChangePercent']}%"
                    })
    except Exception as e:
        print(f"Error fetching Binance data: {e}")

    # Query CoinGecko data
    try:
        symbols = ",".join([asset.lower() for asset in assets])
        coingecko_params = {"ids": symbols, "vs_currencies": "usd"}
        coingecko_response = requests.get(coingecko_url, params=coingecko_params)
        if coingecko_response.status_code == 200:
            gecko_data = coingecko_response.json()
            for asset in assets:
                if asset.lower() in gecko_data:
                    crypto_data.append({
                        "symbol": asset,
                        "name": asset_details[asset],
                        "on_orders": "N/A",  # Example default value
                        "available_balance": f"USD {gecko_data[asset.lower()]['usd']:.2f}",
                        "total_balance": f"USD {gecko_data[asset.lower()]['usd']:.2f}",
                        "market_change": "N/A"  # Example default value
                    })
    except Exception as e:
        print(f"Error fetching CoinGecko data: {e}")

    return crypto_data

def crypto_view(request):
    data = fetch_crypto_data()
    print(data)
    return render(request, 'src/dashboard/wallet.html', {'crypto_data': data})

# @login_required
# def confirm_investment(request, plan_id):

#     plan = get_object_or_404(InvestmentPlan, id=plan_id)
#     wallet = Wallet.objects.filter(user=request.user).first()

#     if not wallet:
#         messages.error(request, 'Wallet not found. Please create a wallet first.')
#         return redirect('wallet')

#     if request.method == 'POST':
#         try:
#             # Check if the user has sufficient balance
#             if wallet.balance <= plan.price:
#                 messages.error(request, 'Insufficient balance. Please deposit funds to proceed.')
#                 return redirect('wallet')

#             # Calculate investment start and end date
#             start_date = now()
#             db_end_date = start_date + timedelta(days=plan.cycle_days)

#             # Create investment record
#             investment = Investment.objects.create(
#                 user=request.user,
#                 plan=plan,
#                 start_date=start_date,
#                 db_end_date=db_end_date,
#                 status="active"
#             )

#             # Deduct plan price from wallet balance
#             wallet.balance -= plan.price
#             wallet.save()

#             messages.success(request, 'Your investment was successful!')
#             return redirect('market')

#         except Exception as e:
#             print(f"Error during investment confirmation: {e}")  # Log the exception
#             messages.error(request, 'OOPS!! There was an error, Please try again!')
#             return redirect('market')
#     messages.error(request, 'OOPS!! There was an error, Please try again!')
#     return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)


def process_investments():
    current_time = now()
    investments = Investment.objects.filter(status="completed", end_date__lte=current_time)

    for inv in investments:

        # Payout only capital (profit already paid daily)
        capital = inv.plan.price

        wallet = Wallet.objects.filter(user=inv.user).first()
        if wallet:
            wallet.balance += capital
            wallet.save()

        inv.total_payout = capital + inv.profit_amount
        inv.status = "paid"
        inv.save()

        # Send email
        send_mail(
            subject="Your Investment Has Matured!",
            message=f"Your investment in {inv.plan.name} has been fully paid out.\n"
                    f"Total earned: {inv.profit_amount}.",
            from_email="info@smrtmine.com",
            recipient_list=[inv.user.email],
            fail_silently=True,
        )

def update_investment_status():
    investments = Investment.objects.filter(status="active", end_date__lte=now())
    for investment in investments:
        investment.status = "completed"
        investment.save()


class Command(BaseCommand):
    help = 'Update the status of expired investments'

    def handle(self, *args, **kwargs):
        update_investment_status()
        self.stdout.write(self.style.SUCCESS('Successfully updated investment statuses.'))

def avg_price(request):
    avg_price = client.get_avg_price()
    return avg_price

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from datetime import datetime, timedelta
from django.utils.timezone import now
from .models import InvestmentPlan, Investment, Wallet

@login_required
def market(request):
    """Display all investment plans for the user to pick."""
    plans = InvestmentPlan.objects.all()
    investments = Investment.objects.filter(user=request.user).select_related("plan")
    return render(request, 'src/dashboard/market.html', {'plans': plans, 'investments': investments})
@login_required
def confirm_investment(request, plan_id):
    """Show confirmation page and process investment on confirmation."""
    plan = get_object_or_404(InvestmentPlan, id=plan_id)
    wallet = Wallet.objects.filter(user=request.user).first()

    if not wallet:
        messages.error(request, 'Wallet not found. Please create a wallet first.')
        return redirect('wallet')

    if wallet.balance < plan.price:
        messages.error(request, 'Insufficient balance. Please deposit funds to proceed.')
        return redirect('wallet')

    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Create investment
                start_date = now()
                end_date = start_date + timedelta(days=plan.cycle_days)
                investment = Investment.objects.create(
                    user=request.user,
                    plan=plan,
                    db_start_date=start_date,
                    db_end_date=end_date,
                    status="active"
                )
                investment.save()

                # Deduct plan price from wallet balance
                wallet.balance -= plan.price
                wallet.save()

                messages.success(request, f'Investment in {plan.name} created successfully!')
                return redirect('market')
        except Exception as e:
            messages.error(request, 'An error occurred while processing your investment. Please try again.')
            return redirect('wallet')

    # Render confirmation template for GET request
    return render(request, 'src/dashboard/confirm_investment.html', {
        'plan': plan,
        'wallet': wallet
    })
@login_required
def invest(request, plan_id):
    """Process the investment after confirmation."""
    plan = get_object_or_404(InvestmentPlan, id=plan_id)

    if request.method != 'POST':
        # Redirect if someone tries to access directly
        return redirect('confirm_investment', plan_id=plan_id)

    try:
        with transaction.atomic():

            # Lock the wallet row to prevent race conditions (double spending)
            wallet = Wallet.objects.select_for_update().filter(user=request.user).first()

            if not wallet:
                messages.error(request, 'No wallet found. Please create a wallet first.')
                return redirect('wallet')

            # Balance check INSIDE the atomic block (safest)
            if wallet.balance < plan.price:
                messages.error(request, 'Your balance is insufficient. Please deposit funds!')
                return redirect('wallet')

            # Create investment
            start_date = now()
            end_date = start_date + timedelta(days=plan.cycle_days)

            Investment.objects.create(
                user=request.user,
                plan=plan,
                db_start_date=start_date,
                end_date=end_date,
                status="active",
                total_days=plan.cycle_days
            )

            # Deduct plan price
            wallet.balance -= plan.price
            wallet.save()

            messages.success(request, f'Investment in {plan.name} created successfully!')
            return redirect('market')

    except Exception as e:
        messages.error(request, 'An error occurred while processing your investment. Please try again.')
        return redirect('wallet')

# @login_required
# def market(request):
#     plans = InvestmentPlan.objects.all()
#     investments = Investment.objects.filter(user=request.user).select_related("plan")
#     return render(request, 'src/dashboard/market.html', {'plans': plans, 'investments':investments})
    # api_key = os.environ['BINANCE_API_KEY']
    # api_secret = os.environ['BINANCE_SECRET_KEY']
    # client = Client(api_key, api_secret, testnet=True)
    # tickers = client.get_all_tickers()
    # df = pd.DataFrame(tickers)
    # # df.head()
    # context = {'tickers':tickers, 'df':df}

    # return render(request, 'src/dashboard/market.html', context)
'''
def profile(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST or None, request.FILES or None, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated!")
        else:
            messages.error(request, "Error updating profile.")
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, 'src/dashboard/profile.html', {'user_form': form})
'''
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CustomUserChangeForm, ProfileUpdateForm
from .models import Profile
from django.contrib.auth.decorators import login_required

@login_required
def profile(request):
    # Get the Profile instance for the logged-in user
    user_instance = request.user
    profile_instance = Profile.objects.get(user=request.user)
    
    if request.method == 'POST':
        user_form = CustomUserChangeForm(request.POST, instance=user_instance)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile_instance)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Congratulations! Your profile was updated successfully.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        user_form = CustomUserChangeForm(instance=user_instance)
        profile_form = ProfileUpdateForm(instance=profile_instance)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'src/dashboard/profile.html', context)
# @login_required
# def profile(request):
#     user_instance = request.user
#     profile_instance = request.user.profile

#     user_form = CustomUserChangeForm(request.POST or None, instance=user_instance)
#     user_form = ProfileUpdateForm(request.POST or None, request.FILES or None, instance=profile_instance)

#     if request.method == 'POST':
#         if user_form.is_valid():# '''and profile_form.is_valid()''':
#             user_form.save()
#             # profile_form.save()
#             messages.success(request, 'Your profile was updated successfully!')
#             return redirect('dashboard')
#         else:
#             print("Errors:", user_form.errors, '''profile_form.errors''')

#     context = {
#         'user_form': user_form,
#         # 'profile_form': profile_form,
#     }
#     return render(request, 'src/dashboard/profile.html', context)


@login_required
def exchanges(request):
    try:
        # Initialize Binance client (use environment variables for security)
        client = Client(os.getenv('BINANCE_API_KEY'), os.getenv('BINANCE_API_SECRET'))

        # Fetch ticker data (24hr ticker for all symbols)
        cache_key = 'tickers'
        tickers = cache.get(cache_key)
        if not tickers:
            tickers = client.get_ticker()
            cache.set(cache_key, tickers, 300)  # Cache for 5 minutes

        # Convert tickers to DataFrame and select relevant fields
        df = pd.DataFrame(tickers)
        df = df[['symbol', 'priceChangePercent', 'lastPrice', 'lowPrice', 'highPrice', 'openPrice', 'closePrice']]
        
        # Convert to list of dictionaries for template
        tickers_list = df.to_dict('records')

        # Pagination
        paginator = Paginator(tickers_list, 10)  # Show 10 tickers per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Fetch recent trades for the "Market Trades" table (example: BTCUSDT)
        trades_cache_key = 'recent_trades'
        recent_trades = cache.get(trades_cache_key)
        if not recent_trades:
            recent_trades = client.get_recent_trades(symbol='BTCUSDT', limit=10)  # Adjust symbol as needed
            cache.set(trades_cache_key, recent_trades, 60)  # Cache for 1 minute

        # Format trades for template
        trades_list = [
            {
                'time': datetime.fromtimestamp(trade['time'] / 1000).strftime('%H:%M:%S'),
                'price': float(trade['price']),
                'amount': float(trade['qty']),
                'total': float(trade['price']) * float(trade['qty']),
                'side': 'text-bullish' if trade['isBuyerMaker'] else 'text-bearish'
            } for trade in recent_trades
        ]

        # Sample chart data for ApexCharts (replace with real data as needed)
        chart_data = {
            'labels': [f'Point {i}' for i in range(10)],
            'series': [
                {'name': 'Price', 'data': [10000, 10500, 10300, 10700, 11000, 10800, 11200, 11500, 11300, 11600]}
            ]
        }

        context = {
            'tickers': page_obj,  # Paginated tickers
            'trades': trades_list,
            'chart_data': chart_data,
        }
        return render(request, 'src/dashboard/exchange.html', context)

    except Exception as e:
        messages.error(request, f"Error fetching exchange data: {str(e)}")
        return render(request, 'src/dashboard/exchange.html', {
            'tickers': [],
            'trades': [],
            'chart_data': {'labels': [], 'series': []}
        })

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect

@csrf_protect
def accept_terms(request):
    if request.method == 'POST' and request.user.is_authenticated:
        request.user.show_terms_modal = False
        request.user.terms_accepted = True
        request.user.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)


# def convert_view(request):
#     # Import wallet balance for the logged-in user
#     wallet = Wallet.objects.filter(user=request.user).first()
#     wallet_balance = wallet.balance if wallet else 0
#     print(wallet_balance)

#     # Convert wallet balance (KES) to USD
#     usd_wallet_balance = convert_kes_to_usd(wallet_balance) if wallet_balance else 0
#     print(usd_wallet_balance)

#     context = {
#         'wallet_balance': wallet_balance,
#         'usd_wallet_balance': usd_wallet_balance,
#     }
#     # if request.method == 'POST':
#     #     try:
#     #         amount_kes = float(request.POST.get('amount_kes', 0))
#     #         usd_value = convert_kes_to_usd(amount_kes)
#     #         context.update({
#     #             'usd_value': usd_value,
#     #             'amount_kes': amount_kes
#     #         })
#     #     except ValueError:
#     #         context['error'] = "Invalid input. Please enter a valid number."
#     return render(request, 'src/dashboard/wallet.html', context)


def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist')
        
        user=authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Wrong username or password! Please Check and try again!')
    context = {'message':messages}

    return render(request, 'account/login.html', context)

@login_required
def logoutUser(request):
    logout(request)
    return redirect('account_login')

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.core.cache import cache
import pandas as pd
from binance.client import Client  # Adjust if using ccxt
import os
from datetime import datetime

@login_required
def exchange(request):
    try:
        # Initialize Binance client (use environment variables for security)
        client = Client(os.getenv('BINANCE_API_KEY'), os.getenv('BINANCE_API_SECRET'))

        # Fetch ticker data (24hr ticker for all symbols)
        cache_key = 'tickers'
        tickers = cache.get(cache_key)
        if not tickers:
            tickers = client.get_ticker()
            cache.set(cache_key, tickers, 300)  # Cache for 5 minutes

        # Convert tickers to DataFrame and select relevant fields
        df = pd.DataFrame(tickers)
        df = df[['symbol', 'priceChangePercent', 'lastPrice', 'lowPrice', 'highPrice', 'openPrice', 'closePrice']]
        
        # Convert to list of dictionaries for template
        tickers_list = df.to_dict('records')

        # Pagination
        paginator = Paginator(tickers_list, 10)  # Show 10 tickers per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Fetch recent trades for the "Market Trades" table (example: BTCUSDT)
        trades_cache_key = 'recent_trades'
        recent_trades = cache.get(trades_cache_key)
        if not recent_trades:
            recent_trades = client.get_recent_trades(symbol='BTCUSDT', limit=10)  # Adjust symbol as needed
            cache.set(trades_cache_key, recent_trades, 60)  # Cache for 1 minute

        # Format trades for template
        trades_list = [
            {
                'time': datetime.fromtimestamp(trade['time'] / 1000).strftime('%H:%M:%S'),
                'price': float(trade['price']),
                'amount': float(trade['qty']),
                'total': float(trade['price']) * float(trade['qty']),
                'side': 'text-bullish' if trade['isBuyerMaker'] else 'text-bearish'
            } for trade in recent_trades
        ]

        # Sample chart data for ApexCharts (replace with real data as needed)
        chart_data = {
            'labels': [f'Point {i}' for i in range(10)],
            'series': [
                {'name': 'Price', 'data': [10000, 10500, 10300, 10700, 11000, 10800, 11200, 11500, 11300, 11600]}
            ]
        }

        context = {
            'tickers': page_obj,  # Paginated tickers
            'trades': trades_list,
            'chart_data': chart_data,
        }
        return render(request, 'src/dashboard/exchange.html', context)

    except Exception as e:
        # messages.error(request, f"Error fetching exchange data: {str(e)}")
        return render(request, 'src/dashboard/exchange.html', {
            'tickers': [],
            'trades': [],
            'chart_data': {'labels': [], 'series': []}
        })

@login_required
def trade(request):
    if request.method != 'POST':
        return redirect('exchange')

    action = request.POST.get('action')        # "buy" or "sell"
    amount = request.POST.get('balance_amount')
    currency = request.POST.get('balance_currency')
    payment_method = request.POST.get('payment_method')

    # Convert amount safely
    try:
        amount = Decimal(amount)
        if amount <= 0:
            raise ValueError
    except:
        messages.error(request, "Invalid trade amount.")
        return redirect('exchange')

    try:
        with transaction.atomic():

            # Lock wallet to prevent race conditions
            wallet = Wallet.objects.select_for_update().filter(user=request.user).first()

            if not wallet:
                messages.error(request, "No wallet found. Please create a wallet first.")
                return redirect('wallet')

            # ======== BUY ===========
            if action == "buy":
                # For a purchase, user must have enough balance
                if wallet.balance < amount:
                    messages.error(request, "Insufficient balance to complete purchase.")
                    return redirect('exchange')

                # Deduct from wallet
                wallet.balance -= amount
                wallet.save()

                # TODO: Implement Binance BUY API call here
                # client.create_order(...)

            # ========= SELL ===========
            elif action == "sell":

                # (Optional) If selling requires holding asset in wallet, add checks here
                # For now, we assume SELL adds credit to wallet
                wallet.balance += amount
                wallet.save()

                # TODO: Implement Binance SELL API call here

            else:
                messages.error(request, "Invalid trade action.")
                return redirect('exchange')

            messages.success(request, f"{action.capitalize()} order placed successfully!")
            return redirect('exchange')

    except Exception as e:
        messages.error(request, "An error occurred while processing your trade. Please try again.")
        return redirect('exchange')


# def trade(request):
#     if request.method == 'POST':
#         action = request.POST.get('action')
#         amount = request.POST.get('balance_amount')
#         currency = request.POST.get('balance_currency')
#         payment_method = request.POST.get('payment_method')
#         # Implement Binance API call (e.g., client.create_order())
#         messages.success(request, f"{action.capitalize()} order placed successfully!")
#         return redirect('exchange')
#     return redirect('exchange')

@login_required
def exchange_trade(request):
    # Fetch wallet balance
    wallet_obj = Wallet.objects.filter(user=request.user).first()

    wallet_bal = wallet_obj.balance if wallet_obj else 0
    wallet_bal_usd = fetch_pair_conversion('KES', 'USD', float(wallet_bal)) if wallet_obj else 0

    if request.method != 'POST':
        return redirect('exchange')

    # Extract POST values
    get_amount = request.POST.get('get_amount')      # Amount user RECEIVES
    get_currency = request.POST.get('get_currency')
    pay_amount = request.POST.get('pay_amount')      # Amount user PAYS from wallet
    pay_currency = request.POST.get('pay_currency')

    # Convert amounts
    try:
        pay_amount = Decimal(pay_amount)
        get_amount = Decimal(get_amount)
        if pay_amount <= 0 or get_amount <= 0:
            raise ValueError
    except:
        messages.error(request, "Invalid exchange amount.")
        return redirect('exchange')

    try:
        with transaction.atomic():

            # Lock the wallet row
            wallet = Wallet.objects.select_for_update().filter(user=request.user).first()

            if not wallet:
                messages.error(request, "No wallet found. Please create a wallet first.")
                return redirect('wallet')

            # =========== CHECK BALANCE ===========
            # User pays in pay_currency. We assume wallet is in KES.
            # If pay_currency != wallet currency, convert required amount to KES.

            if pay_currency != "KES":
                # Convert pay_amount to KES using your conversion function
                required_kes = Decimal(fetch_pair_conversion(pay_currency, 'KES', float(pay_amount)))
            else:
                required_kes = pay_amount

            if wallet.balance < required_kes:
                messages.error(request, "Insufficient balance to complete exchange.")
                return redirect('exchange')

            # =========== DEDUCT AMOUNT ===========
            wallet.balance -= required_kes
            wallet.save()

            # =========== OPTIONAL: ADD RECEIVED CURRENCY ===========
            # For now, assume received amount goes *outside wallet* (Binance balance)
            # If you want to add get_amount to wallet, tell me and I'll implement multi-currency wallet

            # TODO: Integrate Binance API call here
            # client.create_order(...)

            messages.success(request, "Exchange completed successfully!")
            return redirect('exchange')

    except Exception as e:
        messages.error(request, "An error occurred while processing the exchange. Please try again.")
        return redirect('exchange')



# def exchange_trade(request):
#     # Fetch wallet balance
#     wallet_bal = Wallet.objects.filter(user=request.user).first()
#     wallet_bal_usd = 0
#     if wallet_bal:
#         wallet_bal = wallet_bal.balance
#         wallet_bal_usd = fetch_pair_conversion('KES', 'USD', float(wallet_bal))
#     else:
#         wallet_bal = 0
#     if request.method == 'POST':
#         get_amount = request.POST.get('get_amount')
#         get_currency = request.POST.get('get_currency')
#         pay_amount = request.POST.get('pay_amount')
#         pay_currency = request.POST.get('pay_currency')
#         # Implement Binance API call for exchange
#         messages.success(request, "Exchange completed successfully!")
#         return redirect('exchange')
#     return redirect('exchange')


# from django.contrib import admin
# from django.contrib.auth.models import User
# from django.core.mail import send_mail
# from django.contrib import messages

# @admin.action(description='Send email to selected users')
# def send_email_to_users(modeladmin, request, queryset):
#     for user in queryset:
#         if user.email:
#             send_mail(
#                 subject='Hello from Admin!',
#                 message='This is a test email sent from the Django admin panel.',
#                 from_email='admin@example.com',  # Update to your email
#                 recipient_list=[user.email],
#                 fail_silently=False,
#             )
#     messages.success(request, "Emails have been sent successfully!")

# class CustomUserAdmin(admin.ModelAdmin):
#     actions = [send_email_to_users]






# def homeView(request):


#     api_key = os.environ['BINANCE_API_KEY']

#     stock = 'PLTR'

#     api_key = os.environ['BINANCE_API_KEY']
#     period= 60

#     ts = TimeSeries(key=api_key, output_format='pandas',)
#     data_ts, meta_data_ts = ts.get_intraday(stock, interval='1min', outputsize='compact')

#     ti = TechIndicators(key=api_key, output_format='pandas')
#     data_ti, meta_data_ti  = ti.get_rsi(stock, interval='1min', time_period=period, series_type='close')

#     ts_df = data_ts
#     ti_df = data_ti

#     #Fundamentals
#     payload = {'function': 'OVERVIEW', 'symbol': 'PLTR', 'apikey': api_key}
#     r = requests.get('https://www.alphavantage.co/query', params=payload)
#     r = r.json()


#     #plotly graph
#     def candlestick():
#         figure = go.Figure(
#             data = [
#                     go.Candlestick(
#                         x = ts_df.index,
#                         high = ts_df['2. high'],
#                         low = ts_df['3. low'],
#                         open = ts_df['1. open'],
#                         close = ts_df['4. close'],
#                     )
#                     ]
#         )

#         candlestick_div = plot(figure, output_type='div')
#         return candlestick_div


#     sector = r['Sector']
#     marketcap = r['MarketCapitalization']
#     peratio = r['PERatio']
#     yearhigh = r['52WeekHigh']
#     yearlow = r['52WeekLow']
#     eps = r['EPS']



#     timeseries = ts_df.to_dict(orient='records')

#     closingprice = []
#     for k in timeseries:
#         closingprice.append(k['4. close'])

#     lowprice = []
#     for k in timeseries:
#         closingprice.append(k['3. low'])

#     highprice = []
#     for k in timeseries:
#         closingprice.append(k['2. high'])

#     openprice = []
#     for k in timeseries:
#         closingprice.append(k['1. open'])

#     pricedata = {
#         'close': [closingprice],
#         'open': [openprice],
#         'high': [highprice],
#         'low': [lowprice],
#     }

#     #miscellaneous stuff
#     day = datetime.datetime.now()
#     day = day.strftime("%A")

#     def human_format(num):
#         magnitude = 0
#         while abs(num) >= 1000:
#             magnitude += 1
#             num /= 1000.0
#         # add more suffixes if you need them
#         return '%.2f%s' % (num, ['', 'K', 'M', 'G', 'T', 'P'][magnitude])

#     marketcap = int(marketcap)
#     marketcap = human_format(marketcap)

#     closingprice = closingprice[0:15]


#     context = {
#         'sector': sector,
#         'marketcap': marketcap,
#         'peratio': peratio,
#         'yearhigh': yearhigh,
#         'yearlow': yearlow,
#         'eps': eps,
#         'closingprice': closingprice,
#         'openprice': openprice,
#         'highprice': highprice,
#         'lowprice': lowprice,
#         'pricedata': pricedata,
#         'timeseries': timeseries,
#         'stock': stock,
#         'day': day,
#         'candlestick': candlestick(),
#     }

#     context={}
#     return render(request, 'src/dashboard/market.html', context)

# def homeView(request):
#     if request.method == 'POST':
#         symbol = request.POST.get('symbol')
#         return redirect('/')

#     context={

#     }
#     return render(request, 'src/dashboard/market.html', context)



# def cryptoView(request):

#     if request.method == 'POST':
#         symbol = request.POST.get('symbol')
#         symbol = symbol.upper()
#     else:
#         symbol = 'BTCUSD'

#     data = spotquote(symbol)
#     pricedata = pricechange(symbol)
#     moredata = pricechange(symbol)



#     #get a fricken df
#     ts_df = candles(symbol)
#     #PlotlyGraph
#     def candlestick():
#         figure = go.Figure(
#             data = [
#                     go.Candlestick(
#                         x = ts_df.index,
#                         high = ts_df['high'],
#                         low = ts_df['low'],
#                         open = ts_df['open'],
#                         close = ts_df['close'],
#                     )
#                     ]
#         )

#         candlestick_div = plot(figure, output_type='div')
#         return candlestick_div
#     #endPlotlyGraph
#     percentchange = pricedata['priceChangePercent']
#     buyers = pricedata['askQty']
#     sellers = pricedata['bidQty']

#     eth = pricechange(symbol='ETHUSD')
#     btc = pricechange(symbol="BTCUSD")
#     ltc = pricechange(symbol="LTCUSD")



#     context={
#     'moredata': moredata,
#     'eth': eth,
#     'btc': btc,
#     'ltc': ltc,
#     'percentchange': percentchange,
#     'buyers': buyers,
#     'sellers': sellers,
#     'data': data,
#     'candlestick': candlestick(),
#     }
#     return render(request, 'src/dashboard/market.html', context)

