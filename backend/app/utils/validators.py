"""
Input validation utilities
"""
import re
from urllib.parse import urlparse
from typing import Optional
from ..config import settings


def validate_url(url: str) -> tuple[bool, Optional[str]]:
    """
    Validate a URL for scanning

    Args:
        url: The URL to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        parsed = urlparse(url)

        # Check if scheme is HTTP or HTTPS
        if parsed.scheme not in ('http', 'https'):
            return False, "URL must use HTTP or HTTPS protocol"

        # Check if netloc exists
        if not parsed.netloc:
            return False, "Invalid URL format"

        # Check for blocked domains
        if is_domain_blocked(parsed.netloc):
            return False, "Domain is not allowed for scanning"

        # Check URL length
        if len(url) > 255:
            return False, "URL is too long (max 255 characters)"

        return True, None

    except Exception as e:
        return False, f"Invalid URL format: {str(e)}"


def is_domain_blocked(domain: str) -> bool:
    """
    Check if a domain is blocked from scanning

    Args:
        domain: The domain to check

    Returns:
        True if domain is blocked, False otherwise
    """
    blocked_domains = settings.blocked_domains

    # Convert to lowercase for comparison
    domain_lower = domain.lower()

    # Direct match
    if domain_lower in blocked_domains:
        return True

    # Check for subdomains of blocked domains
    for blocked_domain in blocked_domains:
        if domain_lower.endswith(f".{blocked_domain}"):
            return True

    # Check for localhost and private IP ranges
    if domain_lower in ('localhost', '127.0.0.1'):
        return True

    # Check for IP address patterns
    ip_pattern = re.compile(r'^(10\.|172\.(1[6-9]|2[0-9]|3[0-1])\.|192\.168\.)')
    if ip_pattern.match(domain_lower):
        return True

    return False


def sanitize_scan_options(options: dict) -> dict:
    """
    Sanitize and validate scan options

    Args:
        options: Raw scan options

    Returns:
        Sanitized options dictionary
    """
    sanitized = {
        "include_screenshot": bool(options.get("include_screenshot", True)),
        "scan_depth": options.get("scan_depth", "standard") if options.get("scan_depth") in ["quick", "standard", "deep"] else "standard",
        "mobile_view": bool(options.get("mobile_view", False))
    }

    return sanitized