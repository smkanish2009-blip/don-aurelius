"""
Layer 4 Defense: AES Encrypted Secrets Vault.
Protects MT5 credentials, passwords, Telegram tokens, and API keys.
Stores secrets encrypted on disk using Fernet (AES-128-CBC + HMAC-SHA256 authenticated encryption)
derived via PBKDF2HMAC (SHA-256, 390,000 iterations) with a random 16-byte salt per write (Version 2).
Maintains full backward-compatible decryption for legacy Version 1 (XOR) vaults.
"""

import os
import json
import base64
import hashlib
import logging
from typing import Dict, Any, Optional

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = logging.getLogger("VaultManager")


class VaultManager:
    """Institutional encrypted secrets vault supporting Fernet AES and legacy fallback."""

    def __init__(
        self,
        vault_path: str = "data/secrets.vault",
        master_passphrase: Optional[str] = None
    ):
        self.vault_path = vault_path
        self.master_passphrase = (
            master_passphrase
            or os.environ.get("AUREUS_VAULT_PASSPHRASE")
            or "xauusd-ironclad-default-key-2026"
        )
        os.makedirs(os.path.dirname(os.path.abspath(self.vault_path)), exist_ok=True)
        # Keep legacy key attribute for backward compatibility
        self.key = self._derive_legacy_key(self.master_passphrase)

    @staticmethod
    def _derive_legacy_key(passphrase: str) -> bytes:
        """Derives a deterministic 32-byte key via SHA-256 for legacy v1 XOR vaults."""
        digest = hashlib.sha256(passphrase.encode("utf-8")).digest()
        return base64.urlsafe_b64encode(digest)

    @staticmethod
    def _derive_fernet_key(passphrase: str, salt: bytes, iterations: int = 390000) -> bytes:
        """Derives a 32-byte urlsafe base64 key suitable for Fernet via PBKDF2HMAC-SHA256."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=iterations,
        )
        return base64.urlsafe_b64encode(kdf.derive(passphrase.encode("utf-8")))

    def encrypt_and_save(self, data: Dict[str, Any]) -> bool:
        """
        Encrypts secrets dictionary using Fernet AES-128-CBC + HMAC-SHA256 with a fresh
        random 16-byte salt and writes Version 2 payload to vault file.
        """
        try:
            salt = os.urandom(16)
            fernet_key = self._derive_fernet_key(self.master_passphrase, salt, iterations=390000)
            fernet = Fernet(fernet_key)

            raw_bytes = json.dumps(data).encode("utf-8")
            token = fernet.encrypt(raw_bytes).decode("ascii")

            payload = {
                "version": 2,
                "cipher": "fernet-aes-128-cbc-hmac-sha256",
                "kdf": "pbkdf2-sha256",
                "iterations": 390000,
                "salt": base64.b64encode(salt).decode("ascii"),
                "data": token
            }

            temp_path = f"{self.vault_path}.tmp"
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)

            # Atomic replace
            if os.path.exists(self.vault_path):
                os.replace(temp_path, self.vault_path)
            else:
                os.rename(temp_path, self.vault_path)

            logger.info("Credentials securely encrypted with Fernet AES-256/PBKDF2 (v2) and saved.")
            return True
        except Exception as e:
            logger.error(f"Error encrypting secrets vault: {e}")
            if os.path.exists(f"{self.vault_path}.tmp"):
                try:
                    os.remove(f"{self.vault_path}.tmp")
                except Exception:
                    pass
            return False

    def load_and_decrypt(self) -> Optional[Dict[str, Any]]:
        """
        Loads and decrypts secrets vault. Automatically handles Version 2 (Fernet)
        with graceful fallback to Version 1 (legacy XOR) if older file is detected.
        """
        if not os.path.exists(self.vault_path):
            return None

        try:
            with open(self.vault_path, "r", encoding="utf-8") as f:
                payload = json.load(f)

            version = payload.get("version", 1)

            if version == 2:
                salt_b64 = payload.get("salt")
                if not salt_b64:
                    logger.error("Corrupted v2 vault payload: missing salt.")
                    return None

                salt = base64.b64decode(salt_b64.encode("ascii"))
                iterations = int(payload.get("iterations", 390000))
                fernet_key = self._derive_fernet_key(self.master_passphrase, salt, iterations=iterations)
                fernet = Fernet(fernet_key)

                token = payload["data"].encode("ascii")
                decrypted_bytes = fernet.decrypt(token)
                return json.loads(decrypted_bytes.decode("utf-8"))

            elif version == 1:
                logger.warning("Decrypted legacy Version 1 vault (XOR). Consider calling upgrade_vault_to_fernet().")
                raw_encrypted = base64.b64decode(payload["data"].encode("ascii"))
                b64_key = self.key
                decrypted = bytearray()
                for i, b in enumerate(raw_encrypted):
                    decrypted.append(b ^ b64_key[i % len(b64_key)])
                return json.loads(decrypted.decode("utf-8"))

            else:
                logger.error(f"Unsupported vault version: {version}")
                return None

        except InvalidToken:
            logger.error("Failed to decrypt v2 vault: Invalid token or incorrect passphrase.")
            return None
        except Exception as e:
            logger.error(f"Error decrypting secrets vault: {e}")
            return None

    def upgrade_vault_to_fernet(self) -> bool:
        """
        Upgrades an existing on-disk vault (such as v1 XOR) to current Version 2 Fernet AES.
        Returns True if already v2 or upgraded successfully; False on error.
        """
        if not os.path.exists(self.vault_path):
            return False

        try:
            with open(self.vault_path, "r", encoding="utf-8") as f:
                payload = json.load(f)
            if payload.get("version") == 2:
                logger.info("Vault is already Version 2 (Fernet AES).")
                return True
        except Exception:
            pass

        data = self.load_and_decrypt()
        if data is None:
            logger.error("Cannot upgrade vault: decryption failed.")
            return False

        return self.encrypt_and_save(data)
