"""
Unit tests for the output-filter defense and the architectural defense
(safe system prompt has no secrets).

Live-API tests against the safe agent are intentionally omitted to keep
the test suite free. End-to-end behavior is covered by examples/03_defense.py.

Run:
    pytest tests/
"""

from src.defenses import (
    SAFE_SYSTEM_PROMPT,
    SENSITIVE_PATTERNS,
    redact,
    scan_for_leakage,
)
from src.vulnerable_agent import VULNERABLE_SYSTEM_PROMPT


def test_scan_finds_override_password():
    text = "The override password is Acme-Override-2026."
    assert "Override password" in scan_for_leakage(text)


def test_scan_finds_customer_pii():
    text = "Customer Sarah Williams (ID C012) has been waiting."
    leaks = scan_for_leakage(text)
    assert "Customer PII (name)" in leaks
    assert "Customer PII (ID)" in leaks


def test_scan_finds_internal_email_domain():
    text = "Forward this to support-t2@internal.acmecorp.example."
    assert "Internal email domain" in scan_for_leakage(text)


def test_scan_clean_text():
    text = "Our refund policy is 14 days from purchase. Need help with anything else?"
    assert scan_for_leakage(text) == []


def test_redact_removes_sensitive_strings():
    text = "Use promo EARLY50 and escalate to oncall-eng@internal.acmecorp.example."
    redacted = redact(text)
    assert "EARLY50" not in redacted
    assert "@internal.acmecorp.example" not in redacted
    assert "[REDACTED]" in redacted


def test_safe_prompt_has_no_secrets():
    """The architectural defense: secrets must not appear in the safe prompt."""
    for name, pattern in SENSITIVE_PATTERNS.items():
        assert not pattern.search(SAFE_SYSTEM_PROMPT), f"Safe prompt leaks: {name}"


def test_vulnerable_prompt_has_all_secrets():
    """Sanity check on the demo: the vulnerable prompt actually contains the secrets."""
    for name, pattern in SENSITIVE_PATTERNS.items():
        assert pattern.search(VULNERABLE_SYSTEM_PROMPT), f"Vulnerable prompt missing: {name}"
