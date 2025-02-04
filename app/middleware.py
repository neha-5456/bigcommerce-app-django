from django.http import HttpResponse

class CSPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Add Content-Security-Policy header to allow BigCommerce embedding
        response['Content-Security-Policy'] = "frame-ancestors 'self' https://*.bigcommerce.com;"
        
        return response