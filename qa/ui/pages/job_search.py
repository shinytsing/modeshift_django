"""BOSS-only enhanced job-search page interactions."""

from __future__ import annotations

import re

from playwright.sync_api import Locator

from qa.ui.pages.base import BasePage


class JobSearchPage(BasePage):
    def open(self) -> None:
        self.navigate("/tools/job-search/enhanced/")

    @property
    def boss_button(self) -> Locator:
        return self.page.get_by_role("button", name="BOSS直聘")

    @property
    def qr_login_button(self) -> Locator:
        return self.page.get_by_role("button", name=re.compile("扫码登录 BOSS"))

    def choose_boss(self, keyword: str, city: str) -> None:
        self.boss_button.click()
        self.page.get_by_label("搜索关键词").fill(keyword)
        self.page.get_by_label("工作城市").select_option(city)
        self.page.get_by_role("button", name="下一步：登录验证").click()

    def request_qr_login(self) -> None:
        self.qr_login_button.click()
