"""Open the persistent User Search browser session for one-time QR login."""

import os
from playwright.sync_api import sync_playwright

profile = os.environ.get("XHS_USER_SEARCH_PROFILE", os.path.expanduser("~/.modeshift/xhs-user-search"))
with sync_playwright() as pw:
    context = pw.chromium.launch_persistent_context(
        profile,
        headless=False,
        channel=os.environ.get("XHS_USER_SEARCH_BROWSER", "chrome"),
    )
    page = context.pages[0] if context.pages else context.new_page()
    page.goto("https://www.xiaohongshu.com/explore", wait_until="domcontentloaded", timeout=60000)
    print("User Search 浏览器已打开，请扫码登录；登录完成后保持窗口打开或关闭即可保存会话。", flush=True)
    page.wait_for_timeout(300000)
    context.close()
