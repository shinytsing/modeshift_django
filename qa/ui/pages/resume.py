"""Public resume page and its executable skill dialog."""

from __future__ import annotations

import re

from playwright.sync_api import Download, Locator, Response

from qa.ui.pages.base import BasePage


class ResumePage(BasePage):
    def open(self) -> None:
        self.navigate("/resume-3d/")

    @property
    def automation_card(self) -> Locator:
        return self.page.get_by_role("button", name=re.compile("Pytest.*Playwright"))

    @property
    def dialog(self) -> Locator:
        return self.page.get_by_role("dialog")

    @property
    def run_button(self) -> Locator:
        return self.dialog.get_by_role("button", name="执行 UI 自动化", exact=True)

    @property
    def execution_status(self) -> Locator:
        return self.page.get_by_role("status")

    def skill_card(self, name: str) -> Locator:
        return self.page.get_by_role("button", name=re.compile(re.escape(name).replace(r"\ ", ".*")))

    def open_automation(self) -> None:
        self.automation_card.click()

    def open_skill(self, name: str) -> None:
        self.skill_card(name).click()

    def close_skill(self) -> None:
        self.page.get_by_role("button", name="关闭技能展示").click()

    def download_pdf(self) -> Download:
        with self.page.expect_download() as download_info:
            self.page.get_by_role("link", name="下载简历 PDF").click()
        return download_info.value

    def run_ui_demo(self) -> Response:
        with self.page.expect_response(lambda response: response.url.endswith("/resume-3d/run-ui/"), timeout=100_000) as info:
            self.run_button.click()
        return info.value
