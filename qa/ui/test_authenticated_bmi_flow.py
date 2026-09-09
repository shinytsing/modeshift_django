"""Visible Playwright journey for the real registration and fitness-tool workflow."""

from __future__ import annotations

import os
import re

import allure
import pytest
from playwright.sync_api import Page, expect

from qa.support.auth import auth_mutations_are_allowed, new_qa_credentials


def _url(path: str) -> str:
    return f"{os.getenv('BASE_URL', 'http://127.0.0.1:8000').rstrip('/')}{path}"


@pytest.mark.ui
@pytest.mark.e2e
@allure.epic("QAToolBox 左移质量门禁")
@allure.feature("UI 自动化 - Playwright")
@allure.story("注册登录后使用受保护的 BMI 工具")
def test_user_registers_logs_in_and_calculates_bmi_through_the_visible_ui(page: Page) -> None:
    """A new user can complete the portfolio's core auth-to-feature journey in a real browser."""
    base_url = os.getenv("BASE_URL", "http://127.0.0.1:8000").rstrip("/")
    if not auth_mutations_are_allowed(base_url):
        pytest.skip("认证场景会创建 QA 数据；非本机目标需设置 QA_ALLOW_AUTH_MUTATIONS=1")

    credentials = new_qa_credentials()

    with allure.step("使用可见注册表单创建 QA 用户"):
        page.goto(_url("/accounts/signup/"), wait_until="domcontentloaded")
        page.get_by_label("电子邮件:").fill(credentials.email)
        page.get_by_label("密码:").fill(credentials.password)
        page.get_by_role("button", name=re.compile("注册")).click()
        expect(page).to_have_url(re.compile(r"/$"))

    with allure.step("退出后用同一身份回归登录"):
        page.goto(_url("/users/logout/"), wait_until="domcontentloaded")
        expect(page).to_have_url(re.compile(r"/$"))
        page.goto(_url("/accounts/login/"), wait_until="domcontentloaded")
        page.get_by_label("电子邮件:").fill(credentials.email)
        page.get_by_label("密码:").fill(credentials.password)
        page.get_by_role("button", name="登录").click()
        expect(page).to_have_url(re.compile(r"/$"))

    with allure.step("访问受保护个人资料并确认登录身份"):
        page.goto(_url("/users/profile/"), wait_until="domcontentloaded")
        expect(page).to_have_url(re.compile(r"/users/profile/$"))
        expect(page.get_by_text(credentials.email, exact=True)).to_be_visible()

    with allure.step("在受保护 BMI 页面提交身高体重并接收真实接口结果"):
        page.goto(_url("/tools/fitness/tools/bmi-calculator/"), wait_until="domcontentloaded")
        expect(page.get_by_role("heading", name="BMI计算器")).to_be_visible()
        page.get_by_label("身高 (厘米)").fill("170")
        page.get_by_label("体重 (公斤)").fill("65")
        with page.expect_response(
            lambda response: response.url.endswith("/tools/api/fitness/bmi/") and response.request.method == "POST"
        ) as response_info:
            page.get_by_role("button", name="计算BMI").click()

    bmi_response = response_info.value
    assert bmi_response.status == 200
    assert bmi_response.json()["data"]["bmi"] == 22.5
    expect(page.locator("#resultSection")).to_be_visible()
    expect(page.locator("#bmiResult")).to_contain_text("22.5")
    expect(page.locator("#bmiResult")).to_contain_text("正常体重")
    expect(page.get_by_role("heading", name="正常体重")).to_be_visible()
    allure.attach(page.screenshot(full_page=True), name="authenticated-bmi-result.png", attachment_type=allure.attachment_type.PNG)
