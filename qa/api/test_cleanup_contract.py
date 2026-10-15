"""Guardrails for disposable QA identities; no live user is created here."""

from __future__ import annotations

import pytest
import asyncio
from uuid import uuid4

from qa.support.auth import auth_mutations_are_allowed
from qa.support.cleanup import delete_local_qa_users, require_local_cleanup_settings


@pytest.mark.parametrize("url", ["https://example.com", "https://localhost.evil.test", "https://localhost"])
def test_remote_urls_never_enable_account_mutations(monkeypatch, url):
    monkeypatch.setenv("QA_ALLOW_AUTH_MUTATIONS", "1")
    assert auth_mutations_are_allowed(url) is False


@pytest.mark.parametrize("email", ["person@example.com", "qa-e2e-old@example.invalid", "qa-template-xyz@example.invalid"])
def test_cleanup_rejects_non_generated_identity(email):
    with pytest.raises(ValueError, match="outside the generated QA namespace"):
        delete_local_qa_users([email])


def test_cleanup_rejects_non_development_settings(monkeypatch):
    monkeypatch.setenv("DJANGO_SETTINGS_MODULE", "config.settings.production")
    with pytest.raises(RuntimeError, match="config.settings.development"):
        require_local_cleanup_settings()


def test_local_cleanup_is_safe_inside_a_browser_event_loop():
    """Playwright keeps an asyncio loop active during synchronous fixture teardown."""
    email = f"qa-e2e-{uuid4().hex}@example.invalid"

    async def browser_teardown():
        delete_local_qa_users([email])

    asyncio.run(browser_teardown())
