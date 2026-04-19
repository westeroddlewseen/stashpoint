"""Template support for stashpoint — create stashes from predefined templates."""

from typing import Dict, List, Optional

BUILTIN_TEMPLATES: Dict[str, Dict[str, str]] = {
    "python-dev": {
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONUNBUFFERED": "1",
        "PIP_NO_CACHE_DIR": "off",
    },
    "django": {
        "DJANGO_SETTINGS_MODULE": "config.settings.local",
        "DEBUG": "True",
        "ALLOWED_HOSTS": "localhost,127.0.0.1",
    },
    "docker": {
        "DOCKER_BUILDKIT": "1",
        "COMPOSE_DOCKER_CLI_BUILD": "1",
    },
    "aws": {
        "AWS_DEFAULT_REGION": "us-east-1",
        "AWS_OUTPUT_FORMAT": "json",
    },
}


class TemplateNotFoundError(Exception):
    pass


def list_templates() -> List[str]:
    """Return sorted list of available template names."""
    return sorted(BUILTIN_TEMPLATES.keys())


def get_template(name: str) -> Dict[str, str]:
    """Return variables for a named template.

    Raises TemplateNotFoundError if the template does not exist.
    """
    if name not in BUILTIN_TEMPLATES:
        raise TemplateNotFoundError(f"Template '{name}' not found.")
    return dict(BUILTIN_TEMPLATES[name])


def apply_template(
    name: str,
    overrides: Optional[Dict[str, str]] = None,
) -> Dict[str, str]:
    """Return template variables merged with optional overrides."""
    variables = get_template(name)
    if overrides:
        variables.update(overrides)
    return variables
