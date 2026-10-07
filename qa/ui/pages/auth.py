"""User-facing authentication and profile page objects."""

from __future__ import annotations

import re

from playwright.sync_api import Locator

from qa.ui.pages.base import BasePage


class SignupPage(BasePage):
    def open(self) -> None:
        self.navigate("/accounts/signup/")

    def register(self, email: str, password: str) -> None:
        self.page.get_by_label("电子邮件:").fill(email)
        self.page.get_by_label("密码:").fill(password)
        self.page.get_by_role("button", name=re.compile("注册")).click()


class LoginPage(BasePage):
    def open(self) -> None:
        self.navigate("/accounts/login/")

    def sign_in(self, email: str, password: str) -> None:
        self.page.get_by_label("电子邮件:").fill(email)
        self.page.get_by_label("密码:").fill(password)
        self.page.get_by_role("button", name="登录").click()


class ProfilePage(BasePage):
    def open(self) -> None:
        self.navigate("/users/profile/")

    def email(self, address: str) -> Locator:
        return self.page.get_by_text(address, exact=True)


class SessionPage(BasePage):
    def sign_out(self) -> None:
        self.navigate("/users/logout/")
