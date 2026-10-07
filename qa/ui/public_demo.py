"""Read-only Playwright journey shared by the QA gate and resume demo button."""

from __future__ import annotations

import base64
import json
import os
import re
import shutil
import sys
from pathlib import Path

from playwright.sync_api import Page, expect, sync_playwright

from qa.ui.pages.resume import ResumePage


def run_resume_journey(page: Page, base_url: str) -> list[str]:
    """Exercise public pages only: no sign-up, login, writes, or external load."""
    resume = ResumePage(page, base_url)
    resume.open()
    expect(page.get_by_role("heading", name=re.compile("高杰.*测试开发工程师"))).to_be_visible()
    expect(page.get_by_role("link", name="下载简历 PDF")).to_have_attribute("href", "/resume-3d/download/")
    steps = ["打开简历页：标题与 PDF 下载入口可见"]

    resume.open_automation()
    expect(page.get_by_role("dialog", name="UI 自动化展示")).to_be_visible()
    expect(resume.run_button).to_be_visible()
    steps.append("点击 UI 自动化卡片：技能详情与执行按钮可见")

    resume.close_skill()
    resume.open_skill("JMeter · Locust")
    expect(resume.dialog.get_by_text("高途 Coding-Link WebSocket 音频会话", exact=False).first).to_be_visible()
    resume.dialog.get_by_role("link", name="查看 Locust 原页面").click()
    expect(page).to_have_url(f"{base_url}/resume-3d/performance/#locust")
    expect(page.get_by_role("heading", name="Locust：高途多用户音频会话")).to_be_visible()
    image = page.get_by_role("img", name=re.compile("Locust 历史控制台原貌"))
    expect(image).to_be_visible()
    expect(image).not_to_have_js_property("naturalWidth", 0, timeout=10_000)
    steps.append("打开性能案例：Locust 历史图片已加载，无 404")
    return steps


def main() -> int:
    base_url = os.environ.get("BASE_URL", "http://127.0.0.1:8000").rstrip("/")
    headless = os.environ.get("QA_DEMO_HEADED") != "1"
    chromium_path = os.environ.get("QA_CHROMIUM_EXECUTABLE")
    if not chromium_path and sys.platform == "linux":
        chromium_path = shutil.which("chromium")
    if not chromium_path and sys.platform == "darwin":
        chrome = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
        chromium_path = str(chrome) if chrome.exists() else None
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(
                headless=headless,
                executable_path=chromium_path,
                slow_mo=700,  # Demo-only pacing; the CI test calls run_resume_journey without delay.
                args=["--no-sandbox"] if sys.platform == "linux" else [],
            )
            try:
                page = browser.new_page(viewport={"width": 1440, "height": 900})
                steps = run_resume_journey(page, base_url)
                screenshot = base64.b64encode(page.screenshot()).decode("ascii")
                print(json.dumps({"status": "passed", "steps": steps, "screenshot": screenshot}, ensure_ascii=False))
                return 0
            finally:
                browser.close()
    except Exception as exc:
        print(json.dumps({"status": "failed", "error": f"{type(exc).__name__}: {exc}"}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
