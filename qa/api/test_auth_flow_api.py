"""Stateful requests journey covering the real allauth and user-profile contracts."""

from __future__ import annotations

import re

import allure
import pytest
import requests

from qa.support.auth import auth_mutations_are_allowed, new_qa_credentials


def _csrf_token(response: requests.Response) -> str:
    """Extract the CSRF value that Django rendered into an allauth form."""
    matched = re.search(r'name="csrfmiddlewaretoken"\s+value="([^"]+)"', response.text)
    assert matched, "Allauth form did not render a CSRF token"
    return matched.group(1)


@pytest.mark.api
@pytest.mark.e2e
@allure.epic("QAToolBox 左移质量门禁")
@allure.feature("API 自动化 - requests")
@allure.story("注册、登录与资料连续场景")
def test_authenticated_session_survives_registration_login_and_profile_operations(
    base_url: str, http_session: requests.Session
) -> None:
    """One browser-equivalent session must transition safely across the complete user journey."""
    if not auth_mutations_are_allowed(base_url):
        pytest.skip("认证场景会创建 QA 数据；非本机目标需设置 QA_ALLOW_AUTH_MUTATIONS=1")

    credentials = new_qa_credentials()
    profile_url = f"{base_url}/users/api/profile/"

    with allure.step("匿名访问资料 API 被拒绝"):
        anonymous_profile = http_session.get(profile_url, timeout=3)
    assert anonymous_profile.status_code == 401
    assert anonymous_profile.json() == {"success": False, "message": "用户未登录"}

    with allure.step("获取注册表单的 CSRF Token"):
        signup_form = http_session.get(f"{base_url}/accounts/signup/", timeout=3)
    assert signup_form.status_code == 200
    signup_token = _csrf_token(signup_form)

    with allure.step("注册唯一 QA 用户并验证自动登录会话"):
        signup = http_session.post(
            f"{base_url}/accounts/signup/",
            data={"email": credentials.email, "password1": credentials.password, "csrfmiddlewaretoken": signup_token},
            headers={"Referer": f"{base_url}/accounts/signup/"},
            allow_redirects=False,
            timeout=3,
        )
    assert signup.status_code == 302
    assert signup.headers["Location"] == "/"

    with allure.step("读取注册后的受保护资料"):
        registered_profile = http_session.get(profile_url, timeout=3)
    assert registered_profile.status_code == 200
    assert registered_profile.json()["data"]["email"] == credentials.email

    with allure.step("通过 API 登出，验证会话确实失效"):
        first_logout = http_session.post(f"{base_url}/users/api/logout/", timeout=3)
    assert first_logout.status_code == 200
    assert first_logout.json()["success"] is True

    with allure.step("获取登录表单的 CSRF Token"):
        login_form = http_session.get(f"{base_url}/accounts/login/", timeout=3)
    assert login_form.status_code == 200
    login_token = _csrf_token(login_form)

    with allure.step("使用刚注册的身份重新登录"):
        login = http_session.post(
            f"{base_url}/accounts/login/",
            data={"login": credentials.email, "password": credentials.password, "csrfmiddlewaretoken": login_token},
            headers={"Referer": f"{base_url}/accounts/login/"},
            allow_redirects=False,
            timeout=3,
        )
    assert login.status_code == 302
    assert login.headers["Location"] == "/"

    with allure.step("更新后读取资料，确认同一登录会话持久化"):
        update = http_session.post(profile_url, json={"first_name": "QA Flow"}, timeout=3)
        refreshed_profile = http_session.get(profile_url, timeout=3)
    assert update.status_code == 200
    assert update.json()["data"]["first_name"] == "QA Flow"
    assert refreshed_profile.status_code == 200
    assert refreshed_profile.json()["data"]["first_name"] == "QA Flow"

    with allure.step("调用业务 BMI 接口并断言连续场景中的功能结果"):
        bmi = http_session.post(f"{base_url}/tools/api/fitness/bmi/", json={"height": 170, "weight": 65}, timeout=3)
    assert bmi.status_code == 200
    assert bmi.json()["success"] is True
    assert bmi.json()["data"]["bmi"] == 22.5
    assert bmi.json()["data"]["category"] == "正常体重"
    allure.attach(bmi.text, name="authenticated-bmi-response.json", attachment_type=allure.attachment_type.JSON)

    with allure.step("最终登出后，同一客户端再次访问资料必须被拒绝"):
        final_logout = http_session.post(f"{base_url}/users/api/logout/", timeout=3)
        final_profile = http_session.get(profile_url, timeout=3)
    assert final_logout.status_code == 200
    assert final_profile.status_code == 401
    allure.attach(final_profile.text, name="logged-out-profile-response.json", attachment_type=allure.attachment_type.JSON)
