from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages

# Create your views here.
@login_required
def dashboard(request): 
    return render(request, 'src/dashboard/dashboard.html')

@login_required
def wallet(request):
    return render(request, 'src/dashboard/wallet.html')

@login_required
def market(request):
    return render(request, 'src/dashboard/market.html')

@login_required
def profile(request):
    return render(request, 'src/dashboard/profile.html')

@login_required
def exchange(request):
    return render(request, 'src/dashboard/exchange.html')

def signup(request):
    return render(request, 'src/dashboard/sign-up.html')

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