from django.urls import path

from . import views as wallets_veiws


urlpatterns = [
    path('access/token', wallets_veiws.getAccessToken, name='get_mpesa_access_token'),
    path('lipa_na_mpesa/', wallets_veiws.lipa_na_mpesa_online, name='mpesastk'),

    
    # register, confirmation, validation and callback urls
    path('c2b/register', wallets_veiws.register_urls, name="register_mpesa_validation"),
    path('c2b/confirmation', wallets_veiws.confirmation, name="confirmation"),
    path('c2b/validation', wallets_veiws.validation, name="validation"),
    path('c2b/callback', wallets_veiws.mpesa_callback, name="call_back"),
]