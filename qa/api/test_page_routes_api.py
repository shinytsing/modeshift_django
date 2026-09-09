"""Smoke contracts for browser routes that must render from tracked templates."""

from __future__ import annotations

from uuid import uuid4

import allure
import pytest
import requests

from qa.support.auth import auth_mutations_are_allowed


@pytest.mark.api
@allure.epic("QAToolBox 左移质量门禁")
@allure.feature("API 自动化 - requests")
@allure.story("测试用例生成页面可用性")
def test_test_case_generator_page_renders_from_the_deployment_template(base_url: str, http_session: requests.Session) -> None:
    """The linked tool page must not become a production 500 due to a missing template."""
    if not auth_mutations_are_allowed(base_url):
        pytest.skip("页面受登录保护；非本机目标不创建 QA 用户")

    username = f"qa-template-{uuid4().hex[:12]}"
    with allure.step("注册用于访问受保护工具页的 QA 用户"):
        registration = http_session.post(
            f"{base_url}/users/api/register/",
            json={"username": username, "password": "QaTemplate123!", "email": f"{username}@example.invalid"},
            timeout=3,
        )
    assert registration.status_code == 200

    with allure.step("在已登录会话中访问测试用例生成页面"):
        response = http_session.get(f"{base_url}/tools/test_case_generator/", allow_redirects=False, timeout=3)

    assert response.status_code == 200
    assert response.headers["Content-Type"].startswith("text/html")
    assert 'id="testForm"' in response.text
