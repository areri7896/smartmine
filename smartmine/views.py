from django.shortcuts import render
from django.contrib.auth.decorators import login_not_required

# import pandas as pd
# from dotenv import load_dotenv
# load_dotenv()
# import os

# Create your views here.

@login_not_required
def index(request):
#     from binance.client import Client

# # Test 
#     api_key = os.environ['BINANCE_API_KEY_TEST']
#     api_secret = os.environ['BINANCE_API_SECRET_TEST']
#     client = Client(api_key, api_secret, testnet=True)
    
    return render(request, 'src/landing/index.html', {})

# def login(request):
#     return render(request, 'src/landing/login.html', {})

# def company(request):
#     return render(request, 'src/landing/company.html', {})

# def blog(request):
#     return render(request, 'src/landing/blog.html', {})