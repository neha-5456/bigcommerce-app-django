from datetime import datetime
from django.shortcuts import render
from django.http import HttpResponse
import requests
from django.shortcuts import redirect
from django.conf import settings

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


# def bigcommerce_auth(request):
#     """Redirect users to the BigCommerce OAuth URL."""
#     client_id = settings.BIGCOMMERCE['client_id']
#     auth_callback_url = settings.BIGCOMMERCE['auth_callback_url']
#     url = f"https://login.bigcommerce.com/oauth2/authorize?client_id={client_id}&redirect_uri={auth_callback_url}&scope=store_v2_products&response_type=code"
#     return redirect(url)

# def auth_callback(request):
#     """Handle BigCommerce OAuth callback."""
#     code = request.GET.get('code')
#     client_id = settings.BIGCOMMERCE['client_id']
#     client_secret = settings.BIGCOMMERCE['client_secret']
#     redirect_uri = settings.BIGCOMMERCE['auth_callback_url']
    
#     payload = {
#         'client_id': client_id,
#         'client_secret': client_secret,
#         'code': code,
#         'grant_type': 'authorization_code',
#         'redirect_uri': redirect_uri,
#     }

#     response = requests.post("https://login.bigcommerce.com/oauth2/token", json=payload)
#     data = response.json()

#     # Save tokens (e.g., in the database or Django cache)
#     access_token = data.get('access_token')
#     context = {'access_token': access_token}
#     return render(request, 'auth_callback.html', context)


# def products(request):
#     """Fetch products from BigCommerce."""
#     store_hash = settings.BIGCOMMERCE['store_hash']
#     access_token = settings.BIGCOMMERCE['access_token']
    
#     headers = {
#         'X-Auth-Token': access_token,
#         'Content-Type': 'application/json',
#     }

#     url = f"https://api.bigcommerce.com/stores/{store_hash}/v3/catalog/products"
#     response = requests.get(url, headers=headers)
#     products = response.json()

#     return render(request, 'products.html', {'products': products})
