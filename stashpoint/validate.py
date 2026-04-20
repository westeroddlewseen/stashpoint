"""Validation utilities for stash names and variable sets."""

import re
from typing import Dict, List, Tuple

# Valid stash name: alphanumeric, hyphens, underscores, dots. No spaces.
STASH_NAME_RE = re.compile(r'^[a-zA-Z0-9_\-\.]+$')
# Valid env var name: starts with letter or underscore, followed by word chars.
VAR_NAME_RE = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')

MAX_STASH_NAME_LENGTH = 64
MAX_VAR_NAME_LENGTH = 128
MAX_VAR_VALUE_LENGTH = 4096
MAX_VARS_PER_STASH = 256


class ValidationError(Exception):
    """Raised when validation fails."""
    pass


def validate_stash_name(name: str) -> Tuple[bool, str]:
    """Validate a stash name. Returns (is_valid, error_message)."""
    if not name:
        return False, "Stash name cannot be empty."
    if len(name) > MAX_STASH_NAME_LENGTH:
        return False, f"Stash name exceeds maximum length of {MAX_STASH_NAME_LENGTH} characters."
    if not STASH_NAME_RE.match(name):
        return False, "Stash name may only contain letters, digits, hyphens, underscores, and dots."
    return True, ""


def validate_var_name(name: str) -> Tuple[bool, str]:
    """Validate an environment variable name. Returns (is_valid, error_message)."""
    if not name:
        return False, "Variable name cannot be empty."
    if len(name) > MAX_VAR_NAME_LENGTH:
        return False, f"Variable name exceeds maximum length of {MAX_VAR_NAME_LENGTH} characters."
    if not VAR_NAME_RE.match(name):
        return False, "Variable name must start with a letter or underscore and contain only letters, digits, and underscores."
    return True, ""


def validate_var_value(value: str) -> Tuple[bool, str]:
    """Validate an environment variable value. Returns (is_valid, error_message)."""
    if len(value) > MAX_VAR_VALUE_LENGTH:
        return False, f"Variable value exceeds maximum length of {MAX_VAR_VALUE_LENGTH} characters."
    return True, ""


def validate_stash(name: str, variables: Dict[str, str]) -> List[str]:
    """Validate a complete stash. Returns a list of error messages (empty if valid)."""
    errors = []

    ok, msg = validate_stash_name(name)
    if not ok:
        errors.append(f"Invalid stash name '{name}': {msg}")

    if len(variables) > MAX_VARS_PER_STASH:
        errors.append(f"Stash contains {len(variables)} variables, exceeding the maximum of {MAX_VARS_PER_STASH}.")

    for var_name, var_value in variables.items():
        ok, msg = validate_var_name(var_name)
        if not ok:
            errors.append(f"Invalid variable name '{var_name}': {msg}")
        ok, msg = validate_var_value(var_value)
        if not ok:
            errors.append(f"Invalid value for '{var_name}': {msg}")

    return errors
