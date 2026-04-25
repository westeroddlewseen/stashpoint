"""Schema versioning and migration support for stash storage."""

from __future__ import annotations

CURRENT_SCHEMA_VERSION = 2

MIGRATIONS: dict[int, callable] = {}


class SchemaMigrationError(Exception):
    """Raised when a stash file cannot be migrated."""


def register_migration(from_version: int):
    """Decorator to register a migration function for a given version."""
    def decorator(fn):
        MIGRATIONS[from_version] = fn
        return fn
    return decorator


@register_migration(1)
def migrate_v1_to_v2(data: dict) -> dict:
    """v1 -> v2: wrap bare variable dicts under a 'stashes' key with schema_version."""
    if "stashes" not in data:
        return {
            "schema_version": 2,
            "stashes": data,
        }
    data["schema_version"] = 2
    return data


def detect_version(data: dict) -> int:
    """Detect the schema version of a loaded stash file."""
    if "schema_version" in data:
        return int(data["schema_version"])
    # v1 files are plain dicts of stash_name -> {key: value}
    return 1


def migrate(data: dict) -> dict:
    """Migrate data to the current schema version, applying all needed migrations."""
    version = detect_version(data)
    while version < CURRENT_SCHEMA_VERSION:
        if version not in MIGRATIONS:
            raise SchemaMigrationError(
                f"No migration path from schema version {version} "
                f"to {CURRENT_SCHEMA_VERSION}."
            )
        data = MIGRATIONS[version](data)
        version = detect_version(data)
    return data


def unwrap(data: dict) -> dict:
    """Return the stashes dict from a (possibly versioned) data structure."""
    if "stashes" in data:
        return data["stashes"]
    return data


def wrap(stashes: dict) -> dict:
    """Wrap a stashes dict in the current versioned structure."""
    return {
        "schema_version": CURRENT_SCHEMA_VERSION,
        "stashes": stashes,
    }
