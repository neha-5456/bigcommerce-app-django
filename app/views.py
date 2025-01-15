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
    redirect_url = f"?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope=read_orders write_orders&response_type=code"
    return redirect(redirect_url)
    

def auth_callback(request):
    code = request.GET.get('code')
    if not code:
        return JsonResponse({"error": "Authorization code is missing"}, status=400)

    # Exchange code for access token
    token_url = "https://login.bigcommerce.com/oauth2/token"
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
        "code": code,
    }

    response = requests.post(token_url, json=payload)
    if response.status_code == 200:
        data = response.json()
        # Store access token in your database
        # Redirect to a success page or dashboard (NOT to the install page again)
        return JsonResponse(data)
    else:
        print(response.text)  # Debugging
        return JsonResponse({"error": "Authorization failed", "details": response.text}, status=400)


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
