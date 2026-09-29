"""
Cryptographically Secure Password Hashing & Verification Module.
Implements NIST SP 800-132 compliant PBKDF2-HMAC-SHA256 with 100,000 iterations,
cryptographically secure random 16-byte salt, and constant-time verification
against timing analysis attacks.
"""

import os
import hmac
import hashlib
import binascii
from typing import Tuple

DEFAULT_ITERATIONS = 100_000
ALGORITHM = "sha256"


def hash_password(password: str, iterations: int = DEFAULT_ITERATIONS) -> str:
    """
    Hashes a plaintext password using PBKDF2-HMAC-SHA256 with a unique 16-byte salt.
    Returns format: $pbkdf2-sha256${iterations}${salt_hex}${hash_hex}
    """
    if not password:
        raise ValueError("Password cannot be empty.")

    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac(
        ALGORITHM,
        password.encode("utf-8"),
        salt,
        iterations
    )
    salt_hex = binascii.hexlify(salt).decode("ascii")
    hash_hex = binascii.hexlify(dk).decode("ascii")
    return f"$pbkdf2-sha256${iterations}${salt_hex}${hash_hex}"


def verify_password(password: str, stored_hash: str) -> bool:
    """
    Verifies a plaintext password against a stored PBKDF2-HMAC-SHA256 hash
    using constant-time comparison to prevent side-channel timing attacks.
    """
    if not password or not stored_hash:
        return False

    try:
        parts = stored_hash.split("$")
        if len(parts) != 5 or parts[1] != f"pbkdf2-{ALGORITHM}":
            return False

        iterations = int(parts[2])
        salt = binascii.unhexlify(parts[3].encode("ascii"))
        expected_hash = binascii.unhexlify(parts[4].encode("ascii"))

        actual_hash = hashlib.pbkdf2_hmac(
            ALGORITHM,
            password.encode("utf-8"),
            salt,
            iterations
        )
        return hmac.compare_digest(actual_hash, expected_hash)
    except Exception:
        return False


if __name__ == "__main__":
    # Self-test
    pwd = "SovereignTradingKey!2026"
    h = hash_password(pwd)
    assert verify_password(pwd, h), "Verification failed for correct password!"
    assert not verify_password("WrongPassword", h), "Verification passed for incorrect password!"
    print(f"[+] PasswordHasher self-test passed: {h[:35]}...")
