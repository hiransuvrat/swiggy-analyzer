"""Token storage with encryption using macOS Keychain."""

import keyring
from datetime import datetime, timedelta
from typing import Optional

from cryptography.fernet import Fernet
from loguru import logger

from ..data.repository import SwiggyRepository
from ..data.models import OAuthToken


class TokenStore:
    """Secure token storage using encrypted SQLite + macOS Keychain."""

    SERVICE_NAME = "swiggy-analyzer"
    ENCRYPTION_KEY_NAME = "encryption-key"

    def __init__(self, repository: SwiggyRepository):
        self.repository = repository
        self._ensure_encryption_key()

    def _ensure_encryption_key(self):
        """Ensure encryption key exists in Keychain, create if not."""
        key = keyring.get_password(self.SERVICE_NAME, self.ENCRYPTION_KEY_NAME)
        if not key:
            # Generate new key
            key = Fernet.generate_key().decode()
            keyring.set_password(self.SERVICE_NAME, self.ENCRYPTION_KEY_NAME, key)
            logger.info("Generated new encryption key in Keychain")

    def _get_cipher(self) -> Fernet:
        """Get Fernet cipher using key from Keychain."""
        key = keyring.get_password(self.SERVICE_NAME, self.ENCRYPTION_KEY_NAME)
        return Fernet(key.encode())

    def save_token(self, service: str, access_token: str, refresh_token: Optional[str] = None,
                   expires_in: Optional[int] = None, token_type: str = "Bearer"):
        """Save encrypted token."""
        cipher = self._get_cipher()

        # Encrypt tokens
        encrypted_access = cipher.encrypt(access_token.encode()).decode()
        encrypted_refresh = cipher.encrypt(refresh_token.encode()).decode() if refresh_token else None

        # Calculate expiry
        expires_at = None
        if expires_in:
            expires_at = datetime.now() + timedelta(seconds=expires_in)

        token = OAuthToken(
            service=service,
            access_token=encrypted_access,
            refresh_token=encrypted_refresh,
            token_type=token_type,
            expires_at=expires_at,
        )

        self.repository.save_token(token)
        logger.info(f"Saved encrypted token for service: {service}")

    def get_token(self, service: str) -> Optional[dict]:
        """Get decrypted token."""
        token = self.repository.get_token(service)
        if not token:
            return None

        cipher = self._get_cipher()

        # Decrypt tokens
        access_token = cipher.decrypt(token.access_token.encode()).decode()
        refresh_token = None
        if token.refresh_token:
            refresh_token = cipher.decrypt(token.refresh_token.encode()).decode()

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": token.token_type,
            "expires_at": token.expires_at,
        }

    def is_token_valid(self, service: str) -> bool:
        """Check if token exists and is not expired."""
        token_data = self.get_token(service)
        if not token_data:
            return False

        if token_data["expires_at"]:
            # Add 5 minute buffer
            return datetime.now() < token_data["expires_at"] - timedelta(minutes=5)

        return True

    def delete_token(self, service: str):
        """Delete token."""
        self.repository.delete_token(service)
        logger.info(f"Deleted token for service: {service}")
