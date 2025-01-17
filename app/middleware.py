from django.utils.deprecation import MiddlewareMixin

class AllowIframeMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        # Set Content Security Policy to allow BigCommerce domains
        response["Content-Security-Policy"] = "frame-ancestors 'self' https://*.bigcommerce.com"
        return response


  
