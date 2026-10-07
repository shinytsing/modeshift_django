"""Smoke contracts for browser routes that must render from tracked templates."""

from __future__ import annotations

from uuid import uuid4

import allure
import pytest

from qa.api.clients.auth import AuthApi
from qa.api.clients.transport import ApiTransport
from qa.support.auth import auth_mutations_are_allowed


@pytest.mark.api
@allure.epic("QAToolBox 左移质量门禁")
@allure.feature("API 自动化 - requests")
@allure.story("测试用例生成页面可用性")
def test_test_case_generator_page_renders_from_the_deployment_template(
    base_url: str, auth_api: AuthApi, api_transport: ApiTransport
) -> None:
    """The linked tool page must not become a production 500 due to a missing template."""
    if not auth_mutations_are_allowed(base_url):
        pytest.skip("页面受登录保护；非本机目标不创建 QA 用户")

    username = f"qa-template-{uuid4().hex[:12]}"
    with allure.step("注册用于访问受保护工具页的 QA 用户"):
        registration = auth_api.register_json(username, "QaTemplate123!", f"{username}@example.invalid")
    assert registration.status_code == 200

    # Keep this contract independent of whether a reverse proxy forwards the
    # auto-login Set-Cookie from registration; the page itself is protected.
    with allure.step("显式登录 QA 用户以访问受保护工具页"):
        login = auth_api.login_json(username, "QaTemplate123!")
    assert login.status_code == 200

    with allure.step("在已登录会话中访问测试用例生成页面"):
        response = api_transport.get("/tools/test_case_generator/", allow_redirects=False)

    assert response.status_code == 200
    assert response.headers["Content-Type"].startswith("text/html")
    assert 'id="requirement"' in response.text
    assert 'id="userPrompt"' in response.text
    assert 'id="generationModel"' in response.text
    assert 'id="knowledgeQuery"' in response.text
    assert 'id="generateButton"' in response.text
