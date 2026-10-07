import re
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

# 1. Cyrillic / Russian unicode range
CYRILLIC_PATTERN = re.compile(r'[\u0400-\u04FF]')

# 2. Suspicious URL patterns & spam TLDs
URL_PATTERN = re.compile(
    r'(https?://|www\.|ftp://|//[\w\-]+|\b[\w\-]+\.(top|xyz|ru|cn|buzz|click|link|online|site|shop|info|vip|win|work|loan|cc|me|tk|ga|cf|gq|ml|pw|bid|date|racing|download|stream|press|party)\b)',
    re.IGNORECASE
)

# 3. Known bot spam phrases (Cyrillic and English casino / payout spam)
SPAM_PHRASES = [
    'перевод', 'руб', 'рублей', 'выигрыш', 'бонус', 'подарок', 'забрать тут',
    'получить тут', 'детали по ссылке', 'подробности по ссылке', 'информацию по ссылке',
    'casino', 'crypto', 'bitcoin', 'usdt', 't.me/', 'telegram', 'whatsapp', 'payout',
    'investment', 'earn money', 'viagra', 'cialis', 'porn', 'xxx', 'kunirtyrt', 'anarthyt'
]

def is_spam_submission(name: str = '', email: str = '', message: str = '', subject: str = '', ip: str = '') -> Tuple[bool, str]:
    """
    Evaluates whether a form submission is an automated bot/scam attack.
    Returns (True, reason) if spam, or (False, "") if genuine.
    """
    name_str = (name or '').strip()
    msg_str = (message or '').strip()
    email_str = (email or '').strip()
    subject_str = (subject or '').strip()
    combined_lower = f"{name_str} {msg_str} {email_str} {subject_str}".lower()

    # Check 1: Cyrillic / Russian characters in name, message, or subject
    if CYRILLIC_PATTERN.search(name_str) or CYRILLIC_PATTERN.search(msg_str) or CYRILLIC_PATTERN.search(subject_str):
        logger.warning(f"[SPAM DROPPED] Cyrillic detected from IP {ip}: name='{name_str[:30]}'")
        return True, "Cyrillic characters not permitted"

    # Check 2: URLs or spam TLDs in the name field (patients never have URLs in their name)
    if URL_PATTERN.search(name_str):
        logger.warning(f"[SPAM DROPPED] URL in name from IP {ip}: name='{name_str[:30]}'")
        return True, "URLs not permitted in name"

    # Check 3: URLs or spam links in message field
    if URL_PATTERN.search(msg_str):
        logger.warning(f"[SPAM DROPPED] URL in message from IP {ip}: msg='{msg_str[:30]}'")
        return True, "Links not permitted in message"

    # Check 4: Known spam keywords or phrases
    for phrase in SPAM_PHRASES:
        if phrase in combined_lower:
            logger.warning(f"[SPAM DROPPED] Keyword '{phrase}' from IP {ip}")
            return True, f"Spam pattern detected ({phrase})"

    # Check 5: Name length anomaly (bot payload stuffed into name)
    if len(name_str) > 55:
        logger.warning(f"[SPAM DROPPED] Abnormally long name ({len(name_str)} chars) from IP {ip}")
        return True, "Name exceeds maximum allowed length"

    # Check 6: Suspicious punctuation / brackets in name
    if any(ch in name_str for ch in ['<', '>', '{', '}', '[', ']', '$', '%', '^', '*', '=', '~', '`', '|', '\\', '#']):
        logger.warning(f"[SPAM DROPPED] Suspicious characters in name from IP {ip}")
        return True, "Invalid characters in name"

    return False, ""
