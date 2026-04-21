"""Tests for stashpoint.encrypt module."""

import pytest
from unittest.mock import patch, MagicMock

pytest.importorskip("cryptography", reason="cryptography package required")

from stashpoint.encrypt import (
    generate_key,
    encrypt_variables,
    decrypt_variables,
    save_key,
    load_key,
    get_key_path,
    InvalidKeyError,
    EncryptionNotAvailableError,
)


@pytest.fixture
def key():
    return generate_key()


def test_generate_key_returns_bytes(key):
    assert isinstance(key, bytes)
    assert len(key) > 0


def test_encrypt_returns_dict(key):
    variables = {"FOO": "bar", "BAZ": "qux"}
    encrypted = encrypt_variables(variables, key)
    assert set(encrypted.keys()) == {"FOO", "BAZ"}
    assert encrypted["FOO"] != "bar"
    assert encrypted["BAZ"] != "qux"


def test_decrypt_restores_original(key):
    variables = {"FOO": "bar", "BAZ": "qux"}
    encrypted = encrypt_variables(variables, key)
    decrypted = decrypt_variables(encrypted, key)
    assert decrypted == variables


def test_decrypt_with_wrong_key_raises(key):
    variables = {"SECRET": "password123"}
    encrypted = encrypt_variables(variables, key)
    wrong_key = generate_key()
    with pytest.raises(InvalidKeyError):
        decrypt_variables(encrypted, wrong_key)


def test_encrypt_empty_dict(key):
    result = encrypt_variables({}, key)
    assert result == {}


def test_decrypt_empty_dict(key):
    result = decrypt_variables({}, key)
    assert result == {}


def test_save_and_load_key(tmp_path, key):
    with patch("stashpoint.encrypt.get_key_path", return_value=tmp_path / "stash.key"):
        save_key(key)
        loaded = load_key()
    assert loaded == key


def test_load_key_not_found(tmp_path):
    with patch("stashpoint.encrypt.get_key_path", return_value=tmp_path / "missing.key"):
        with pytest.raises(InvalidKeyError, match="No encryption key found"):
            load_key()


def test_key_file_permissions(tmp_path, key):
    key_path = tmp_path / "stash.key"
    with patch("stashpoint.encrypt.get_key_path", return_value=key_path):
        save_key(key)
    import stat
    mode = key_path.stat().st_mode & 0o777
    assert mode == 0o600


def test_encrypt_not_available_raises():
    import stashpoint.encrypt as enc
    original = enc.Fernet
    enc.Fernet = None
    try:
        with pytest.raises(EncryptionNotAvailableError):
            generate_key()
    finally:
        enc.Fernet = original
