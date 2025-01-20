from django.utils.deprecation import MiddlewareMixin



  
class AllowIframeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['X-Frame-Options'] = 'ALLOW-FROM https://*.bigcommerce.com'
        response['Content-Security-Policy'] = "frame-ancestors 'self' https://*.bigcommerce.com"
        return response
    
