"""Shared HTTP client for contract-focused QA tests."""

from __future__ import annotations

import os

import pytest
import requests


@pytest.fixture(scope="session")
def base_url() -> str:
    """Return the target environment without hardcoding a host into a test."""
    return os.getenv("BASE_URL", "http://127.0.0.1:8000").rstrip("/")


@pytest.fixture(scope="session")
def http_session() -> requests.Session:
    """Provide a reusable, identifiable HTTP client for the QA suite."""
    session = requests.Session()
    session.headers.update({"User-Agent": "qatoolbox-qa-suite/1.0"})
    return session
