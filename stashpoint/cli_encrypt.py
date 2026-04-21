"""CLI commands for managing stash encryption."""

import click
from stashpoint.encrypt import (
    generate_key,
    save_key,
    load_key,
    encrypt_variables,
    decrypt_variables,
    get_key_path,
    EncryptionNotAvailableError,
    InvalidKeyError,
)
from stashpoint.storage import load_stash, save_stash


@click.group("encrypt")
def encrypt_cmd():
    """Manage stash encryption."""


@encrypt_cmd.command("init")
@click.option("--force", is_flag=True, help="Overwrite existing key.")
def init_cmd(force):
    """Generate and save a new encryption key."""
    path = get_key_path()
    if path.exists() and not force:
        click.echo(f"Key already exists at {path}. Use --force to overwrite.", err=True)
        raise SystemExit(1)
    try:
        key = generate_key()
        save_key(key)
        click.echo(f"Encryption key saved to {path}")
    except EncryptionNotAvailableError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@encrypt_cmd.command("lock")
@click.argument("stash_name")
def lock_cmd(stash_name):
    """Encrypt all variables in a stash."""
    try:
        key = load_key()
        variables = load_stash(stash_name)
        encrypted = encrypt_variables(variables, key)
        save_stash(stash_name, encrypted)
        click.echo(f"Stash '{stash_name}' encrypted successfully.")
    except (InvalidKeyError, EncryptionNotAvailableError) as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)
    except KeyError:
        click.echo(f"Stash '{stash_name}' not found.", err=True)
        raise SystemExit(1)


@encrypt_cmd.command("unlock")
@click.argument("stash_name")
def unlock_cmd(stash_name):
    """Decrypt all variables in a stash."""
    try:
        key = load_key()
        variables = load_stash(stash_name)
        decrypted = decrypt_variables(variables, key)
        save_stash(stash_name, decrypted)
        click.echo(f"Stash '{stash_name}' decrypted successfully.")
    except (InvalidKeyError, EncryptionNotAvailableError) as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)
    except KeyError:
        click.echo(f"Stash '{stash_name}' not found.", err=True)
        raise SystemExit(1)


@encrypt_cmd.command("status")
def status_cmd():
    """Show whether an encryption key exists."""
    path = get_key_path()
    if path.exists():
        click.echo(f"Encryption key found at {path}")
    else:
        click.echo("No encryption key found. Run 'stashpoint encrypt init' to create one.")
