"""Testing dashboard controls and rendered summary locators."""

from __future__ import annotations

from playwright.sync_api import Locator, Response

from qa.ui.pages.base import BasePage


class TestingDashboardPage(BasePage):
    __test__ = False  # Page object, not a pytest test class.

    def open(self) -> None:
        self.navigate("/testing-dashboard/")

    @property
    def run_button(self) -> Locator:
        return self.page.get_by_role("button", name="执行测试")

    @property
    def status(self) -> Locator:
        # The legacy dashboard exposes status only by a stable ID.
        return self.page.locator("#test-status")

    def total(self, category: str) -> Locator:
        return self.page.locator(f"#{category}")

    def selected_test_type(self, name: str) -> Locator:
        return self.page.get_by_label(name)

    def deselect_test_type(self, name: str) -> None:
        self.selected_test_type(name).uncheck()

    def run(self) -> Response:
        with self.page.expect_response(
            lambda response: response.url.endswith("/api/tests/run/") and response.request.method == "POST",
            timeout=3_000,
        ) as info:
            self.run_button.click()
        return info.value
