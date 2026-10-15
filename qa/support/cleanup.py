"""Remove only identities created by this QA run from the local Django database."""

from __future__ import annotations

import os
import re
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor


QA_EMAIL = re.compile(r"qa-(?:e2e-[0-9a-f]{32}|template-[0-9a-f]{12})@example\.invalid\Z")


def require_local_cleanup_settings() -> None:
    """Never use a production Django configuration for ORM cleanup."""
    configured = os.getenv("DJANGO_SETTINGS_MODULE", "config.settings.development")
    if configured != "config.settings.development":
        raise RuntimeError("QA user cleanup requires config.settings.development")


def delete_local_qa_users(emails: Iterable[str]) -> None:
    """Delete exact generated identities, never a broad QA prefix or remote data."""
    identities = set(emails)
    if not identities:
        return
    if any(QA_EMAIL.fullmatch(email) is None for email in identities):
        raise ValueError("Refusing to delete an identity outside the generated QA namespace")

    require_local_cleanup_settings()
    # Playwright's sync facade can leave an event loop running in this thread.
    # Keep ORM work in its own thread rather than disabling Django's async guard.
    with ThreadPoolExecutor(max_workers=1) as executor:
        executor.submit(_delete_users, identities).result()


def _delete_users(identities: set[str]) -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
    import django
    from django.apps import apps
    from django.contrib.auth import get_user_model
    from django.db import connections

    if not apps.ready:
        django.setup()
    try:
        user_model = get_user_model()
        user_model.objects.filter(email__in=identities).delete()
    finally:
        connections.close_all()
