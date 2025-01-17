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
    
    try:
        # Extract query parameters
        code = request.GET.get("code")
        context = request.GET.get("context")
        scope = request.GET.get("scope")

        if not code or not context or not scope:
            return JsonResponse({"error": "Missing required query parameters"}, status=400)

        store_hash = context.split("/")[-1]
        redirect_uri = REDIRECT_URI 

        # Request OAuth token from BigCommerce
        token_url = "https://login.bigcommerce.com/oauth2/token"
        payload = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": code,
            "context": context,
            "scope": scope,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
        }

        response = requests.post(token_url, json=payload)
        print(response)
        if response.status_code != 200:
            logger.error(f"Failed to fetch token: {response.json()}")
            return JsonResponse({"error": "Failed to fetch token", "details": response.json()}, status=400)

        token_data = response.json()
        bc_user_id = token_data["user"]["id"]
        email = token_data["user"]["email"]
        access_token = token_data["access_token"]

        # Transaction to ensure data consistency
        with transaction.atomic():
            # Create or update store
            store, created = Store.objects.get_or_create(
                store_hash=store_hash,
                defaults={"access_token": access_token, "scope": scope},
            )
            if not created:
                store.access_token = access_token
                store.scope = scope
                store.save()

                # Reset admin status for the old admin
                StoreUser.objects.filter(store=store, admin=True).update(admin=False)

            # Create or update user
            user, user_created = User.objects.get_or_create(
                bc_id=bc_user_id, defaults={"email": email}
            )
            if not user_created and user.email != email:
                user.email = email
                user.save()

            # Create or update store user
            store_user, store_user_created = StoreUser.objects.get_or_create(
                store=store,
                user=user,
                defaults={"admin": True},
            )
            if not store_user_created:
                store_user.admin = True
                store_user.save()
        logger.info(f"OAuth payload: {payload}")
        logger.info(f"BigCommerce token URL: {token_url}")
        logger.info(f"BigCommerce response status: {response.status_code}")
        logger.info(f"BigCommerce response content: {response.content}")
        # Log user in and redirect
        request.session["store_user_id"] = store_user.id
        bigcommerce_dashboard_url = f"https://store-0sl32ohrbq.mybigcommerce.com/manage/app"
        return redirect(bigcommerce_dashboard_url)

    except Exception as e:
        logger.error(f"Error in auth_callback: {str(e)}")
        return JsonResponse({"error": "An error occurred during authentication"}, status=500)
    # # Prepare the payload
    # payload = {
    #     "client_id": CLIENT_ID,
    #     "client_secret": CLIENT_SECRET,
    #     "redirect_uri": REDIRECT_URI,
    #     "grant_type": "authorization_code",
    #     "code": request.GET.get("code"),
    #     "scope": request.GET.get("scope"),
    #     "context": request.GET.get("context"),
    # }

    # # BigCommerce OAuth2 token URL
    # token_url = "https://login.bigcommerce.com/oauth2/token"

    # # Retry logic
    # for attempt in range(3):  # Retry 3 times
    #     try:
    #         response = requests.post(token_url, json=payload, timeout=30)
    #         if response.status_code == 200:
    #             break
    #     except requests.exceptions.RequestException as e:
    #         logger.error(f"Error on attempt {attempt + 1}: {str(e)}")
    #         if attempt == 2:  # Last attempt
    #             return JsonResponse({"error": "Failed to obtain token after retries."}, status=504)
    #         time.sleep(5)  # Wait 5 seconds before retrying

    # if response.status_code == 200:
    #     # Handle successful response
    #     data = response.json()
    #     context = data.get("context")
    #     store_hash = context.split("/")[-1]
    #     access_token = data.get("access_token")
    #     user_email = data.get("user", {}).get("email")
    #     create_script(store_hash, access_token, "app.js")
    #     # Check if the store_hash already exists in the database
    #     try:
    #         # Try to get the existing record
    #         store_data = StoreData.objects.get(store_hash=store_hash)
    #         # If found, update the access token
    #         store_data.access_token = access_token
    #         store_data.user_email = user_email
    #         store_data.save()
    #         logger.info(f"Updated access token for store {store_hash}.")
    #     except StoreData.DoesNotExist:
    #         # If not found, create a new record
    #         store_data = StoreData(store_hash=store_hash, access_token=access_token, user_email=user_email)
    #         store_data.save()
    #         logger.info(f"New store data added for {store_hash}.")
        
    #     # Create script or perform additional actions
    #     # create_script(store_hash, access_token, "app.js")
        
    #     # Redirect to BigCommerce dashboard
    #     bigcommerce_dashboard_url = f"https://store-0sl32ohrbq.mybigcommerce.com/manage/app"
    #     return redirect(bigcommerce_dashboard_url)

    # else:
    #     # Handle API error
    #     error_message = response.json()
    #     logger.error(f"Error obtaining OAuth2 token: {error_message}")
    #     return JsonResponse({"error": "Authorization failed", "details": error_message}, status=response.status_code)



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
    try:
        # Decode and verify payload
        payload = request.GET.get("signed_payload_jwt")
        if not payload:
            return JsonResponse({"error": "Missing signed_payload_jwt"}, status=400)

        try:
            user_data = decode_and_verify_jwt(payload, CLIENT_SECRET, CLIENT_ID)
        except Exception as e:
            logger.error(f"JWT verification error: {str(e)}")
            return JsonResponse({"error": "Invalid JWT"}, status=401)

        bc_user_id = user_data["user"]["id"]
        email = user_data["user"]["email"]
        store_hash = user_data["sub"].split("stores/")[1]

        # Lookup store
        try:
            store = Store.objects.get(store_hash=store_hash)
        except Store.DoesNotExist:
            return JsonResponse({"error": "Store not found"}, status=401)

        # Lookup user and create if doesn't exist
        user, user_created = User.objects.get_or_create(
            bc_id=bc_user_id,
            defaults={"email": email}
        )
        if not user_created and user.email != email:
            user.email = email
            user.save()

        # Lookup store user and create if doesn't exist
        with transaction.atomic():
            store_user, store_user_created = StoreUser.objects.get_or_create(
                user=user, store=store
            )

        # Log user in
        request.session["store_user_id"] = store_user.id

        # Redirect to app interface
        return redirect(REDIRECT_URI)

    except Exception as e:
        logger.error(f"Error in load function: {str(e)}")
        return JsonResponse({"error": "An error occurred", "details": str(e)}, status=500)
    
    
    
    # signed_payload_jwt = request.GET.get('signed_payload_jwt')
    
    # if not signed_payload_jwt:
    #     return JsonResponse({'error': 'Missing signed_payload_jwt'}, status=400)

    # try:
    #     # Decode the JWT with HS256 (assuming BigCommerce uses HS256)
    #     payload = jwt.decode(
    #         signed_payload_jwt,
    #         CLIENT_SECRET,  # Ensure your CLIENT_SECRET is correctly set in settings.py
    #         algorithms=['0sl32ohrbq'],
    #         audience=CLIENT_ID,  # Ensure CLIENT_ID is set in settings.py
    #     )
    # except jwt.ExpiredSignatureError:
    #     return JsonResponse({'error': 'Token has expired'}, status=401)
    # except jwt.InvalidTokenError as e:
    #     return JsonResponse({'error': f'Invalid token: {str(e)}'}, status=401)

    # # Extract user and store information
    # user_data = payload.get('user', {})
    # store_hash = payload.get('sub', '').split('stores/')[1]

    # # Display HTML content with store and user info
    # now = datetime.now()
    # html = f'''
    # <html>
    #     <body>
    #         <h1>Hello from Vercel!</h1>
    #         <p>The current time is {now}.</p>
    #         <h2>User Info:</h2>
    #         <p>Email: {user_data.get("email", "Unknown")}</p>
    #         <h2>Store Info:</h2>
    #         <p>Store Hash: {store_hash}</p>
    #     </body>
    # </html>
    # '''
    # return HttpResponse(html)