from django.http import HttpResponse
import requests
from requests.auth import HTTPBasicAuth
import json
from . mpesa_credentials import MpesaAccessToken, LipanaMpesaPpassword
from django.views.decorators.csrf import csrf_exempt


def getAccessToken(request):
    consumer_key = 'cHnkwYIgBbrxlgBoneczmIJFXVm0oHky'
    consumer_secret = '2nHEyWSD4VjpNh2g'
    api_URL = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'

    r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    mpesa_access_token = json.loads(r.text)
    validated_mpesa_access_token = mpesa_access_token['access_token']

    return HttpResponse(validated_mpesa_access_token)


def lipa_na_mpesa_online(request):
    if request.method == "POST":
        data = json.loads(request.body)  # Get data from frontend
        phone_number = data.get("phone")  # Get phone number from request
        amount = data.get("amount")  # Get amount from request

        access_token = MpesaAccessToken.validated_mpesa_access_token
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
            "CallBackURL": "https://yourdomain.com/mpesa/callback/",
            "AccountReference": "Payment",
            "TransactionDesc": "MPESA Payment"
        }
        response = requests.post(api_url, json=request_payload, headers=headers)
        return JsonResponse(response.json())  # Send response back to frontend
    return JsonResponse({"error": "Invalid request"}, status=400)

# def lipa_na_mpesa_online(request):
#     if request.method == "POST":
#         phone = request.POST('phone')
#         amount = request.POST('amount')
#     access_token = MpesaAccessToken.validated_mpesa_access_token
#     api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
#     headers = {"Authorization": "Bearer %s" % access_token}
#     request = {
#         "BusinessShortCode": LipanaMpesaPpassword.Business_short_code,
#         "Password": LipanaMpesaPpassword.decode_password,
#         "Timestamp": LipanaMpesaPpassword.lipa_time,
#         "TransactionType": "CustomerPayBillOnline",
#         "Amount": int(amount),
#         "PartyA": phone,  # replace with your phone number to get stk push
#         "PartyB": LipanaMpesaPpassword.Business_short_code,
#         "PhoneNumber": phone,  # replace with your phone number to get stk push
#         "CallBackURL": "https://sandbox.safaricom.co.ke/mpesa/",
#         "AccountReference": "smartmine",
#         "TransactionDesc": "Testing stk push"
#     }

#     response = requests.post(api_url, json=request, headers=headers)
#     return HttpResponse('success')

@csrf_exempt
def register_urls(request):
    access_token = MpesaAccessToken.validated_mpesa_access_token
    api_url = "https://sandbox.safaricom.co.ke/mpesa/c2b/v1/registerurl"
    headers = {"Authorization": "Bearer %s" % access_token}
    options = {"ShortCode": LipanaMpesaPpassword.Test_c2b_shortcode,
                "ResponseType": "Completed",
                "ConfirmationURL":"https://8884-105-160-2-61.ngrok-free.app/api/v1/c2b/confirmation",
                "CallbackURL":"https://8884-105-160-2-61.ngrok-free.app/api/v1/c2b/callback",
                "ValidationURL": "https://8884-105-160-2-61.ngrok-free.app/api/v1/c2b/validation"}
    response = requests.post(api_url, json=options, headers=headers)
    return HttpResponse(response.text)

'''
@csrf_exempt
def register_urls(request):
    access_token = MpesaAccessToken.validated_mpesa_access_token
    api_url = "https://sandbox.safaricom.co.ke/mpesa/c2b/v1/registerurl"
    headers = {"Authorization": "Bearer %s" % access_token}
    options = {"ShortCode": LipanaMpesaPpassword.Business_short_code,
               "ResponseType": "Completed",
               "ConfirmationURL": "https://8884-105-160-2-61.ngrok-free.app/api/v1/c2b/confirmation",
               "ValidationURL": "https://8884-105-160-2-61.ngrok-free.app/api/v1/c2b/validation"}
    response = requests.post(api_url, json=options, headers=headers)

    return HttpResponse(response.text)

'''
@csrf_exempt
def call_back(request):
    pass


@csrf_exempt
def validation(request):

    context = {
        "ResultCode": 0,
        "ResultDesc": "Accepted"
    }
    return JsonResponse(dict(context))


@csrf_exempt
def confirmation(request):
    mpesa_body =request.body.decode('utf-8')
    mpesa_payment = json.loads(mpesa_body)

    payment = MpesaPayment(
        first_name=mpesa_payment['FirstName'],
        last_name=mpesa_payment['LastName'],
        middle_name=mpesa_payment['MiddleName'],
        description=mpesa_payment['TransID'],
        phone_number=mpesa_payment['MSISDN'],
        amount=mpesa_payment['TransAmount'],
        reference=mpesa_payment['BillRefNumber'],
        organization_balance=mpesa_payment['OrgAccountBalance'],
        type=mpesa_payment['TransactionType'],

    )
    payment.save()

    context = {
        "ResultCode": 0,
        "ResultDesc": "Accepted"
    }

    return JsonResponse(dict(context))
    #

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import MpesaTransaction

def extract_metadata(metadata_items):
    metadata = {}
    for item in metadata_items:
        metadata[item["Name"]] = item.get("Value", None)
    return metadata

@csrf_exempt
def mpesa_callback(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            callback = data.get("Body", {}).get("stkCallback", {})
            
            merchant_request_id = callback.get("MerchantRequestID")
            checkout_request_id = callback.get("CheckoutRequestID")
            result_code = callback.get("ResultCode")
            result_desc = callback.get("ResultDesc")
            
            if result_code == 0:  # Successful transaction
                callback_metadata = callback.get("CallbackMetadata", {}).get("Item", [])
                metadata = extract_metadata(callback_metadata)
                
                MpesaTransaction.objects.create(
                    merchant_request_id=merchant_request_id,
                    checkout_request_id=checkout_request_id,
                    result_code=result_code,
                    result_desc=result_desc,
                    amount=metadata.get("Amount"),
                    mpesa_receipt_number=metadata.get("MpesaReceiptNumber"),
                    balance=metadata.get("Balance"),
                    transaction_date=metadata.get("TransactionDate"),
                    phone_number=metadata.get("PhoneNumber"),
                )
                return JsonResponse({"message": "Transaction saved successfully"}, status=201)
            else:
                # Log the failed transaction attempt
                return JsonResponse({"message": "Transaction failed", "error": result_desc}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"message": "Internal Server Error", "error": str(e)}, status=500)
    
    return JsonResponse({"message": "Method not allowed"}, status=405)
