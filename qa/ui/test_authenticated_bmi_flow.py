"""Visible Playwright journey for the real registration and fitness-tool workflow."""

from __future__ import annotations

import re

import allure
import pytest
from playwright.sync_api import Page, expect

from qa.support.auth import auth_mutations_are_allowed, new_qa_credentials
from qa.ui.pages.auth import LoginPage, ProfilePage, SessionPage, SignupPage
from qa.ui.pages.fitness import BmiPage


@pytest.mark.ui
@pytest.mark.e2e
@allure.epic("QAToolBox 左移质量门禁")
@allure.feature("UI 自动化 - Playwright")
@allure.story("注册登录后使用受保护的 BMI 工具")
def test_user_registers_logs_in_and_calculates_bmi_through_the_visible_ui(page: Page, base_url: str) -> None:
    """A new user can complete the portfolio's core auth-to-feature journey in a real browser."""
    if not auth_mutations_are_allowed(base_url):
        pytest.skip("认证场景会创建 QA 数据；非本机目标需设置 QA_ALLOW_AUTH_MUTATIONS=1")

    credentials = new_qa_credentials()
    signup = SignupPage(page, base_url)
    session = SessionPage(page, base_url)
    login = LoginPage(page, base_url)
    profile = ProfilePage(page, base_url)
    bmi = BmiPage(page, base_url)

    with allure.step("使用可见注册表单创建 QA 用户"):
        signup.open()
        signup.register(credentials.email, credentials.password)
        expect(page).to_have_url(re.compile(r"/$"))

    with allure.step("退出后用同一身份回归登录"):
        session.sign_out()
        expect(page).to_have_url(re.compile(r"/$"))
        login.open()
        login.sign_in(credentials.email, credentials.password)
        expect(page).to_have_url(re.compile(r"/$"))

    with allure.step("访问受保护个人资料并确认登录身份"):
        profile.open()
        expect(page).to_have_url(re.compile(r"/users/profile/$"))
        expect(profile.email(credentials.email)).to_be_visible()

    with allure.step("在受保护 BMI 页面提交身高体重并接收真实接口结果"):
        bmi.open()
        expect(page.get_by_role("heading", name="BMI计算器")).to_be_visible()
        bmi_response = bmi.calculate("170", "65")

    assert bmi_response.status == 200
    assert bmi_response.json()["data"]["bmi"] == 22.5
    expect(bmi.result_section).to_be_visible()
    expect(bmi.result_value).to_contain_text("22.5")
    expect(bmi.result_value).to_contain_text("正常体重")
    expect(page.get_by_role("heading", name="正常体重")).to_be_visible()
    allure.attach(
        page.screenshot(full_page=True), name="authenticated-bmi-result.png", attachment_type=allure.attachment_type.PNG
    )
