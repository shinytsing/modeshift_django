"""Shared QA environment fixtures for both API and browser contracts."""

from __future__ import annotations

import os

import pytest


@pytest.fixture(scope="session")
def base_url() -> str:
    """The single target selected by the local runner or CI gate."""
    return os.getenv("BASE_URL", "http://127.0.0.1:8000").rstrip("/")
