"""Allure evidence collected automatically for successful browser scenarios."""

from __future__ import annotations

import allure
import pytest
from playwright.sync_api import Page


@pytest.fixture(autouse=True)
def expose_page_for_allure_evidence(page: Page, request: pytest.FixtureRequest):
    """Keep the live Playwright page available to the test-result hook."""
    request.node.qa_page = page
    yield


@pytest.hookimpl(hookwrapper=True, trylast=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[None]):
    """Attach the final page while Allure still owns the passed test result."""
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.passed:
        page = getattr(item, "qa_page", None)
        if page is not None:
            allure.attach(
                page.screenshot(full_page=True),
                name="成功页面截图",
                attachment_type=allure.attachment_type.PNG,
            )
