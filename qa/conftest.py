"""Shared QA environment fixtures for both API and browser contracts."""

from __future__ import annotations

import os

import pytest

from qa.support.cleanup import delete_local_qa_users, require_local_cleanup_settings


@pytest.fixture(scope="session")
def base_url() -> str:
    """The single target selected by the local runner or CI gate."""
    return os.getenv("BASE_URL", "http://127.0.0.1:8000").rstrip("/")


@pytest.fixture
def qa_user_cleanup(base_url: str):
    """Register before signup so teardown also runs after a failed assertion."""
    from qa.support.auth import auth_mutations_are_allowed

    if not auth_mutations_are_allowed(base_url):
        pytest.skip("Stateful QA users require a local target with ORM cleanup")
    require_local_cleanup_settings()
    emails: list[str] = []
    yield emails.append
    delete_local_qa_users(emails)
