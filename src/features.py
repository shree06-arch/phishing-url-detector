"""
features.py
Extracts lexical, structural, and heuristic features from a URL for
phishing classification. No network calls are made — every feature is
computed purely from the URL string, which keeps this fast and safe to
run on unverified input.
"""

import re
import math
from urllib.parse import urlparse

SUSPICIOUS_WORDS = [
    "login", "verify", "account", "update", "secure", "banking",
    "confirm", "signin", "password", "billing", "webscr", "ebayisapi",
    "paypal", "wallet", "suspend", "unlock", "alert", "recover",
]

SHORTENING_SERVICES = [
    "bit.ly", "goo.gl", "tinyurl.com", "ow.ly", "t.co", "is.gd",
    "buff.ly", "adf.ly", "shorte.st", "cutt.ly", "rb.gy",
]

BRAND_NAMES = [
    "paypal", "amazon", "apple", "microsoft", "google", "facebook",
    "netflix", "bankofamerica", "wellsfargo", "chase", "instagram",
]


def _shannon_entropy(s: str) -> float:
    if not s:
        return 0.0
    probs = [s.count(c) / len(s) for c in set(s)]
    return -sum(p * math.log2(p) for p in probs)


def _count_digits(s: str) -> int:
    return sum(c.isdigit() for c in s)


def _is_ip_address(host: str) -> bool:
    return bool(re.match(r"^(\d{1,3}\.){3}\d{1,3}$", host or ""))


def extract_features(url: str) -> dict:
    """Return a dict of numeric/boolean features for a single URL."""
    url = url.strip()
    if not re.match(r"^[a-zA-Z]+://", url):
        # assume http if no scheme given, so urlparse behaves
        parse_target = "http://" + url
    else:
        parse_target = url

    parsed = urlparse(parse_target)
    host = parsed.netloc.split("@")[-1].split(":")[0].lower()
    path = parsed.path or ""
    query = parsed.query or ""
    full = url.lower()

    subdomain_count = max(host.count(".") - 1, 0) if host else 0

    features = {
        "url_length": len(url),
        "host_length": len(host),
        "path_length": len(path),
        "num_dots": url.count("."),
        "num_hyphens": url.count("-"),
        "num_underscores": url.count("_"),
        "num_slashes": url.count("/"),
        "num_digits": _count_digits(url),
        "num_at_symbols": url.count("@"),
        "num_question_marks": url.count("?"),
        "num_equal_signs": url.count("="),
        "num_percent": url.count("%"),
        "num_subdomains": subdomain_count,
        "has_ip_host": int(_is_ip_address(host)),
        "has_https": int(parsed.scheme == "https"),
        "has_port": int(parsed.port is not None) if host else 0,
        "is_shortened": int(any(s in host for s in SHORTENING_SERVICES)),
        "has_suspicious_word": int(any(w in full for w in SUSPICIOUS_WORDS)),
        "suspicious_word_count": sum(w in full for w in SUSPICIOUS_WORDS),
        "brand_in_subdomain_or_path": int(
            any(b in host.split(".")[0] or b in path.lower() for b in BRAND_NAMES)
            and not any(host.endswith(b + ".com") for b in BRAND_NAMES)
        ),
        "host_entropy": round(_shannon_entropy(host), 3),
        "path_entropy": round(_shannon_entropy(path), 3),
        "digit_ratio_host": round(_count_digits(host) / len(host), 3) if host else 0,
        "has_double_slash_redirect": int("//" in path),
        "tld_length": len(host.split(".")[-1]) if "." in host else 0,
        "query_length": len(query),
    }
    return features


FEATURE_NAMES = list(extract_features("http://example.com/").keys())


if __name__ == "__main__":
    import sys
    import json

    test_url = sys.argv[1] if len(sys.argv) > 1 else "http://paypal-verify-account.tk/login.php?id=123"
    print(json.dumps(extract_features(test_url), indent=2))
