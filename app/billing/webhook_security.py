"""Signed webhook verification utilities for Stage 5D.

The application verifies the signature before trusting any provider event.
The secret must come from deployment configuration, never from source code.
"""
from __future__ import annotations
import hashlib
import hmac


def sign_payload(payload: bytes, secret: str) -> str:
    return hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()


def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    if not secret or not signature:
        return False
    expected = sign_payload(payload, secret)
    return hmac.compare_digest(expected, signature.strip())
