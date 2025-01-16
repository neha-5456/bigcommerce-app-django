from datetime import datetime
from django.shortcuts import render, redirect
from django.http import HttpResponse
import requests
from django.http import JsonResponse
import logging
from .models import StoreData
# import IntegrityError
import time
import hmac
import hashlib
import base64
import json
from django.views.decorators.csrf import csrf_exempt


def index(request):
    now = datetime.now()
    html = f'''
    <html>
        <body>
            <h1>Hello from Vercel!</h1>
            <p>The current time is { now }.</p>
        </body>
    </html>
    '''
    return HttpResponse(html)

def test(request):
    return render(request, 'index.html')

# ACCESS TOKEN: qw057iqufn4b9wzr6jk7rn2jqtmqher
# CLIENT NAME: python custom widgest app
# CLIENT ID: 7k8045hpi7yytidpf6tzuzz8t10o3i2
# CLIENT SECRET: edf5b63b03b4e3eef72a4bca6ce41bc983c460661d4033ba49588304ea404188
# NAME: python custom widgest app
# API PATH: https://api.bigcommerce.com/stores/0sl32ohrbq/v3/


CLIENT_ID = 'n52tn8ffugohj3n6w9ybda12laoc7r'
CLIENT_SECRET = 'd4d1cc283a571aecb7793f8b6e80f1d3c37eb45740af0dcc7617cbc43a6ad3bc'
REDIRECT_URI = "https://bigcommerce-app-django-9iyk.vercel.app/auth/callback/"

# Step 1: Handle app installation




logger = logging.getLogger(__name__)
from django.db import IntegrityError

def install(request):
    # Prepare the payload
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
        "code": request.GET.get("code"),
        "scope": request.GET.get("scope"),
        "context": request.GET.get("context"),
    }

    # BigCommerce OAuth2 token URL
    token_url = "https://login.bigcommerce.com/oauth2/token"

    # Retry logic
    for attempt in range(3):  # Retry 3 times
        try:
            response = requests.post(token_url, json=payload, timeout=30)
            if response.status_code == 200:
                break
        except requests.exceptions.RequestException as e:
            logger.error(f"Error on attempt {attempt + 1}: {str(e)}")
            if attempt == 2:  # Last attempt
                return JsonResponse({"error": "Failed to obtain token after retries."}, status=504)
            time.sleep(5)  # Wait 5 seconds before retrying

    if response.status_code == 200:
        # Handle successful response
        data = response.json()
        context = data.get("context")
        store_hash = context.split("/")[-1]
        access_token = data.get("access_token")
        user_email = data.get("user", {}).get("email")

        # Check if the store_hash already exists in the database
        try:
            # Try to get the existing record
            store_data = StoreData.objects.get(store_hash=store_hash)
            # If found, update the access token
            store_data.access_token = access_token
            store_data.user_email = user_email
            store_data.save()
            logger.info(f"Updated access token for store {store_hash}.")
        except StoreData.DoesNotExist:
            # If not found, create a new record
            store_data = StoreData(store_hash=store_hash, access_token=access_token, user_email=user_email)
            store_data.save()
            logger.info(f"New store data added for {store_hash}.")
        
        # Create script or perform additional actions
        # create_script(store_hash, access_token, "app.js")
        
        # Redirect to BigCommerce dashboard
        bigcommerce_dashboard_url = f"https://store-0sl32ohrbq.mybigcommerce.com/manage/app"
        return redirect(bigcommerce_dashboard_url)

    else:
        # Handle API error
        error_message = response.json()
        logger.error(f"Error obtaining OAuth2 token: {error_message}")
        return JsonResponse({"error": "Authorization failed", "details": error_message}, status=response.status_code)






def verify_signed_payload(signed_payload):
    encoded_json, encoded_signature = signed_payload.split(".")
    decoded_json = base64.b64decode(encoded_json + "==")
    decoded_signature = base64.b64decode(encoded_signature + "==")

    expected_signature = hmac.new(
        CLIENT_SECRET.encode(), encoded_json.encode(), hashlib.sha256
    ).digest()

    if hmac.compare_digest(decoded_signature, expected_signature):
        return json.loads(decoded_json)
    else:
        return None

@csrf_exempt
def load(request):
    return render(request, "load.html", {"store_hash": request.GET.get("store_hash")})
