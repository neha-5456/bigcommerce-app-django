from datetime import datetime
from django.shortcuts import render, redirect
from django.http import HttpResponse
import requests
from django.http import JsonResponse
import logging
from .models import StoreData
from django.db import IntegrityError

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

def install(request):
    # Step 1: Prepare the payload for token exchange
    payload = {
        "client_id": CLIENT_ID,  # Replace with your environment variable or config
        "client_secret":CLIENT_SECRET,
        "redirect_uri":REDIRECT_URI,  # Replace with your environment variable or config
        "grant_type": "authorization_code",
        "code": request.GET.get("code"),
        "scope": request.GET.get("scope"),
        "context": request.GET.get("context"),
    }

    # Step 2: Send a POST request to BigCommerce OAuth2 endpoint
    token_url = "https://login.bigcommerce.com/oauth2/token"
    response = requests.post(token_url, json=payload)

    if response.status_code == 200:
        # Step 3: Handle successful token response
        data = response.json()

        # Extract necessary data
        context = data.get("context")
        store_hash = context.split("/")[-1]  # Get store hash from context
        access_token = data.get("access_token")
        user_email = data.get("user", {}).get("email")
        
        
        # try:
        #     record = StoreData(store_hash=store_hash, access_token=access_token, user_email=user_email)
        #     record.save()
        #     logger.info(f"Store data saved: {store_hash}")
        # except Exception as e:  # Catching all exceptions to log the error
        #     logger.error(f"Error saving store data: {str(e)}")
        #     return JsonResponse({"error": "Failed to save store data."}, status=500)
        
        
        # Step 4: Call create_script to register the app script
        create_script(store_hash, access_token, "app.js")

        # Respond with success message or redirect to a success page
        return JsonResponse({"message": "App installed successfully", "store_hash": store_hash, "email": user_email, "access token": access_token, "data":data})

    else:
        # Step 5: Handle errors
        error_message = response.json()
        logger.error(f"Error obtaining OAuth2 token: {error_message}")
        return JsonResponse({"error": "Authorization failed", "details": error_message}, status=response.status_code)

def create_script(store_hash, access_token, script_name):
    # Step 6: Register a script with BigCommerce API
    script_url = f"https://api.bigcommerce.com/stores/{store_hash}/v3/content/scripts"
    headers = {
        "X-Auth-Token": access_token,
        "Content-Type": "application/json",
    }

    payload = {
        "name": script_name,
        "description": "A custom script for the BigCommerce app.",
        "html": "<script src='https://example.com/static/app.js'></script>",
        "auto_uninstall": True,
        "load_method": "default",
        "location": "footer",
        "visibility": "all",
        "kind": "script_tag",
    }

    response = requests.post(script_url, json=payload, headers=headers)

    if response.status_code == 201:
        logger.info("Script successfully registered")
    else:
        logger.error(f"Failed to create script: {response.text}")

