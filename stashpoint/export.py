"""Export stashes to various shell formats."""

from typing import Dict

SUPPORTED_SHELLS = ["bash", "fish", "zsh", "powershell"]


def export_bash(variables: Dict[str, str]) -> str:
    """Export variables as bash/zsh export statements."""
    lines = []
    for key, value in variables.items():
        escaped = value.replace('"', '\\"')
        lines.append(f'export {key}="{escaped}"')
    return "\n".join(lines)


def export_fish(variables: Dict[str, str]) -> str:
    """Export variables as fish shell set statements."""
    lines = []
    for key, value in variables.items():
        escaped = value.replace('"', '\\"')
        lines.append(f'set -x {key} "{escaped}"')
    return "\n".join(lines)


def export_powershell(variables: Dict[str, str]) -> str:
    """Export variables as PowerShell environment variable assignments."""
    lines = []
    for key, value in variables.items():
        escaped = value.replace('"', '`"')
        lines.append(f'$env:{key} = "{escaped}"')
    return "\n".join(lines)


def export_dotenv(variables: Dict[str, str]) -> str:
    """Export variables in .env file format."""
    lines = []
    for key, value in variables.items():
        escaped = value.replace('"', '\\"')
        lines.append(f'{key}="{escaped}"')
    return "\n".join(lines)


def export_variables(variables: Dict[str, str], shell: str) -> str:
    """Export variables in the specified shell format."""
    shell = shell.lower()
    if shell in ("bash", "zsh"):
        return export_bash(variables)
    elif shell == "fish":
        return export_fish(variables)
    elif shell == "powershell":
        return export_powershell(variables)
    elif shell == "dotenv":
        return export_dotenv(variables)
    else:
        raise ValueError(f"Unsupported shell format: {shell}. Choose from: bash, zsh, fish, powershell, dotenv")
