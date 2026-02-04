from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.referral_dashboard, name='referral_dashboard'),
]
