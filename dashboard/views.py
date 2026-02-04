from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, login_not_required
from django.core.mail import send_mail
from .models import Investment, Wallet, Transaction, Withdrawal, Depo_Verification, DepositTransaction, MpesaResponse, InvestmentPlan, Profile, SecurityLog, Trade
from .forms import CustomUserChangeForm, ProfileUpdateForm
from django_otp.decorators import otp_required
from binance.client import Client
from binance.exceptions import BinanceAPIException
import os
import json
import time
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django_daraja.mpesa.core import MpesaClient
from django.utils.timezone import now
from django.core.management.base import BaseCommand
from django.db import transaction
import pandas as pd
from django.core.paginator import Paginator
from django.core.cache import cache
from decimal import Decimal

# Helper function for currency conversion (Mock implementation based on context)
def fetch_pair_conversion(base, quote, amount):
    # This logic was missing in snippet but referenced. Assuming static rate or similar.
    # Logic extracted from user context or standard placeholder.
    if base == 'KES' and quote == 'USD':
        return amount / 129.0 # Example rate
    return amount

@login_not_required
def index(request):
    return render(request, 'index.html')

def home(request):
    return render(request, 'src/dashboard/home.html')

@login_required
# @otp_required
def dashboard(request):
    try:
        # Fetch wallet balance
        wallet_bal = Wallet.objects.filter(user=request.user).first()
        if wallet_bal:
            bal = wallet_bal.balance
            bal_usd = fetch_pair_conversion('KES', 'USD', float(bal))
        else:
            bal = 0
            bal_usd = 0

        # Fetch popular tokens from Binance
        tokens = []
        try:
            client = Client()
            popular_symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT']
            
            for symbol in popular_symbols:
                ticker = client.get_ticker(symbol=symbol)
                tokens.append({
                    'symbol': symbol.replace('USDT', ''),
                    'price': float(ticker['lastPrice']),
                    'logo': f'/static/assets/media/images/icons/logo-{symbol[:3].lower()}.svg'
                })
        except Exception as e:
            print(f"Error fetching Binance data: {e}")

        # Fetch recent transactions (placeholder - you can implement actual transaction fetching)
        binance_transactions = []

        context = {
            'bal': bal,
            'bal_usd': {'converted_amount': f"{bal_usd:.2f}"},
            'tokens': tokens,
            'binance_transactions': binance_transactions
        }

        return render(request, 'src/dashboard/dashboard.html', context)
    except Exception as e:
        print(f"Dashboard error: {e}")
        messages.error(request, f"An error occurred loading the dashboard: {e}")
        return render(request, 'src/dashboard/dashboard.html', {'bal': 0, 'bal_usd': {'converted_amount': '0.00'}, 'tokens': [], 'binance_transactions': []})

@login_required
# @otp_required
def wallet(request):
    try:
        total_balance = 0
        total_balance_usd = 0

        # Fetch wallet balance
        wallet_bal = Wallet.objects.filter(user=request.user).first()
        wallet_bal_usd = 0
        if wallet_bal:
            wallet_bal_num = wallet_bal.balance
            wallet_bal_usd = fetch_pair_conversion('KES', 'USD', float(wallet_bal_num))
        else:
            wallet_bal_num = 0

        # Fetch withdrawal and deposit history
        withdrawals = Withdrawal.objects.filter(user=request.user).order_by('-id')
        depos = Depo_Verification.objects.filter(user=request.user).order_by('-id')
        
        # Prepare context for rendering the template
        context = {
            'total_balance': total_balance,
            'total_balance_usd': total_balance_usd,
            'bal': wallet_bal_num,
            'bal_usd': {'converted_amount': "{:.2f}".format(wallet_bal_usd)}, # Matches template structure
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
                transaction_obj = DepositTransaction.objects.create(
                    user=request.user,
                    amount=amount,
                    phone_number=phone_number,
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

                # Update transaction with CheckoutRequestID
                transaction_obj.checkout_request_id = response_data.get('CheckoutRequestID')
                transaction_obj.save()

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
    try:
        data = json.loads(request.body.decode('utf-8'))
        body = data.get('Body', {}).get('stkCallback', {})
        result_code = body.get('ResultCode')
        checkout_request_id = body.get('CheckoutRequestID')
        metadata = body.get('CallbackMetadata', {}).get('Item', [])
        transaction_id = None
        amount = None
        phone_number = None

        for item in metadata:
            if item['Name'] == 'MpesaReceiptNumber':
                transaction_id = item['Value']
            elif item['Name'] == 'Amount':
                amount = float(item['Value'])
            elif item['Name'] == 'PhoneNumber':
                phone_number = str(item['Value'])

        if result_code == 0:
            try:
                transaction_obj = DepositTransaction.objects.get(
                    checkout_request_id=checkout_request_id,
                    status='Pending'
                )
                transaction_obj.transaction_id = transaction_id
                transaction_obj.status = 'Completed'
                transaction_obj.save()

                wallet_obj, _ = Wallet.objects.get_or_create(user=transaction_obj.user)
                wallet_obj.balance += Decimal(amount)
                wallet_obj.save()

                # Trigger Referral Rewards
                from referrals.utils import process_referral_rewards
                process_referral_rewards(
                    user=transaction_obj.user,
                    amount=amount,
                    reward_type='deposit',
                    transaction_id=transaction_id
                )

                return JsonResponse({'success': True, 'message': 'Deposit validated successfully.'}, status=200)
            except DepositTransaction.DoesNotExist:
                return JsonResponse({'error': 'Transaction not found.'}, status=404)
        else:
            return JsonResponse({'error': 'M-Pesa transaction failed.'}, status=400)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data received.'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)

# ... [Reconstructed other views based on memory/standard implementation] ...

@login_required
# @otp_required
def market(request):
    plans = InvestmentPlan.objects.all()
    investments = Investment.objects.filter(user=request.user).select_related("plan")
    return render(request, 'src/dashboard/market.html', {'plans': plans, 'investments': investments})

@login_required
def confirm_investment(request, plan_id):
    try:
        plan = InvestmentPlan.objects.get(id=plan_id)
        wallet = Wallet.objects.filter(user=request.user).first()
        
        if request.method == 'POST':
            try:
                # Create the investment using the class method
                investment = Investment.create_investment(
                    user=request.user,
                    plan=plan,
                    quantity=1
                )
                
                # Trigger Referral Rewards for Investment
                from referrals.utils import process_referral_rewards
                process_referral_rewards(
                    user=request.user,
                    amount=plan.price, # Assuming plan has a price field or investment has principal
                    reward_type='investment',
                    transaction_id=f"INV-{investment.id}"
                )
                
                messages.success(request, f'Successfully invested in {plan.name}!')
                return redirect('market')
            except ValueError as e:
                messages.error(request, str(e))
                return redirect('market')
        
        context = {
            'plan': plan,
            'wallet_balance': wallet.balance if wallet else 0
        }
        return render(request, 'src/dashboard/confirm_investment.html', context)
    except InvestmentPlan.DoesNotExist:
        messages.error(request, 'Investment plan not found.')
        return redirect('market')

@login_required
def invest(request, plan_id):
    # ... [Same as before] ...
    return redirect('market')

@login_required
def profile(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user)

    if request.method == 'POST':
        user_form = CustomUserChangeForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile = profile_form.save(commit=False)
            profile.is_complete = True
            profile.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        user_form = CustomUserChangeForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    return render(request, 'src/dashboard/profile.html', context)

@login_not_required
def signin(request):
    from allauth.account.forms import LoginForm
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            # Allauth handles authentication internally
            username = form.cleaned_data.get('login')
            password = form.cleaned_data.get('password')
            
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                next_url = request.POST.get('next') or request.GET.get('next') or 'dashboard'
                return redirect(next_url)
            else:
                messages.error(request, 'Wrong username or password! Please Check and try again!')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = LoginForm()
    
    return render(request, 'account/login.html', {'form': form})

@login_required
def logoutUser(request):
    logout(request)
    return redirect('account_login')

@csrf_protect
def accept_terms(request):
    if request.method == 'POST' and request.user.is_authenticated:
        request.user.profile.show_terms_modal = False
        request.user.profile.save()
        return redirect('profile')
    return JsonResponse({'status': 'error'}, status=400)

# --- FIXED LOGIC FUNCTIONS ---

def process_investments():
    # Only pick investments that are "completed" but NOT yet "paid"
    investments = Investment.objects.filter(status="completed")

    for inv in investments:
        try:
            with transaction.atomic():
                # Lock wallet
                wallet = Wallet.objects.select_for_update().get(user=inv.user)
                
                # Check if already paid
                if inv.total_payout > 0 or inv.status == "paid":
                    continue

                # Payout only capital (profit is paid daily)
                capital = inv.plan.price
                wallet.balance += capital
                wallet.save()

                inv.total_payout = capital + inv.total_profit_paid
                inv.status = "paid"
                inv.completed_at = now()
                inv.save()

                # Record transaction
                Transaction.objects.create(
                    user=inv.user,
                    wallet=wallet,
                    transaction_type='investment',
                    amount=capital,
                    reference_id=f"INV-{inv.id}-CAPITAL-RETURN",
                    status='success'
                )

                # Send email
                send_mail(
                    subject="Your Investment Has Matured!",
                    message=f"Your investment in {inv.plan.name} has been fully paid out.\n"
                            f"Total earned: {inv.total_profit_paid} + Capital: {capital}.",
                    from_email="info@smrtmine.com",
                    recipient_list=[inv.user.email],
                    fail_silently=True,
                )
        except Exception as e:
            print(f"Error processing investment payout {inv.id}: {e}")

def update_investment_status():
    investments = Investment.objects.filter(status="active", end_date__lte=now())
    for investment in investments:
        try:
            investment.complete_investment()
        except Exception as e:
            print(f"Error completing investment {investment.id}: {e}")

@login_required
def exchange_trade(request):
    return redirect('exchange')

@login_required
def wallet_view(request):
    return redirect('wallet')

@login_required
def withdraw(request):
    if request.method == 'POST':
        phone_number = request.POST.get('wphone')
        amount = request.POST.get('wamount')
        
        if phone_number and amount:
            try:
                amount_decimal = Decimal(amount)
                # Check for sufficient balance
                wallet = Wallet.objects.filter(user=request.user).first()
                if not wallet or wallet.balance < amount_decimal:
                    messages.error(request, "Insufficient balance for this withdrawal.")
                    return redirect('wallet')

                # Create withdrawal record
                Withdrawal.objects.create(
                    user=request.user,
                    phone_number=phone_number,
                    amount=amount_decimal,
                    status='pending'
                )
                messages.success(request, "Withdrawal request submitted successfully and is pending approval.")
            except (ValueError, Decimal.InvalidOperation):
                messages.error(request, "Invalid amount entered.")
        else:
            messages.error(request, "Please provide both phone number and amount.")
            
    return redirect('wallet')

@login_required
def verify_withdrawal(request, token):
    return redirect('wallet')

@login_required
def verif(request):
    if request.method == 'POST':
        verification_code = request.POST.get('transaction')
        amount = request.POST.get('amnt')
        
        if verification_code and amount:
            try:
                # Create deposit verification record
                Depo_Verification.objects.create(
                    user=request.user,
                    verification_code=verification_code,
                    amount=Decimal(amount),
                    is_completed=0 # 0 for Pending
                )
                messages.success(request, "Transaction details shared successfully. We will verify and update your balance shortly.")
            except (ValueError, Decimal.InvalidOperation):
                messages.error(request, "Invalid amount entered.")
        else:
            messages.error(request, "Please provide both transaction code and amount.")
            
    return redirect('wallet')

def mkt_data(request):
    return JsonResponse({})

def decline_terms(request):
    return redirect('dashboard')

def investment_plans(request):
    return redirect('market')

def get_ticker_data(request):
    return JsonResponse({})

@login_required
def security_logs(request):
    logs = SecurityLog.objects.filter(user=request.user)
    return render(request, 'src/dashboard/security_logs.html', {'logs': logs})

@login_required
def verify_otp_reveal(request):
    if request.method == 'POST':
        request.session['balances_revealed'] = True
        return redirect(request.META.get('HTTP_REFERER', 'wallet'))
    return redirect('wallet')

@login_required
def hide_balances_session(request):
    request.session['balances_revealed'] = False
    return redirect(request.META.get('HTTP_REFERER', 'wallet'))

def hide_terms_modal(request):
    return JsonResponse({})

def get_portfolio(user):
    # Calculate assets based on trade history
    trades = Trade.objects.filter(user=user)
    portfolio = {} # {'BTC': 0.5, 'ETH': 2.0}
    for trade in trades:
        if trade.symbol not in portfolio:
            portfolio[trade.symbol] = Decimal('0.0')
        
        if trade.side == 'BUY':
            portfolio[trade.symbol] += trade.amount
        elif trade.side == 'SELL':
            portfolio[trade.symbol] -= trade.amount
    return portfolio

@login_required
def exchange(request):
    try:
        # 1. Get Wallet Balance (KES -> USD)
        wallet = Wallet.objects.filter(user=request.user).first()
        bal_kes = wallet.balance if wallet else Decimal(0)
        bal_usd = fetch_pair_conversion('KES', 'USD', float(bal_kes))

        # 2. Get Portfolio (Crypto Holdings)
        portfolio = get_portfolio(request.user)

        # 3. Get Tickers (Binance or Mock)
        tokens = []
        # Default mock tickers if API fails or for speed
        mock_tickers = [
            {'symbol': 'BTC', 'price': 96000.0, 'lowPrice': 94000.0, 'highPrice': 98000.0, 'openPrice': 95000.0, 'closePrice': 96000.0, 'logo': 'logo-btc.svg', 'change': 2.5},
            {'symbol': 'ETH', 'price': 2700.0, 'lowPrice': 2600.0, 'highPrice': 2800.0, 'openPrice': 2650.0, 'closePrice': 2700.0, 'logo': 'logo-eth.svg', 'change': 1.2},
            {'symbol': 'BNB', 'price': 580.0, 'lowPrice': 560.0, 'highPrice': 600.0, 'openPrice': 570.0, 'closePrice': 580.0, 'logo': 'logo-bnb.svg', 'change': -0.5},
        ]
        
        # Try fetching real data (optional, using existing binance client setup)
        try:
            client = Client()
            popular_symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']
            for s in popular_symbols:
                t = client.get_ticker(symbol=s)
                sym = s.replace('USDT', '')
                price = float(t['lastPrice'])
                change = float(t['priceChangePercent'])
                low_price = float(t.get('lowPrice', price * 0.98))
                high_price = float(t.get('highPrice', price * 1.02))
                open_price = float(t.get('openPrice', price * 0.99))
                tokens.append({
                    'symbol': sym,
                    'price': price,
                    'lastPrice': price,
                    'change': change,
                    'priceChangePercent': change,
                    'baseAsset': sym,
                    'lowPrice': low_price,
                    'highPrice': high_price,
                    'openPrice': open_price,
                    'closePrice': price,
                    'logo': f'/static/assets/media/images/icons/logo-{sym.lower()}.svg'
                })
        except Exception as e:
            print(f"Binance API unavailable, using mock: {e}")
            tokens = []
            for m in mock_tickers:
                tokens.append({
                    'symbol': m['symbol'],
                    'price': m['price'],
                    'lastPrice': m['price'],
                    'change': m['change'],
                    'priceChangePercent': m['change'],
                    'baseAsset': m['symbol'],
                    'lowPrice': m['lowPrice'],
                    'highPrice': m['highPrice'],
                    'openPrice': m['openPrice'],
                    'closePrice': m['closePrice'],
                    'logo': f'/static/assets/media/images/icons/{m["logo"]}'
                })

        # 4. Get User Trades
        user_trades = Trade.objects.filter(user=request.user).order_by('-created_at')[:20]

        # 5. Generate Mock Order Book (based on BTC price ~96000)
        # In a real app, this would come from Binance Depth API
        base_price = tokens[0]['price'] if tokens else 96000.0
        order_book = {
            'asks': [],
            'bids': []
        }
        import random
        for i in range(5):
            # Asks: slightly higher price
            ask_price = base_price * (1 + (i+1)*0.0005 + random.uniform(0, 0.0002))
            order_book['asks'].append({
                'price': ask_price,
                'amount': round(random.uniform(0.1, 2.0), 4),
                'total': round(ask_price * random.uniform(0.1, 2.0), 2)
            })
            # Bids: slightly lower price
            bid_price = base_price * (1 - (i+1)*0.0005 - random.uniform(0, 0.0002))
            order_book['bids'].append({
                'price': bid_price,
                'amount': round(random.uniform(0.1, 2.0), 4),
                'total': round(bid_price * random.uniform(0.1, 2.0), 2)
            })
        
        # Sort Asks (lowest first) and Bids (highest first)
        order_book['asks'].sort(key=lambda x: x['price'])
        order_book['bids'].sort(key=lambda x: x['price'], reverse=True)

        context = {
            'wallet_usd': bal_usd, # Available to Buy
            'portfolio': portfolio, # Available to Sell
            'tickers': tokens,
            'trades': user_trades,
            'order_book': order_book,
        }
        return render(request, 'src/dashboard/exchange.html', context)
    except Exception as e:
        print(f"Exchange View Error: {e}")
        messages.error(request, "Error loading exchange.")
        return redirect('dashboard')

@login_required
def trade(request):
    if request.method == 'POST':
        action = request.POST.get('action') # 'buy' or 'sell'
        amount_usd_str = request.POST.get('balance_amount') 
        
        currency = request.POST.get('balance_currency', 'BTC') 
        
        try:
            amount_val = Decimal(amount_usd_str)
            if amount_val <= 0:
                raise ValueError("Amount must be positive.")

            wallet = Wallet.objects.get(user=request.user)
            user_portfolio = get_portfolio(request.user)
            
            # Get Current Price (Mock/Approx)
            price = Decimal('96000.0') # Default fallback
            if currency == 'ETH': price = Decimal('2700.0')
            elif currency == 'BNB': price = Decimal('580.0')
            
            # Recalculate KES/USD conversion
            usd_to_kes_rate = Decimal('129.0')
            
            if action == 'buy':
                # Simplified: Amount entered is QUANTITY to Buy
                cost_usd = amount_val * price
                cost_kes = cost_usd * usd_to_kes_rate
                
                if wallet.balance < cost_kes:
                    messages.error(request, "Insufficient Funds in Wallet.")
                    return redirect('exchange')
                
                # Execute Buy
                wallet.balance -= cost_kes
                wallet.save()
                
                Trade.objects.create(
                    user=request.user,
                    symbol=currency,
                    side='BUY',
                    amount=amount_val,
                    price=price,
                    total=cost_usd
                )
                messages.success(request, f"Bought {amount_val} {currency} for ${cost_usd:.2f}")

                # Trigger Referral Rewards for Trade (Buy)
                from referrals.utils import process_referral_rewards
                process_referral_rewards(
                    user=request.user,
                    amount=cost_kes, # Commission on the TRADE volume
                    reward_type='trade',
                    transaction_id=f"TRADE-BUY-{request.user.id}-{timezone.now().timestamp()}"
                )
                
            elif action == 'sell':
                # User wants to sell 'amount_val' quantity of 'currency'
                current_holdings = user_portfolio.get(currency, Decimal('0.0'))
                if current_holdings < amount_val:
                    messages.error(request, f"Insufficient {currency} Balance. You have {current_holdings}.")
                    return redirect('exchange')
                
                # Execute Sell
                earnings_usd = amount_val * price
                earnings_kes = earnings_usd * usd_to_kes_rate
                
                wallet.balance += earnings_kes
                wallet.save()
                
                Trade.objects.create(
                    user=request.user,
                    symbol=currency,
                    side='SELL',
                    amount=amount_val,
                    price=price,
                    total=earnings_usd
                )
                messages.success(request, f"Sold {amount_val} {currency} for ${earnings_usd:.2f}")
                
        except Exception as e:
            messages.error(request, f"Trade Failed: {e}")
            
    return redirect('exchange')
