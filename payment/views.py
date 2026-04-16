"""
payment/views.py

NOTE: The `payment` app is currently disabled (commented out of INSTALLED_APPS).
The primary M-Pesa flow is handled in `dashboard/views.py` via django-daraja.

This module retains utility views for:
  - Manual access token retrieval (admin/debugging)
  - C2B URL registration (run once per environment)
  - C2B callback/validation/confirmation stubs

All credentials are loaded from environment variables via .env — NO hardcoding.
"""

import json
import requests
import logging

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required

from .mpesa_credentials import MpesaC2bCredential, LipanaMpesaPpassword, get_mpesa_access_token

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Token utility (staff/admin only — NEVER expose publicly)
# ---------------------------------------------------------------------------

@staff_member_required
def getAccessToken(request):
    """
    Returns a fresh M-Pesa OAuth2 access token.
    IMPORTANT: Restricted to Django staff members only.
    Never expose this endpoint to the public internet.
    """
    try:
        token = get_mpesa_access_token()
        # Return as JSON to avoid browser autosave of raw token strings
        return JsonResponse({"access_token": token})
    except Exception as e:
        logger.error(f"Failed to get M-Pesa access token: {e}")
        return JsonResponse({"error": "Failed to retrieve access token."}, status=500)


# ---------------------------------------------------------------------------
# STK Push (legacy — main flow is in dashboard/views.py via django-daraja)
# ---------------------------------------------------------------------------

def lipa_na_mpesa_online(request):
    """
    Initiates an M-Pesa STK Push (Lipa Na M-Pesa Online).
    Prefer using the dashboard/views.py wallet view which uses django-daraja.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    try:
        data = json.loads(request.body)
        phone_number = data.get("phone")
        amount = data.get("amount")

        access_token = get_mpesa_access_token()
        env = MpesaC2bCredential.mpesa_environment
        if env == 'production':
            api_url = "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        else:
            api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

        headers = {"Authorization": f"Bearer {access_token}"}
        request_payload = {
            "BusinessShortCode": LipanaMpesaPpassword.Business_short_code,
            "Password": LipanaMpesaPpassword.decode_password,
            "Timestamp": LipanaMpesaPpassword.lipa_time,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone_number,
            "PartyB": LipanaMpesaPpassword.Business_short_code,
            "PhoneNumber": phone_number,
            "CallBackURL": "https://www.smrtmine.com/dashboard/api/mpesa/callback/",
            "AccountReference": "SmartMine",
            "TransactionDesc": "Investment/Deposit Payment",
        }
        response = requests.post(api_url, json=request_payload, headers=headers, timeout=30)
        return JsonResponse(response.json())
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)
    except Exception as e:
        logger.error(f"STK Push error: {e}")
        return JsonResponse({"error": str(e)}, status=500)


# ---------------------------------------------------------------------------
# C2B URL Registration (run once when setting up the shortcode)
# ---------------------------------------------------------------------------

@csrf_exempt
def register_urls(request):
    """
    Registers C2B confirmation/validation URLs with Safaricom.
    Run this once per environment setup via: GET /payment/register-urls/
    """
    try:
        access_token = get_mpesa_access_token()
        env = MpesaC2bCredential.mpesa_environment
        if env == 'production':
            api_url = "https://api.safaricom.co.ke/mpesa/c2b/v1/registerurl"
            base_url = "https://www.smrtmine.com"
        else:
            api_url = "https://sandbox.safaricom.co.ke/mpesa/c2b/v1/registerurl"
            base_url = "https://www.smrtmine.com"  # Replace with ngrok URL during local sandbox testing

        headers = {"Authorization": f"Bearer {access_token}"}
        options = {
            "ShortCode": LipanaMpesaPpassword.Test_c2b_shortcode,
            "ResponseType": "Completed",
            "ConfirmationURL": f"{base_url}/payment/c2b/confirmation/",
            "CallbackURL": f"{base_url}/payment/c2b/callback/",
            "ValidationURL": f"{base_url}/payment/c2b/validation/",
        }
        response = requests.post(api_url, json=options, headers=headers, timeout=30)
        return HttpResponse(response.text)
    except Exception as e:
        logger.error(f"register_urls error: {e}")
        return HttpResponse(f"Error: {e}", status=500)


# ---------------------------------------------------------------------------
# C2B Callbacks (Safaricom will POST to these when payments come in)
# ---------------------------------------------------------------------------

@csrf_exempt
def call_back(request):
    """Generic C2B callback placeholder. Implement as needed."""
    logger.info(f"C2B callback received: {request.body}")
    return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})


@csrf_exempt
def validation(request):
    """C2B validation endpoint — Safaricom checks before processing payment."""
    return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})


@csrf_exempt
def confirmation(request):
    """
    C2B confirmation endpoint — called after a successful payment.
    Logs the transaction for audit. Wallet crediting is handled in dashboard/views.py.
    """
    try:
        mpesa_body = request.body.decode('utf-8')
        mpesa_payment = json.loads(mpesa_body)
        logger.info(
            f"C2B confirmation received: TransID={mpesa_payment.get('TransID')}, "
            f"Amount={mpesa_payment.get('TransAmount')}, Phone={mpesa_payment.get('MSISDN')}"
        )
        return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})
    except Exception as e:
        logger.error(f"C2B confirmation error: {e}")
        return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})
