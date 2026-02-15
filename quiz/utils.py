import secrets
import string

def generate_public_id():
    chars = string.digits
    return ''.join(secrets.choice(chars) for _ in range(6))

def generate_admin_id():
    return secrets.token_urlsafe(12)[:16]