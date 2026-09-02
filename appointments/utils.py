import secrets
import string
from django.utils import timezone


def generate_booking_id(prefix="CF-APT") -> str:
    """
    Generates a unique, non-predictable, human-friendly booking ID.
    Format: CF-APT-YYYYMMDD-XXXXX (e.g. CF-APT-20260902-K9R7M)
    """
    date_str = timezone.now().strftime('%Y%m%d')
    random_suffix = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(5))
    return f"{prefix}-{date_str}-{random_suffix}"


def generate_secure_access_token() -> str:
    """
    Generates a cryptographically secure random URL-safe token.
    Prevents sequential ID guessing or scraping of patient appointments.
    """
    return secrets.token_urlsafe(32)
