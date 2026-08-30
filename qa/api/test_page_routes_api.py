"""Smoke contracts for browser routes that must render from tracked templates."""

from __future__ import annotations

import allure
import pytest
import requests


@pytest.mark.api
@allure.epic("QAToolBox 左移质量门禁")
@allure.feature("API 自动化 - requests")
@allure.story("测试用例生成页面可用性")
def test_test_case_generator_page_renders_from_the_deployment_template(
    base_url: str, http_session: requests.Session
) -> None:
    """The linked tool page must not become a production 500 due to a missing template."""
    with allure.step("访问测试用例生成页面"):
        response = http_session.get(f"{base_url}/tools/test_case_generator/", timeout=3)

    assert response.status_code == 200
    assert response.headers["Content-Type"].startswith("text/html")
    assert 'id="testForm"' in response.text
