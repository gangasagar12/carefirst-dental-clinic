import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

def get_client_ip(request) -> str:
    """
    Extracts the client's actual IP address, handling proxies and load balancers.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '127.0.0.1')

def verify_recaptcha_token(token: str, remote_ip: str = None) -> bool:
    """
    Verifies a Google reCAPTCHA v3 or Cloudflare Turnstile response token.
    
    Security Behavior:
    - If no secret key is configured in settings (e.g. dev/local test environment),
      it returns True gracefully so legitimate development workflows are not blocked.
    - If a secret key IS configured, it strictly validates the token with Google/Cloudflare API.
    - In case of external API network failure/timeout, logs the error and safely allows
      the request to proceed so real patients are never blocked by third-party downtime.
    """
    google_secret = getattr(settings, 'RECAPTCHA_SECRET_KEY', '')
    turnstile_secret = getattr(settings, 'CLOUDFLARE_TURNSTILE_SECRET_KEY', '')

    # If neither secret key is set, allow (graceful fallback)
    if not google_secret and not turnstile_secret:
        return True

    # If configured but token is empty, reject
    if not token or not token.strip():
        logger.warning(f"Spam defense rejected submission: Missing captcha token from IP {remote_ip}.")
        return False

    # 1. Cloudflare Turnstile Verification
    if turnstile_secret:
        verify_url = 'https://challenges.cloudflare.com/turnstile/v0/siteverify'
        payload = {
            'secret': turnstile_secret,
            'response': token.strip(),
        }
        if remote_ip:
            payload['remoteip'] = remote_ip

        try:
            resp = requests.post(verify_url, data=payload, timeout=4)
            data = resp.json()
            if data.get('success', False):
                return True
            logger.warning(f"Cloudflare Turnstile rejected submission from {remote_ip}: {data.get('error-codes')}")
            return False
        except Exception as err:
            logger.error(f"Turnstile verification network error: {err}")
            return True

    # 2. Google reCAPTCHA v3 Verification
    if google_secret:
        verify_url = 'https://www.google.com/recaptcha/api/siteverify'
        payload = {
            'secret': google_secret,
            'response': token.strip(),
        }
        if remote_ip:
            payload['remoteip'] = remote_ip

        try:
            resp = requests.post(verify_url, data=payload, timeout=4)
            data = resp.json()
            success = data.get('success', False)
            score = float(data.get('score', 0.0))
            threshold = float(getattr(settings, 'RECAPTCHA_SCORE_THRESHOLD', 0.5))

            if success and score >= threshold:
                return True

            logger.warning(
                f"Google reCAPTCHA v3 rejected submission from {remote_ip}: "
                f"success={success}, score={score} (threshold={threshold}), errors={data.get('error-codes')}"
            )
            return False
        except Exception as err:
            logger.error(f"Google reCAPTCHA verification network error: {err}")
            return True

    return True
