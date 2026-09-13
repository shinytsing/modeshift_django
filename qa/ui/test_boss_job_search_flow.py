"""Browser contract for the BOSS-only enhanced job-search page."""

from __future__ import annotations

import json
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
@allure.feature("BOSS 单平台求职投递")
@allure.story("页面只显示 BOSS 并进入扫码登录步骤")
def test_enhanced_job_search_exposes_only_boss_qr_flow(page: Page) -> None:
    if not auth_mutations_are_allowed(os.getenv("BASE_URL", "http://127.0.0.1:8000")):
        pytest.skip("页面需要本地 QA 登录；非本机目标需设置 QA_ALLOW_AUTH_MUTATIONS=1")

    credentials = new_qa_credentials()
    page.goto(_url("/accounts/signup/"), wait_until="domcontentloaded")
    page.get_by_label("电子邮件:").fill(credentials.email)
    page.get_by_label("密码:").fill(credentials.password)
    page.get_by_role("button", name=re.compile("注册")).click()
    expect(page).to_have_url(re.compile(r"/$"))

    page.goto(_url("/tools/job-search/enhanced/"), wait_until="domcontentloaded")
    expect(page.get_by_role("heading", name="增强版AI一键投递系统")).to_be_visible()
    expect(page.get_by_role("button", name="BOSS直聘")).to_be_visible()
    expect(page.locator("body")).not_to_contain_text("猎聘")
    expect(page.locator("body")).not_to_contain_text("拉勾")
    expect(page.locator("body")).not_to_contain_text("智联")
    expect(page.locator("body")).not_to_contain_text("多平台")

    page.get_by_role("button", name="BOSS直聘").click()
    page.get_by_label("搜索关键词").fill("Python")
    page.get_by_label("工作城市").select_option("北京")
    page.get_by_role("button", name="下一步：登录验证").click()

    expect(page.get_by_role("button", name=re.compile("扫码登录 BOSS"))).to_be_visible()
    expect(page.get_by_text("手机号登录", exact=True)).to_have_count(0)

    qr_login_calls = []

    def fulfill_qr_login(route):
        qr_login_calls.append(len(qr_login_calls) + 1)
        route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps({
                "success": True,
                "qr_code_url": "data:image/png;base64,"
                "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=",
                "expires_in": 10,
            }),
        )

    page.route("**/tools/job-search/api/boss-qr-login/", fulfill_qr_login)
    page.route(
        "**/tools/job-search/api/boss-status-check/",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps({"success": True, "is_logged_in": False, "qr_status": "waiting_scan"}),
        ),
    )
    page.get_by_role("button", name=re.compile("扫码登录 BOSS")).click()
    expect(page.get_by_text(re.compile(r"二维码将在 \d+ 秒后自动刷新"))).to_be_visible()
    assert qr_login_calls == [1]
