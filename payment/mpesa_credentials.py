import requests
import json
from requests.auth import HTTPBasicAuth
from datetime import datetime
import base64
from decouple import config


class MpesaC2bCredential:
    consumer_key = config('MPESA_CONSUMER_KEY')
    consumer_secret = config('MPESA_CONSUMER_SECRET')
    mpesa_environment = config('MPESA_ENVIRONMENT', default='sandbox')

    @classmethod
    def get_api_url(cls):
        if cls.mpesa_environment == 'production':
            return 'https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
        return 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'


def get_mpesa_access_token():
    """
    Fetches a fresh M-Pesa access token from Safaricom.
    Called lazily at request time — NOT at module import.
    """
    cred = MpesaC2bCredential
    r = requests.get(
        cred.get_api_url(),
        auth=HTTPBasicAuth(cred.consumer_key, cred.consumer_secret),
        timeout=10,
    )
    r.raise_for_status()
    return r.json()['access_token']


# Legacy class kept for backward compatibility with views that reference
# MpesaAccessToken.validated_mpesa_access_token. Prefer get_mpesa_access_token().
class MpesaAccessToken:
    @classmethod
    def get_token(cls):
        return get_mpesa_access_token()

    # Deprecated — calling this at class level is dangerous (runs at import).
    # Use get_mpesa_access_token() or MpesaAccessToken.get_token() instead.
    validated_mpesa_access_token = property(lambda self: get_mpesa_access_token())


class LipanaMpesaPpassword:
    lipa_time = datetime.now().strftime('%Y%m%d%H%M%S')
    Business_short_code = config('MPESA_SHORTCODE', default='174379')
    Test_c2b_shortcode = config('MPESA_EXPRESS_SHORTCODE', default='600344')
    passkey = config('MPESA_PASSKEY')

    data_to_encode = Business_short_code + passkey + lipa_time
    online_password = base64.b64encode(data_to_encode.encode())
    decode_password = online_password.decode('utf-8')