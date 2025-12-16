# checkout/mpesa.py
import os
import base64
import requests
import re
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# M-Pesa Configuration from .env
MPESA_CONSUMER_KEY = os.getenv('MPESA_CONSUMER_KEY')
MPESA_CONSUMER_SECRET = os.getenv('MPESA_CONSUMER_SECRET')
MPESA_PASSKEY = os.getenv('MPESA_PASSKEY')
MPESA_SHORTCODE = os.getenv('MPESA_SHORTCODE')
MPESA_CALLBACK_URL = os.getenv('MPESA_CALLBACK_URL')
MPESA_BASE_URL = os.getenv('MPESA_BASE_URL', 'https://sandbox.safaricom.co.ke').rstrip('/')

# Validate required env vars
if not all([MPESA_CONSUMER_KEY, MPESA_CONSUMER_SECRET, MPESA_PASSKEY, MPESA_SHORTCODE, MPESA_CALLBACK_URL]):
    raise ValueError("Missing required M-Pesa environment variables in .env")

def format_phone_number(phone: str) -> str:
    """Convert to 254XXXXXXXXX format"""
    phone = re.sub(r"[^\d]", "", phone.strip())
    if phone.startswith("254") and len(phone) == 12:
        return phone
    elif phone.startswith("0") and len(phone) == 10:
        return "254" + phone[1:]
    elif phone.startswith("7") and len(phone) == 9:
        return "254" + phone
    else:
        raise ValueError("Invalid phone number. Use 07xx, 7xx, or 2547xx format.")

def get_access_token() -> str:
    """Get OAuth access token with detailed error reporting"""
    if not MPESA_CONSUMER_KEY or not MPESA_CONSUMER_SECRET:
        raise ValueError("MPESA_CONSUMER_KEY or MPESA_CONSUMER_SECRET missing")

    auth_str = f"{MPESA_CONSUMER_KEY}:{MPESA_CONSUMER_SECRET}"
    encoded_auth = base64.b64encode(auth_str.encode()).decode()

    headers = {
        "Authorization": f"Basic {encoded_auth}",
        "Content-Type": "application/json"
    }
    url = f"{MPESA_BASE_URL}/oauth/v1/generate?grant_type=client_credentials"

    print(f"[MPESA] Requesting token from: {url}")
    try:
        response = requests.get(url, headers=headers, timeout=15)
        print(f"[MPESA] Token response status: {response.status_code}")
        print(f"[MPESA] Token response body: {response.text}")

        if response.status_code == 200:
            data = response.json()
            if "access_token" in data:
                return data["access_token"]
            else:
                raise Exception(f"Access token missing in response: {data}")
        else:
            raise Exception(f"HTTP {response.status_code}: {response.text}")

    except requests.exceptions.Timeout:
        raise Exception("Timeout while getting access token")
    except requests.exceptions.ConnectionError:
        raise Exception("Connection error - check internet or M-Pesa sandbox status")
    except Exception as e:
        raise Exception(f"Failed to get access token: {str(e)}")

def initiate_stk_push(phone_number: str, amount: int):
    """Initiate STK Push with full debugging"""
    try:
        phone = format_phone_number(phone_number)
        token = get_access_token()

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        password = base64.b64encode(f"{MPESA_SHORTCODE}{MPESA_PASSKEY}{timestamp}".encode()).decode()

        payload = {
            "BusinessShortCode": MPESA_SHORTCODE,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone,
            "PartyB": MPESA_SHORTCODE,
            "PhoneNumber": phone,
            "CallBackURL": MPESA_CALLBACK_URL,
            "AccountReference": "ARIFARM",
            "TransactionDesc": "Payment for order on Arifarm",
        }

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        url = f"{MPESA_BASE_URL}/mpesa/stkpush/v1/processrequest"
        print(f"[MPESA] Sending STK Push to {phone} for KSh {amount}")
        print(f"[MPESA] Payload: {payload}")

        response = requests.post(url, json=payload, headers=headers, timeout=20)
        print(f"[MPESA] STK Push response: {response.status_code} - {response.text}")

        return response.json()

    except Exception as e:
        print(f"[MPESA ERROR] STK Push failed: {str(e)}")
        raise

def query_stk_push(checkout_request_id: str):
    """Query STK Push status with debugging"""
    try:
        token = get_access_token()
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        password = base64.b64encode(f"{MPESA_SHORTCODE}{MPESA_PASSKEY}{timestamp}".encode()).decode()

        payload = {
            "BusinessShortCode": MPESA_SHORTCODE,
            "Password": password,
            "Timestamp": timestamp,
            "CheckoutRequestID": checkout_request_id
        }

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        url = f"{MPESA_BASE_URL}/mpesa/stkpushquery/v1/query"
        print(f"[MPESA] Querying status for CheckoutRequestID: {checkout_request_id}")

        response = requests.post(url, json=payload, headers=headers, timeout=20)
        print(f"[MPESA] Query response: {response.status_code} - {response.text}")

        return response.json()

    except Exception as e:
        print(f"[MPESA ERROR] Query failed: {str(e)}")
        raise