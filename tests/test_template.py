"""Tests for stashpoint.template."""

import pytest
from stashpoint.template import (
    list_templates,
    get_template,
    apply_template,
    TemplateNotFoundError,
    BUILTIN_TEMPLATES,
)


def test_list_templates_returns_sorted():
    result = list_templates()
    assert result == sorted(BUILTIN_TEMPLATES.keys())


def test_list_templates_not_empty():
    assert len(list_templates()) > 0


def test_get_template_known():
    variables = get_template("python-dev")
    assert "PYTHONDONTWRITEBYTECODE" in variables
    assert variables["PYTHONUNBUFFERED"] == "1"


def test_get_template_not_found():
    with pytest.raises(TemplateNotFoundError, match="'nonexistent'"):
        get_template("nonexistent")


def test_get_template_returns_copy():
    v1 = get_template("python-dev")
    v1["NEW_KEY"] = "mutated"
    v2 = get_template("python-dev")
    assert "NEW_KEY" not in v2


def test_apply_template_no_overrides():
    result = apply_template("docker")
    assert result == get_template("docker")


def test_apply_template_with_overrides():
    result = apply_template("django", {"DEBUG": "False", "EXTRA": "yes"})
    assert result["DEBUG"] == "False"
    assert result["EXTRA"] == "yes"
    assert "DJANGO_SETTINGS_MODULE" in result


def test_apply_template_not_found():
    with pytest.raises(TemplateNotFoundError):
        apply_template("bogus")
