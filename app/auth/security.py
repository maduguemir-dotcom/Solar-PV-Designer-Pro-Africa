"""Password hashing helpers for the Stage 5A authentication foundation."""
from __future__ import annotations
import hashlib
import hmac
import secrets

ALGORITHM = "pbkdf2_sha256"
ITERATIONS = 310_000
SALT_BYTES = 16


def hash_password(password: str) -> str:
    if not isinstance(password, str) or len(password) < 8:
        raise ValueError("Password must contain at least 8 characters")
    salt = secrets.token_bytes(SALT_BYTES)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, ITERATIONS)
    return f"{ALGORITHM}${ITERATIONS}${salt.hex()}${digest.hex()}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, iterations, salt_hex, digest_hex = encoded.split("$", 3)
        if algorithm != ALGORITHM:
            return False
        expected = bytes.fromhex(digest_hex)
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt_hex), int(iterations))
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False
