"""Shared HTTP client for contract-focused QA tests."""

from __future__ import annotations

import os
from urllib.parse import urlsplit

import allure
import pytest
import requests


@pytest.fixture(scope="session")
def base_url() -> str:
    """Return the target environment without hardcoding a host into a test."""
    return os.getenv("BASE_URL", "http://127.0.0.1:8000").rstrip("/")


@pytest.fixture(scope="session")
def http_session() -> requests.Session:
    """Provide a reusable client and attach every exercised API to Allure."""
    session = requests.Session()
    session.headers.update({"User-Agent": "qatoolbox-qa-suite/1.0"})

    def attach_api_evidence(response: requests.Response, *args, **kwargs) -> requests.Response:
        """Make the endpoint, result status, and JSON response visible in the report."""
        request = response.request
        route = urlsplit(request.url).path
        allure.attach(
            f"{request.method} {route}\nHTTP {response.status_code}\nContent-Type: {response.headers.get('Content-Type', '')}",
            name=f"API 执行记录 - {request.method} {route}",
            attachment_type=allure.attachment_type.TEXT,
        )
        if response.headers.get("Content-Type", "").startswith("application/json"):
            allure.attach(
                response.text,
                name=f"API 响应 - {request.method} {route}",
                attachment_type=allure.attachment_type.JSON,
            )
        return response

    session.hooks["response"].append(attach_api_evidence)
    return session
