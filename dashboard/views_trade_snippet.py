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
            {'symbol': 'BTC', 'price': 96000.0, 'logo': 'logo-btc.svg', 'change': 2.5},
            {'symbol': 'ETH', 'price': 2700.0, 'logo': 'logo-eth.svg', 'change': 1.2},
            {'symbol': 'BNB', 'price': 580.0, 'logo': 'logo-bnb.svg', 'change': -0.5},
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
                tokens.append({
                    'symbol': sym,
                    'price': price,
                    'lastPrice': price, # Alias for template
                    'change': change,
                    'priceChangePercent': change, # Alias
                    'baseAsset': sym, # Alias
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
                    'logo': f'/static/assets/media/images/icons/{m["logo"]}'
                })

        # 4. Get User Trades
        user_trades = Trade.objects.filter(user=request.user).order_by('-created_at')[:20]

        context = {
            'wallet_usd': bal_usd, # Available to Buy
            'portfolio': portfolio, # Available to Sell
            'tickers': tokens,
            'trades': user_trades,
            # 'chart_data': ... (left as is or mocked)
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
        amount_usd_str = request.POST.get('balance_amount') # Input is in USD usually? Or BTC?
        # Let's assume input is in the "Amount" field.
        # Check exchange.html form: 
        # <input name="balance_amount" ...>
        # <select name="balance_currency"> (BTC, USD, etc)
        # <button name="action" value="buy">
        
        currency = request.POST.get('balance_currency', 'BTC') # The asset to buy/sell
        
        # NOTE: The current form is a bit ambiguous. Let's simplify:
        # IF BUY: User enters amount in USD (spending USD to get BTC) OR amount in BTC (buying X BTC)?
        # Let's assume for simplicity:
        # BUY -> Spending 'balance_amount' (USD) to buy 'currency'.
        # SELL -> Selling 'balance_amount' ('currency') to get USD.
        
        try:
            amount_val = Decimal(amount_usd_str)
            if amount_val <= 0:
                raise ValueError("Amount must be positive.")

            wallet = Wallet.objects.get(user=request.user)
            user_portfolio = get_portfolio(request.user)
            
            # Get Current Price
            # (In production, fetch real-time price again. Here using mock/approx)
            price = Decimal('96000.0') # Default fallback
            if currency == 'ETH': price = Decimal('2700.0')
            elif currency == 'BNB': price = Decimal('580.0')
            
            # Recalculate KES/USD conversion
            usd_to_kes_rate = Decimal('129.0')
            
            if action == 'buy':
                # User wants to buy 'currency' worth 'amount_val' USD ?? 
                # OR is 'amount_val' the quantity of coins?
                # "Enter your trade Amount" -> usually Quantity.
                # Let's assume amount_val is Quantity (e.g. 0.1 BTC).
                
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
