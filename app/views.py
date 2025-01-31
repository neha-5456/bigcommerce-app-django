from datetime import datetime
from django.shortcuts import render, redirect
from django.http import HttpResponse
import requests
from django.http import JsonResponse
import logging
import time
import jwt
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from .models import Store, User, StoreUser
from .utils import decode_and_verify_jwt
import json
from bigcommerce.api import BigcommerceApi





def index(request):
    # now = datetime.now()
    html = f'''
    <html>
        <body>
            <h1>Hello from Vercel!</h1>
            <p>The current time is jghjfhkf.</p>
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
# REDIRECT_URI = "https://bigcommerce-app-django.vercel.app/auth/callback/"
APP_URL = "https://bigcommerce-app-django.vercel.app"

# Step 1: Handle app installation

logger = logging.getLogger(__name__)

def install(request):
    code = request.GET.get('code')
    context = request.GET.get('context')
    scope = request.GET.get('scope')
    store_hash = context.split('/')[1]
    redirect_url = f"{APP_URL}{request.path}"

    # Initialize the BigCommerce API client
    client = BigcommerceApi(client_id=CLIENT_ID, store_hash=store_hash)
    
    # Fetch the OAuth token
    token = client.oauth_fetch_token(
        client_secret=CLIENT_SECRET,
        code=code,
        context=context,
        scope=scope,
        redirect_uri=redirect_url
    )

    bc_user_id = token['user']['id']
    email = token['user']['email']
    access_token = token['access_token']

    # Transaction to ensure database consistency
    with transaction.atomic():
        # Create or update the Store
        store, created = Store.objects.update_or_create(
            store_hash=store_hash,
            defaults={
                'access_token': access_token,
                'scope': scope
            }
        )

        # If the store existed, revoke the old admin
        if not created:
            StoreUser.objects.filter(store=store, admin=True).update(admin=False)

        # Create or update the User
        user, _ = User.objects.update_or_create(
            bc_id=bc_user_id,
            defaults={'email': email}
        )

        # Create or update the StoreUser
        store_user, _ = StoreUser.objects.update_or_create(
            store=store,
            user=user,
            defaults={'admin': True}
        )

    # Store the StoreUser ID in the session
    request.session['storeuserid'] = store_user.id

    # Redirect to the app home
    return redirect(APP_URL)



def create_script(store_hash, access_token, script_name):
    api_url = f"https://api.bigcommerce.com/stores/{store_hash}/v3/content/scripts"
    headers = {
        'X-Auth-Token': access_token,
        'Content-Type': 'application/json',
    }
    script_data = {
        "name": script_name,
        "description": "A custom script for the BigCommerce app.",
        "html": f"<script src='https://bigcommerce-app-django-9iyk.vercel.app/{script_name}'></script>",
        "auto_uninstall": True,
        "load_method": "default",
        "location": "footer",
        "visibility": "all_pages",
        "kind": "script_tag"
    }
    
    response = requests.post(api_url, headers=headers, json=script_data)
    
    if response.status_code == 200:
        script_info = response.json()
        logger.info(f"Script created successfully: {script_info['data']['name']}")
    else:
        logger.error(f"Failed to create script: {response.status_code} - {response.text}")


def load(request):
    # Extract the signed payload
    payload = request.GET.get('signed_payload_jwt')
    if not payload:
        return JsonResponse({"error": "Missing signed payload"}, status=400)

    try:
        # Decode and verify the JWT payload
        user_data = BigcommerceApi.oauth_verify_payload_jwt(
            payload,
            client_secret=CLIENT_SECRET,
            client_id=CLIENT_ID
        )
    except jwt.PyJWTError as e:
        return JsonResponse({"error": "Invalid JWT payload", "details": str(e)}, status=401)

    bc_user_id = user_data['user']['id']
    email = user_data['user']['email']
    store_hash = user_data['sub'].split('stores/')[1]

    # Lookup the store
    store = Store.objects.filter(store_hash=store_hash).first()
    if not store:
        return JsonResponse({"error": "Store not found!"}, status=401)

    # Lookup or create the user
    user, created = User.objects.get_or_create(
        bc_id=bc_user_id,
        defaults={'email': email}
    )

    # Lookup or create the StoreUser
    store_user, created = StoreUser.objects.get_or_create(
        store=store,
        user=user
    )

    # Store the StoreUser ID in the session
    request.session['storeuserid'] = store_user.id

    # Redirect to the app interface
    return redirect(APP_URL)


