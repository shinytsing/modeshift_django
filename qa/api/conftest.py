"""Shared HTTP client for contract-focused QA tests."""

from __future__ import annotations

from urllib.parse import urlsplit

import allure
import pytest
import requests

from qa.api.clients.auth import AuthApi
from qa.api.clients.dashboard import DashboardApi
from qa.api.clients.fitness import FitnessApi
from qa.api.clients.resume import ResumeApi
from qa.api.clients.transport import ApiTransport


@pytest.fixture
def http_session() -> requests.Session:
    """Isolate cookies per test and attach exercised APIs to Allure."""
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
    yield session
    session.close()


@pytest.fixture
def api_transport(http_session: requests.Session, base_url: str) -> ApiTransport:
    return ApiTransport(http_session, base_url)


@pytest.fixture
def auth_api(api_transport: ApiTransport) -> AuthApi:
    return AuthApi(api_transport)


@pytest.fixture
def dashboard_api(api_transport: ApiTransport) -> DashboardApi:
    return DashboardApi(api_transport)


@pytest.fixture
def fitness_api(api_transport: ApiTransport) -> FitnessApi:
    return FitnessApi(api_transport)


@pytest.fixture
def resume_api(api_transport: ApiTransport) -> ResumeApi:
    return ResumeApi(api_transport)
