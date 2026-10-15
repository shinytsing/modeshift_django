"""Safe, disposable identities for authentication journeys."""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse
from uuid import uuid4


@dataclass(frozen=True)
class QaCredentials:
    """An identity that is recognisable as test data in local development."""

    email: str
    password: str


def new_qa_credentials() -> QaCredentials:
    """Return a unique allauth-compatible identity without using a real address."""
    identifier = uuid4().hex
    return QaCredentials(
        email=f"qa-e2e-{identifier}@example.invalid",
        password=f"QaFlow!{identifier[:12]}",
    )


def auth_mutations_are_allowed(base_url: str) -> bool:
    """Only local QA accounts can be removed through this suite's ORM teardown."""
    parsed = urlparse(base_url)
    return parsed.scheme == "http" and parsed.hostname in {"127.0.0.1", "localhost", "::1"}
