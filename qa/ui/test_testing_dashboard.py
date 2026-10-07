"""Playwright smoke checks for the public testing dashboard."""

from __future__ import annotations

import re

import allure
import pytest
from playwright.sync_api import Page, expect
from qa.ui.pages.dashboard import TestingDashboardPage


@pytest.mark.ui
@allure.epic("QAToolBox 左移质量门禁")
@allure.feature("UI 自动化 - Playwright")
@allure.story("测试看板端到端冒烟")
def test_dashboard_renders_the_quality_console_and_its_live_summary(page: Page, base_url: str) -> None:
    """A user sees the dashboard identity and an API-populated functional-test total."""
    with allure.step("打开测试手法展示中心"):
        dashboard = TestingDashboardPage(page, base_url)
        dashboard.open()

    with allure.step("验证页面身份与接口渲染结果"):
        expect(page).to_have_title(re.compile(r"测试手法展示 - ModeShift$"))
        expect(page.get_by_role("heading", name="测试手法展示中心")).to_be_visible()
        expect(dashboard.total("functional-tests")).to_have_text("50")

    allure.attach(
        page.screenshot(full_page=False),
        name="testing-dashboard.png",
        attachment_type=allure.attachment_type.PNG,
    )


@pytest.mark.ui
@allure.epic("QAToolBox 左移质量门禁")
@allure.feature("UI 自动化 - Playwright")
@allure.story("空选择前端拦截")
def test_dashboard_blocks_execution_when_no_test_type_is_selected(page: Page, base_url: str) -> None:
    """A user receives immediate feedback instead of sending an empty test run request."""
    dashboard = TestingDashboardPage(page, base_url)
    dashboard.open()

    with allure.step("取消全部默认选择"):
        dashboard.deselect_test_type("功能测试")
        dashboard.deselect_test_type("接口测试")
        expect(dashboard.selected_test_type("功能测试")).not_to_be_checked()
        expect(dashboard.selected_test_type("接口测试")).not_to_be_checked()

    with allure.step("执行空选择并验证前端阻断提示"):
        dialog_messages: list[str] = []

        def accept_dialog(dialog) -> None:
            dialog_messages.append(dialog.message)
            dialog.accept()

        page.once("dialog", accept_dialog)
        dashboard.run_button.click()
        assert dialog_messages == ["请至少选择一个测试类型"]

    allure.attach(
        page.screenshot(full_page=False),
        name="empty-selection-guard.png",
        attachment_type=allure.attachment_type.PNG,
    )


@pytest.mark.ui
@allure.epic("QAToolBox 左移质量门禁")
@allure.feature("UI 自动化 - Playwright")
@allure.story("看板统计渲染")
def test_dashboard_renders_each_api_provided_summary_total(page: Page, base_url: str) -> None:
    """The visible cards must render the exact totals returned by the statistics API."""
    dashboard = TestingDashboardPage(page, base_url)
    dashboard.open()

    with allure.step("验证五类看板统计的用户可见数值"):
        expect(dashboard.total("functional-tests")).to_have_text("50")
        expect(dashboard.total("api-tests")).to_have_text("80")
        expect(dashboard.total("performance-tests")).to_have_text("60")
        expect(dashboard.total("security-tests")).to_have_text("40")
        expect(dashboard.total("success-rate")).to_have_text("90%")


@pytest.mark.ui
@allure.epic("QAToolBox 左移质量门禁")
@allure.feature("UI 自动化 - Playwright")
@allure.story("已选测试类型执行")
def test_dashboard_submits_only_the_user_selected_test_type(page: Page, base_url: str) -> None:
    """Selecting API only sends that exact scope to the real dashboard runner endpoint."""
    dashboard = TestingDashboardPage(page, base_url)
    dashboard.open()
    dashboard.deselect_test_type("功能测试")
    expect(dashboard.selected_test_type("接口测试")).to_be_checked()

    with allure.step("仅执行接口测试并观察真实请求"):
        response = dashboard.run()
    assert response.status == 200
    assert response.json()["test_types"] == ["api"]

    with allure.step("验证看板恢复可执行状态"):
        expect(dashboard.status).to_have_text("就绪", timeout=5_000)
        expect(dashboard.run_button).to_be_enabled()
