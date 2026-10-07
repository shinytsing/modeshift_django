"""Protected BMI calculator interaction and user-visible result locators."""

from __future__ import annotations

from playwright.sync_api import Locator, Response

from qa.ui.pages.base import BasePage


class BmiPage(BasePage):
    def open(self) -> None:
        self.navigate("/tools/fitness/tools/bmi-calculator/")

    @property
    def result_section(self) -> Locator:
        # The legacy calculator exposes no semantic name for this dynamic panel.
        return self.page.locator("#resultSection")

    @property
    def result_value(self) -> Locator:
        return self.page.locator("#bmiResult")

    def calculate(self, height_cm: str, weight_kg: str) -> Response:
        self.page.get_by_label("身高 (厘米)").fill(height_cm)
        self.page.get_by_label("体重 (公斤)").fill(weight_kg)
        with self.page.expect_response(
            lambda response: response.url.endswith("/tools/api/fitness/bmi/") and response.request.method == "POST"
        ) as response_info:
            self.page.get_by_role("button", name="计算BMI").click()
        return response_info.value
