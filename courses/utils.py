import base64
from django.conf import settings

def encrypt_id(id_val):
    """Simple encryption of an ID to a string"""
    if id_val is None:
        return None
    try:
        # Simple XOR with a key from settings or a default
        key = getattr(settings, 'SECRET_KEY', 'default_key')[:8]
        s = str(id_val)
        # Pad or repeat key to match length of s
        repeated_key = (key * (len(s) // len(key) + 1))[:len(s)]
        xor_result = bytes([ord(a) ^ ord(b) for a, b in zip(s, repeated_key)])
        return base64.urlsafe_b64encode(xor_result).decode().rstrip('=')
    except Exception:
        return None

def decrypt_id(encrypted_id):
    """Decrypt the string back to an ID"""
    if not encrypted_id:
        return None
    try:
        # Add padding back
        padding = '=' * (4 - len(encrypted_id) % 4)
        xor_result = base64.urlsafe_b64decode(encrypted_id + padding)
        key = getattr(settings, 'SECRET_KEY', 'default_key')[:8]
        repeated_key = (key * (len(xor_result) // len(key) + 1))[:len(xor_result)]
        decrypted = "".join([chr(a ^ ord(b)) for a, b in zip(xor_result, repeated_key)])
        return int(decrypted)
    except Exception:
        return None
