from datetime import datetime
from django.shortcuts import render, redirect
from django.http import HttpResponse
import requests
from django.http import JsonResponse

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


CLIENT_ID = '7k8045hpi7yytidpf6tzuzz8t10o3i2'
CLIENT_SECRET = 'edf5b63b03b4e3eef72a4bca6ce41bc983c460661d4033ba49588304ea404188'
REDIRECT_URI = "https://bigcommerce-app-django-9iyk.vercel.app/auth/callback/"

# Step 1: Handle app installation
def install(request):
    install_url = request.GET.get('install_url')
    return redirect(f"{install_url}?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}")

# Step 2: Handle OAuth callback
def auth_callback(request):
    
    code = request.GET.get('code')
    scope = request.GET.get('scope')
    context = request.GET.get('context')

    token_url = "https://login.bigcommerce.com/oauth2/token"
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
        "code": code,
        "scope": scope,
        "context": context,
    }

    response = requests.post(token_url, json=payload)
    if response.status_code == 200:
        data = response.json()
        # Save access token, store hash, and user details in your database
        return JsonResponse(data)
    else:
        return JsonResponse({"error": "Authorization failed"}, status=400)
    
def custom_tab(request):
    access_token = "qw057iqufn4b9wzr6jk7rn2jqtmqher"
    store_hash = "0sl32ohrbq"

    headers = {
        "X-Auth-Token": access_token,
        "Content-Type": "application/json"
    }

    product_url = f"https://api.bigcommerce.com/stores/{store_hash}/v3/catalog/products"
    response = requests.get(product_url, headers=headers)

    if response.status_code == 200:
        products = response.json()
        return JsonResponse({"products": products})
    else:
        return JsonResponse({"error": "Failed to fetch products"}, status=400)
