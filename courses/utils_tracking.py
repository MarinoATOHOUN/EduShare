import geocoder
from ipware import get_client_ip
from user_agents import parse
from .models import UserActivity
import logging
import ipaddress

logger = logging.getLogger("courses.tracking")

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
        # Skip geo lookup for local/private IPs (reduces latency + avoids noisy errors)
        try:
            ip_obj = ipaddress.ip_address(ip)
            if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local or ip_obj.is_reserved:
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
        except ValueError:
            pass

        # Use free ip-api.com via geocoder
        g = geocoder.ip(ip)
        if g.ok:
            city = g.city or ""
            country = g.country or ""
            if g.latlng:
                latitude = g.latlng[0]
                longitude = g.latlng[1]
    except Exception as e:
        logger.warning("Error getting location for ip=%s: %s", ip, e)
        
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
        
    try:
        info = get_user_activity_info(request)
    except Exception:
        logger.exception("Error building user activity info")
        return
    
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
