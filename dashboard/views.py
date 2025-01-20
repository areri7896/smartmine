from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from allauth.socialaccount.forms import SignupForm
from django import forms
from django.core.mail import send_mail

import os
import pandas as pd
from binance.client import Client
import requests
import json
import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .functions import *

from dotenv import load_dotenv
load_dotenv()

api_key = os.environ['BINANCE_API_KEY']
api_secret = os.environ['BINANCE_SECRET_KEY']
client = Client(api_key, api_secret, testnet=True)
tickers = client.get_all_tickers()
df = pd.DataFrame(tickers)
df.head()
# print(tickers)


url = 'https://api1.binance.com'
api_call = '/api/v3/ticker/price'
headers = {'content-type': 'application/json', 'X-MBX-APIKEY': api_key}
response = requests.get(url + api_call , headers=headers)
response = json.loads(response.text)
df = pd.DataFrame.from_records(response)
# print(response)
df.head()

#checking server status
client.ping() #empty response no errors
res= client.get_server_time()
ts=res['serverTime']/1000
your_dt = datetime.datetime.fromtimestamp(ts)
fmt = your_dt.strftime("%Y-%n-%d %H:%M:%S")
print(fmt)


# getting all tickers
# coin_info = client.get_all_tickers()
# df=pd.DataFrame(coin_info)
# df.head()

# print(tickers)

# Create your views here.
# assets = ['BTCUSDT','ETHUDT','BNBUSDT']
# assets =(coin.lower()+'@kline_1m' for coin in assets)
# assets ='/'.join(assets)
# socket = "wss://stream.binance.com:9443/stream?streams="
# ws=websockets.websocketApp(socket,on_message='on_message')
# ws.run_forever()

# def on_message(ws, message):
#     message=json.loads(message)
#     manipulation(message)
#     print (message)

# def manipulation(source):
#     rel_data = source ['data']['k']['c']
#     evt_time = pd.to_datetime(source['data']['E'], unit='ms')
#     df=pd.DataFrame(rel_data,columns=source[['data']['s']], index=[evt_time])
#     df.index.name ='timestamp'
#     df = df.astype(float)
#     df=df.reset_index()
#     print(df)
#     return df

#https://www.youtube.com/redirect?event=video_description&redir_token=QUFFLUhqbTR2cHBLOV9rN0lvTUJNVWJRMGE5bWd6RzBuQXxBQ3Jtc0tuTW85WUdYcVdXMEdNdXVwczZzeUthbEhRWUpRX3AzRnI3eWNBZUdONDdvYURfOFZyMVVuNlh6Y0VSNlpYWi13LUQzemxTaWJ5dlpyNHMwWkRndUVqcy0tVkRFZzNXYkx3aXR0WWlEb1U3NGZLRTJtVQ&q=https%3A%2F%2Fgithub.com%2Fsevenisalie%2Fdjango_alpha_vantage&v=3OOD9bFdBOQ

@csrf_exempt
def get_ticker_data(request):
    try:
        # Fetch all tickers
        tickers = client.get_all_tickers()
        df = pd.DataFrame(tickers)
        df['price'] = pd.to_numeric(df['price'])  # Convert price to numeric
        df['symbol'] = pd.to_numeric(df['symbol'])  # Convert price to numeric
        return JsonResponse(df.to_dict(orient='records'), safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@login_required
def dashboard(request): 
    api_key = os.environ['BINANCE_API_KEY']
    api_secret = os.environ['BINANCE_SECRET_KEY']
    client = Client(api_key, api_secret, testnet=True)
    tickers = client.get_all_tickers()
    df = pd.DataFrame(tickers)
    df.head()
    # tick_symbol = [ticker['symbol'] for ticker in tickers]
    # tick_price = [ticker['price'] for ticker in tickers]
    combined_tickers = [(ticker['symbol'], ticker['price']) for ticker in tickers]
    context = {'tickers': combined_tickers, 'df':df}

    # context = {'tick_symbol':tick_symbol, 'tick_price':tick_price}
    return render(request, 'src/dashboard/dashboard.html', context)



def account(request):
    info = client.get_account()
    return info


def asset_balance(request):
    asset_balance = client.get_asset_balance()
    asset_details = client.get_asset_details()
    context = {'asset_balance':asset_balance, 'asset_details':asset_details}
    return render(request, 'src/dashboard/wallet.html', context)


@login_required
def wallet(request):

    return render(request, 'src/dashboard/wallet.html')


def exchange(request):
    exchange_info = client.get_exchange_info()
    exchange_info.keys()
    df =pd.DataFrame(exchange_info['symbols'])
    return df


def mkt_data(request):
    market_depth = client.get_order_book(symbol = 'BTCBUSD')
    market_depth 
    bids = pd.DataFrame(market_depth['bids'])
    bids.column = ['price', 'bids']
    asks = pd.DataFrame(market_depth['asks'])
    asks.columns =['price', 'asks']
    df = pd.concat([bids,asks]).fillna(0)
    return df

def recent_trades(request):
    recent_trade= client.get_recent_trades(symbol='BTCBUSD')
    df = pd.DataFrame(recent_trade)
    df.head()
    return df

def avg_price(request):
    avg_price = client.get_avg_price()
    return avg_price

@login_required
def market(request):
    api_key = os.environ['BINANCE_API_KEY']
    api_secret = os.environ['BINANCE_SECRET_KEY']
    client = Client(api_key, api_secret, testnet=True)
    tickers = client.get_all_tickers()
    df = pd.DataFrame(tickers)
    # df.head()
    context = {'tickers':tickers, 'df':df}
    return render(request, 'src/dashboard/market.html', context)

@login_required
def profile(request):
    return render(request, 'src/dashboard/profile.html')

@login_required
def exchange(request):
    exchange_info = client.get_exchange_info()
    df=pd.DataFrame(exchange_info['symbols'])
    context = {'df':df,}
    return render(request, 'src/dashboard/exchange.html')


# class MyCustomSocialSignupForm(SignupForm):
#     first_name = forms.CharField(max_length=30, label='First Name')
#     last_name = forms.CharField(max_length=30, label='Last Name')
#     phone_number = forms.CharField(max_length=15, label='Phone Number', required=False
#     def save(self, request):
#         user = super(MyCustomSocialSignupForm, self).save(request)

#         user.first_name = self.cleaned_data['first_name']
#         user.last_name = self.cleaned_data['last_name']
#         user.phone_number = self.cleaned_data.get('phone_number', '')
#         user.save()
#         #send a welcome email
#         send_mail(
#             'Welcome to SmartMine',
#             'Hello {},\n\nThank you for signing up for SmartMine.'.format(user.first_name),
#             'noreply@smartmine.com',
#             [user.email],
#             fail_silently=False,
#         )
#         return user

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



def homeView(request):


    api_key = os.environ['BINANCE_API_KEY']

    stock = 'PLTR'

    api_key = os.environ['BINANCE_API_KEY']
    period= 60

    ts = TimeSeries(key=api_key, output_format='pandas',)
    data_ts, meta_data_ts = ts.get_intraday(stock, interval='1min', outputsize='compact')

    ti = TechIndicators(key=api_key, output_format='pandas')
    data_ti, meta_data_ti  = ti.get_rsi(stock, interval='1min', time_period=period, series_type='close')

    ts_df = data_ts
    ti_df = data_ti

    #Fundamentals
    payload = {'function': 'OVERVIEW', 'symbol': 'PLTR', 'apikey': api_key}
    r = requests.get('https://www.alphavantage.co/query', params=payload)
    r = r.json()


    #plotly graph
    def candlestick():
        figure = go.Figure(
            data = [
                    go.Candlestick(
                        x = ts_df.index,
                        high = ts_df['2. high'],
                        low = ts_df['3. low'],
                        open = ts_df['1. open'],
                        close = ts_df['4. close'],
                    )
                    ]
        )

        candlestick_div = plot(figure, output_type='div')
        return candlestick_div


    sector = r['Sector']
    marketcap = r['MarketCapitalization']
    peratio = r['PERatio']
    yearhigh = r['52WeekHigh']
    yearlow = r['52WeekLow']
    eps = r['EPS']



    timeseries = ts_df.to_dict(orient='records')

    closingprice = []
    for k in timeseries:
        closingprice.append(k['4. close'])

    lowprice = []
    for k in timeseries:
        closingprice.append(k['3. low'])

    highprice = []
    for k in timeseries:
        closingprice.append(k['2. high'])

    openprice = []
    for k in timeseries:
        closingprice.append(k['1. open'])

    pricedata = {
        'close': [closingprice],
        'open': [openprice],
        'high': [highprice],
        'low': [lowprice],
    }

    #miscellaneous stuff
    day = datetime.datetime.now()
    day = day.strftime("%A")

    def human_format(num):
        magnitude = 0
        while abs(num) >= 1000:
            magnitude += 1
            num /= 1000.0
        # add more suffixes if you need them
        return '%.2f%s' % (num, ['', 'K', 'M', 'G', 'T', 'P'][magnitude])

    marketcap = int(marketcap)
    marketcap = human_format(marketcap)

    closingprice = closingprice[0:15]


    context = {
        'sector': sector,
        'marketcap': marketcap,
        'peratio': peratio,
        'yearhigh': yearhigh,
        'yearlow': yearlow,
        'eps': eps,
        'closingprice': closingprice,
        'openprice': openprice,
        'highprice': highprice,
        'lowprice': lowprice,
        'pricedata': pricedata,
        'timeseries': timeseries,
        'stock': stock,
        'day': day,
        'candlestick': candlestick(),
    }

    context={}
    return render(request, 'src/dashboard/dashboard.html', context)

def homeView(request):
    if request.method == 'POST':
        symbol = request.POST.get('symbol')
        return redirect('/')

    context={

    }
    return render(request, 'src/dashboard/dashboard.html', context)



def cryptoView(request):

    if request.method == 'POST':
        symbol = request.POST.get('symbol')
        symbol = symbol.upper()
    else:
        symbol = 'BTCUSD'

    data = spotquote(symbol)
    pricedata = pricechange(symbol)
    moredata = pricechange(symbol)



    #get a fricken df
    ts_df = candles(symbol)
    #PlotlyGraph
    def candlestick():
        figure = go.Figure(
            data = [
                    go.Candlestick(
                        x = ts_df.index,
                        high = ts_df['high'],
                        low = ts_df['low'],
                        open = ts_df['open'],
                        close = ts_df['close'],
                    )
                    ]
        )

        candlestick_div = plot(figure, output_type='div')
        return candlestick_div
    #endPlotlyGraph
    percentchange = pricedata['priceChangePercent']
    buyers = pricedata['askQty']
    sellers = pricedata['bidQty']

    eth = pricechange(symbol='ETHUSD')
    btc = pricechange(symbol="BTCUSD")
    ltc = pricechange(symbol="LTCUSD")



    context={
    'moredata': moredata,
    'eth': eth,
    'btc': btc,
    'ltc': ltc,
    'percentchange': percentchange,
    'buyers': buyers,
    'sellers': sellers,
    'data': data,
    'candlestick': candlestick(),
    }
    return render(request, 'src/dashboard/market.html', context)