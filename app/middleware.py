from django.utils.deprecation import MiddlewareMixin

class AllowIframeMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        # Set Content Security Policy to allow BigCommerce domains
        response["Content-Security-Policy"] = "frame-ancestors 'self' https://*.bigcommerce.com"
        
        # Optionally remove X-Frame-Options if conflicting
        if "X-Frame-Options" in response:
            del response["X-Frame-Options"]
        
        return response
