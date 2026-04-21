"""Tests for the encrypt CLI commands."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from pathlib import Path

pytest.importorskip("cryptography", reason="cryptography package required")

from stashpoint.cli_encrypt import encrypt_cmd


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def mock_key():
    from stashpoint.encrypt import generate_key
    return generate_key()


def test_init_creates_key(runner, tmp_path):
    key_path = tmp_path / "stash.key"
    with patch("stashpoint.cli_encrypt.get_key_path", return_value=key_path), \
         patch("stashpoint.cli_encrypt.generate_key", return_value=b"fakekey"), \
         patch("stashpoint.cli_encrypt.save_key") as mock_save:
        result = runner.invoke(encrypt_cmd, ["init"])
    assert result.exit_code == 0
    assert "saved" in result.output


def test_init_refuses_overwrite_without_force(runner, tmp_path):
    key_path = tmp_path / "stash.key"
    key_path.write_bytes(b"existing")
    with patch("stashpoint.cli_encrypt.get_key_path", return_value=key_path):
        result = runner.invoke(encrypt_cmd, ["init"])
    assert result.exit_code != 0
    assert "already exists" in result.output


def test_init_force_overwrites(runner, tmp_path):
    key_path = tmp_path / "stash.key"
    key_path.write_bytes(b"existing")
    with patch("stashpoint.cli_encrypt.get_key_path", return_value=key_path), \
         patch("stashpoint.cli_encrypt.generate_key", return_value=b"newkey"), \
         patch("stashpoint.cli_encrypt.save_key"):
        result = runner.invoke(encrypt_cmd, ["init", "--force"])
    assert result.exit_code == 0


def test_lock_encrypts_stash(runner, mock_key):
    variables = {"FOO": "bar"}
    with patch("stashpoint.cli_encrypt.load_key", return_value=mock_key), \
         patch("stashpoint.cli_encrypt.load_stash", return_value=variables), \
         patch("stashpoint.cli_encrypt.save_stash") as mock_save, \
         patch("stashpoint.cli_encrypt.encrypt_variables", return_value={"FOO": "encrypted"}):
        result = runner.invoke(encrypt_cmd, ["lock", "myproject"])
    assert result.exit_code == 0
    assert "encrypted" in result.output
    mock_save.assert_called_once_with("myproject", {"FOO": "encrypted"})


def test_lock_stash_not_found(runner, mock_key):
    with patch("stashpoint.cli_encrypt.load_key", return_value=mock_key), \
         patch("stashpoint.cli_encrypt.load_stash", side_effect=KeyError("missing")):
        result = runner.invoke(encrypt_cmd, ["lock", "ghost"])
    assert result.exit_code != 0
    assert "not found" in result.output


def test_unlock_decrypts_stash(runner, mock_key):
    encrypted = {"FOO": "encryptedvalue"}
    with patch("stashpoint.cli_encrypt.load_key", return_value=mock_key), \
         patch("stashpoint.cli_encrypt.load_stash", return_value=encrypted), \
         patch("stashpoint.cli_encrypt.save_stash") as mock_save, \
         patch("stashpoint.cli_encrypt.decrypt_variables", return_value={"FOO": "bar"}):
        result = runner.invoke(encrypt_cmd, ["unlock", "myproject"])
    assert result.exit_code == 0
    assert "decrypted" in result.output


def test_status_key_exists(runner, tmp_path):
    key_path = tmp_path / "stash.key"
    key_path.write_bytes(b"key")
    with patch("stashpoint.cli_encrypt.get_key_path", return_value=key_path):
        result = runner.invoke(encrypt_cmd, ["status"])
    assert "found" in result.output


def test_status_key_missing(runner, tmp_path):
    key_path = tmp_path / "missing.key"
    with patch("stashpoint.cli_encrypt.get_key_path", return_value=key_path):
        result = runner.invoke(encrypt_cmd, ["status"])
    assert "No encryption key" in result.output
