import requests
import base64
from datetime import datetime

# M-Pesa API credentials
CONSUMER_KEY = 'Y8RDO3rtdjW2mk7qp4pGlfxGAIpYIYz7nWUb4HNifiYLwL3i'
CONSUMER_SECRET = 'VKhpK8wIuhDQxXGhrFoWk9W4mrL3SZ1Kch39ZTS9kjlxTFnlKpz5NcrdlWKzaQOZ'
LIPA_NA_MPESA_PASSKEY = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
SHORTCODE = '174379'  # Lipa Na M-Pesa Shortcode
CALLBACK_URL = 'https://yourdomain.com/callback'  # Callback URL for payment confirmation

# Generate access token
def get_access_token():
    url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    auth = base64.b64encode(f"{CONSUMER_KEY}:{CONSUMER_SECRET}".encode()).decode()
    headers = {'Authorization': f'Basic {auth}'}
    response = requests.get(url, headers=headers)
    return response.json().get('access_token')

# Initiate STK Push
def initiate_stk_push(phone, amount, account_reference, transaction_desc):
    access_token = get_access_token()
    url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password = base64.b64encode(f"{SHORTCODE}{LIPA_NA_MPESA_PASSKEY}{timestamp}".encode()).decode()
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    payload = {
        "BusinessShortCode": SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone,
        "PartyB": SHORTCODE,
        "PhoneNumber": phone,
        "CallBackURL": CALLBACK_URL,
        "AccountReference": f"Unirent Booking {account_reference}", 
        "TransactionDesc": f"Payment for {transaction_desc}. Thank you for choosing Unirent!",
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()