from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from allauth.socialaccount.forms import SignupForm
from django import forms
from django.core.mail import send_mail

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


# class MyCustomSocialSignupForm(SignupForm):
#     first_name = forms.CharField(max_length=30, label='First Name')
#     last_name = forms.CharField(max_length=30, label='Last Name')
#     phone_number = forms.CharField(max_length=15, label='Phone Number', required=False)

#     def save(self, request):
#         # Ensure you call the parent class's save method.
#         # .save() returns a User object.
#         user = super(MyCustomSocialSignupForm, self).save(request)

#         # Add your own processing here.
#         user.first_name = self.cleaned_data['first_name']
#         user.last_name = self.cleaned_data['last_name']
#         user.phone_number = self.cleaned_data.get('phone_number', '')
#         user.save()

#         # Example: send a welcome email
#         send_mail(
#             'Welcome to SmartMine',
#             'Hello {},\n\nThank you for signing up for SmartMine.'.format(user.first_name),
#             'noreply@smartmine.com',
#             [user.email],
#             fail_silently=False,
#         )

#         # You must return the original result.
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