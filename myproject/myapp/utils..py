from django.http import HttpRequest

def get_client_ip(request: HttpRequest):
    """Get the IP address of the client making the request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]  # Get the first IP in the list
    else:
        ip = request.META.get('REMOTE_ADDR')  # Default IP
    return ip
