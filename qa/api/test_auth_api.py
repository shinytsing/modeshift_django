"""Non-mutating browser-auth API contracts."""

from __future__ import annotations

import allure
import pytest
import requests


@pytest.mark.api
@allure.epic("QAToolBox 左移质量门禁")
@allure.feature("API 自动化 - requests")
@pytest.mark.parametrize("path", ["/users/api/login/", "/users/api/register/"])
def test_browser_auth_endpoints_return_validation_errors_instead_of_not_found(
    base_url: str, http_session: requests.Session, path: str
) -> None:
    """Modal authentication requests must reach their JSON validation contract."""
    with allure.step(f"提交空请求到 {path}"):
        response = http_session.post(f"{base_url}{path}", json={}, timeout=3)

    assert response.status_code == 400
    assert response.headers["Content-Type"].startswith("application/json")
    body = response.json()
    assert body["success"] is False
    assert body["message"] == "用户名和密码不能为空"
