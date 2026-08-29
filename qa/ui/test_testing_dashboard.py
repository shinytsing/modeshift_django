"""Playwright smoke checks for the public testing dashboard."""

from __future__ import annotations

import os
import re

import allure
import pytest
from playwright.sync_api import Page, expect


def _dashboard_url() -> str:
    return f"{os.getenv('BASE_URL', 'http://127.0.0.1:8000').rstrip('/')}/testing-dashboard/"


@pytest.mark.ui
@allure.epic("QAToolBox 左移质量门禁")
@allure.feature("UI 自动化 - Playwright")
@allure.story("测试看板端到端冒烟")
def test_dashboard_renders_the_quality_console_and_its_live_summary(page: Page) -> None:
    """A user sees the dashboard identity and an API-populated functional-test total."""
    with allure.step("打开测试手法展示中心"):
        page.goto(_dashboard_url(), wait_until="domcontentloaded")

    with allure.step("验证页面身份与接口渲染结果"):
        expect(page).to_have_title(re.compile(r"测试手法展示 - ModeShift$"))
        expect(page.get_by_role("heading", name="测试手法展示中心")).to_be_visible()
        expect(page.locator("#functional-tests")).to_have_text("50")

    allure.attach(
        page.screenshot(full_page=False),
        name="testing-dashboard.png",
        attachment_type=allure.attachment_type.PNG,
    )


@pytest.mark.ui
@allure.epic("QAToolBox 左移质量门禁")
@allure.feature("UI 自动化 - Playwright")
@allure.story("空选择前端拦截")
def test_dashboard_blocks_execution_when_no_test_type_is_selected(page: Page) -> None:
    """A user receives immediate feedback instead of sending an empty test run request."""
    page.goto(_dashboard_url(), wait_until="domcontentloaded")

    with allure.step("取消全部默认选择"):
        page.get_by_label("功能测试").uncheck()
        page.get_by_label("接口测试").uncheck()
        expect(page.get_by_label("功能测试")).not_to_be_checked()
        expect(page.get_by_label("接口测试")).not_to_be_checked()

    with allure.step("执行空选择并验证前端阻断提示"):
        dialog_messages: list[str] = []

        def accept_dialog(dialog) -> None:
            dialog_messages.append(dialog.message)
            dialog.accept()

        page.once("dialog", accept_dialog)
        page.get_by_role("button", name="执行测试").click()
        assert dialog_messages == ["请至少选择一个测试类型"]

    allure.attach(
        page.screenshot(full_page=False),
        name="empty-selection-guard.png",
        attachment_type=allure.attachment_type.PNG,
    )
