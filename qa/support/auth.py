"""Safe, disposable identities for authentication journeys."""

from __future__ import annotations

import os
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
    """Allow account creation only locally unless an operator explicitly opts in."""
    hostname = urlparse(base_url).hostname
    if hostname in {"127.0.0.1", "localhost", "::1"}:
        return True
    return os.getenv("QA_ALLOW_AUTH_MUTATIONS", "").lower() in {"1", "true", "yes"}
