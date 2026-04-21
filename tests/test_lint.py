"""Tests for stashpoint.lint."""

import pytest
from stashpoint.lint import lint_stash, format_lint, LintIssue


def test_lint_empty_stash_returns_warning():
    issues = lint_stash({})
    assert len(issues) == 1
    assert issues[0].level == "warning"
    assert "empty" in issues[0].message.lower()


def test_lint_clean_stash_returns_no_issues():
    issues = lint_stash({"APP_ENV": "production", "PORT": "8080"})
    assert issues == []


def test_lint_detects_empty_value():
    issues = lint_stash({"MY_VAR": ""})
    assert any(i.key == "MY_VAR" and "empty" in i.message.lower() for i in issues)


def test_lint_detects_whitespace_padding():
    issues = lint_stash({"MY_VAR": "  hello  "})
    assert any(i.key == "MY_VAR" and "whitespace" in i.message.lower() for i in issues)


def test_lint_detects_long_value():
    issues = lint_stash({"BIG": "x" * 1025})
    assert any(i.key == "BIG" and "1024" in i.message for i in issues)


def test_lint_detects_long_key():
    long_key = "A" * 129
    issues = lint_stash({long_key: "value"})
    assert any(i.key == long_key and i.level == "error" for i in issues)


@pytest.mark.parametrize("key", [
    "DB_PASSWORD",
    "API_SECRET",
    "GITHUB_TOKEN",
    "MY_API_KEY",
    "AWS_PRIVATE_KEY",
])
def test_lint_warns_on_sensitive_key_names(key):
    issues = lint_stash({key: "somevalue"})
    assert any(i.key == key and i.level == "warning" for i in issues)


def test_lint_sensitive_check_is_case_insensitive():
    issues = lint_stash({"db_password": "secret"})
    assert any(i.key == "db_password" for i in issues)


def test_format_lint_no_issues():
    result = format_lint("myproject", [])
    assert "myproject" in result
    assert "no issues" in result


def test_format_lint_with_issues():
    issues = [
        LintIssue("warning", "MY_VAR", "Value is empty"),
        LintIssue("error", "LONG_KEY", "Key exceeds 128 characters"),
    ]
    result = format_lint("myproject", issues)
    assert "myproject" in result
    assert "[WARN]" in result
    assert "[ERROR]" in result
    assert "MY_VAR" in result
    assert "LONG_KEY" in result


def test_format_lint_empty_key_issue():
    issues = [LintIssue("warning", "", "Stash is empty")]
    result = format_lint("empty-stash", issues)
    assert "Stash is empty" in result
