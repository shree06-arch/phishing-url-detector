import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from features import extract_features, _is_ip_address, _shannon_entropy  # noqa: E402


def test_ip_detection():
    assert _is_ip_address("192.168.1.1") is True
    assert _is_ip_address("github.com") is False
    assert _is_ip_address("") is False


def test_entropy_of_empty_string():
    assert _shannon_entropy("") == 0.0


def test_extract_features_basic_shape():
    feats = extract_features("https://example.com/path?x=1")
    assert isinstance(feats, dict)
    assert feats["has_https"] == 1
    assert feats["num_question_marks"] == 1
    assert feats["num_equal_signs"] == 1


def test_suspicious_url_flags_keywords():
    feats = extract_features("http://paypal-verify-login.tk/signin")
    assert feats["has_suspicious_word"] == 1
    assert feats["suspicious_word_count"] >= 2


def test_ip_host_detected():
    feats = extract_features("http://192.168.10.5/account/login")
    assert feats["has_ip_host"] == 1


def test_shortened_url_detected():
    feats = extract_features("http://bit.ly/abc123")
    assert feats["is_shortened"] == 1


def test_no_scheme_url_still_parses():
    feats = extract_features("example.com/path")
    assert feats["host_length"] > 0


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-v"]))
