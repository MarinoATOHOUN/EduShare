import geocoder
from ipware import get_client_ip
from user_agents import parse
from .models import UserActivity

def get_user_activity_info(request):
    """Extract IP, device and location info from request"""
    # Get IP
    ip, is_routable = get_client_ip(request)
    if ip is None:
        ip = '0.0.0.0'
    
    # Get User Agent info
    ua_string = request.META.get('HTTP_USER_AGENT', '')
    user_agent = parse(ua_string)
    
    device_type = "Mobile" if user_agent.is_mobile else "Tablet" if user_agent.is_tablet else "PC" if user_agent.is_pc else "Bot" if user_agent.is_bot else "Unknown"
    os_info = f"{user_agent.os.family} {user_agent.os.version_string}"
    browser_info = f"{user_agent.browser.family} {user_agent.browser.version_string}"
    
    # Get Location info
    city = ""
    country = ""
    latitude = None
    longitude = None
    
    try:
        # Use free ip-api.com via geocoder
        g = geocoder.ip(ip)
        if g.ok:
            city = g.city or ""
            country = g.country or ""
            if g.latlng:
                latitude = g.latlng[0]
                longitude = g.latlng[1]
    except Exception as e:
        print(f"Error getting location: {e}")
        
    return {
        'ip_address': ip,
        'user_agent': ua_string,
        'device_type': device_type,
        'os': os_info,
        'browser': browser_info,
        'city': city,
        'country': country,
        'latitude': latitude,
        'longitude': longitude
    }

def record_user_activity(user, request):
    """Record user activity if it has changed since last time"""
    if not user.is_authenticated:
        return
        
    info = get_user_activity_info(request)
    
    # Get last activity
    last_activity = UserActivity.objects.filter(user=user).first()
    
    should_record = False
    if not last_activity:
        should_record = True
    else:
        # Check if anything changed
        if (last_activity.ip_address != info['ip_address'] or 
            last_activity.user_agent != info['user_agent'] or
            last_activity.city != info['city'] or
            last_activity.country != info['country']):
            should_record = True
            
    if should_record:
        UserActivity.objects.create(
            user=user,
            **info
        )
