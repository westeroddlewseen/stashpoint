"""Encryption support for stash variables using Fernet symmetric encryption."""

import os
import base64
from pathlib import Path
from typing import Dict

try:
    from cryptography.fernet import Fernet, InvalidToken
except ImportError:
    Fernet = None
    InvalidToken = Exception


class EncryptionNotAvailableError(Exception):
    """Raised when the cryptography package is not installed."""


class InvalidKeyError(Exception):
    """Raised when the encryption key is invalid or decryption fails."""


def get_key_path() -> Path:
    base = Path(os.environ.get("STASHPOINT_DIR", Path.home() / ".stashpoint"))
    return base / "stash.key"


def _require_cryptography() -> None:
    if Fernet is None:
        raise EncryptionNotAvailableError(
            "The 'cryptography' package is required for encryption. "
            "Install it with: pip install cryptography"
        )


def generate_key() -> bytes:
    """Generate a new Fernet key."""
    _require_cryptography()
    return Fernet.generate_key()


def save_key(key: bytes) -> None:
    """Save a Fernet key to the default key path."""
    path = get_key_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(key)
    path.chmod(0o600)


def load_key() -> bytes:
    """Load the Fernet key from disk."""
    path = get_key_path()
    if not path.exists():
        raise InvalidKeyError(f"No encryption key found at {path}. Run 'stashpoint encrypt init' to create one.")
    return path.read_bytes()


def encrypt_variables(variables: Dict[str, str], key: bytes) -> Dict[str, str]:
    """Encrypt all variable values using the given key."""
    _require_cryptography()
    f = Fernet(key)
    return {k: base64.urlsafe_b64encode(f.encrypt(v.encode())).decode() for k, v in variables.items()}


def decrypt_variables(variables: Dict[str, str], key: bytes) -> Dict[str, str]:
    """Decrypt all variable values using the given key."""
    _require_cryptography()
    f = Fernet(key)
    result = {}
    for k, v in variables.items():
        try:
            raw = base64.urlsafe_b64decode(v.encode())
            result[k] = f.decrypt(raw).decode()
        except Exception:
            raise InvalidKeyError(f"Failed to decrypt variable '{k}'. Wrong key or corrupted data.")
    return result
