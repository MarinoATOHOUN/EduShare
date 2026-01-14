from .utils_tracking import record_user_activity

class UserActivityMiddleware:
    """Middleware to track user activity on every request"""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Process request
        response = self.get_response(request)
        
        # After response is generated, record activity if user is authenticated
        # We do it after to ensure authentication middleware has run
        if hasattr(request, 'user') and request.user.is_authenticated:
            try:
                record_user_activity(request.user, request)
            except Exception as e:
                # Don't let tracking errors break the application
                print(f"Error recording user activity: {e}")
                
        return response
