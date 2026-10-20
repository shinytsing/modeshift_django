"""Browser-session user search adapter for Xiaohongshu's web usersearch API."""

from __future__ import annotations

import os
import json
import subprocess
from urllib.parse import quote

from apps.tools.services.xiaohongshu_profile_agent import XhsServiceError


def search_users(keyword: str) -> list[dict]:
    """Search users in an already authenticated persistent browser profile.

    The page generates the short-lived request signatures; this adapter only
    observes the response and never stores cookies or signatures in the app.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise XhsServiceError("User Search 浏览器适配器缺少 Playwright") from exc

    profile = os.environ.get("XHS_USER_SEARCH_PROFILE", os.path.expanduser("~/.modeshift/xhs-user-search"))
    url = f"https://www.xiaohongshu.com/search_result?keyword={quote(keyword)}&type=51"
    response_data = {}
    try:
        with sync_playwright() as pw:
            context = pw.chromium.launch_persistent_context(
                profile,
                headless=True,
                channel=os.environ.get("XHS_USER_SEARCH_BROWSER", "chrome"),
                args=["--disable-blink-features=AutomationControlled"],
            )
            _sync_official_mcp_cookies(context)
            page = context.pages[0] if context.pages else context.new_page()

            def capture(response):
                nonlocal response_data
                if "/api/sns/web/v1/search/usersearch" not in response.url:
                    return
                try:
                    payload = response.json()
                    if isinstance(payload, dict):
                        response_data = payload
                except Exception:
                    return

            page.on("response", capture)
            page.goto(url, wait_until="domcontentloaded", timeout=15000)
            # The web app issues usersearch after hydration; allow a short
            # window for that request while avoiding a long agent stall.
            page.wait_for_timeout(8000)
            if "/login" in page.url and not response_data:
                raise XhsServiceError("User Search 登录态已过期，请重新扫码")
            context.close()
    except Exception as exc:
        raise XhsServiceError("User Search 浏览器会话不可用，请先在该 Profile 扫码登录") from exc

    if response_data.get("code") in (-100, 401):
        raise XhsServiceError("User Search 登录态已过期，请重新扫码")
    return _normalize(response_data)


def _normalize(payload: dict) -> list[dict]:
    data = payload.get("data") if isinstance(payload.get("data"), dict) else payload
    raw = data.get("users") or data.get("user_list") or data.get("userList") or data.get("items") or []
    result = []
    for item in raw if isinstance(raw, list) else []:
        if not isinstance(item, dict):
            continue
        user = item.get("user") if isinstance(item.get("user"), dict) else item
        user_id = user.get("user_id") or user.get("userId") or user.get("userid") or ""
        nickname = user.get("nickname") or user.get("nick_name") or user.get("nickName") or ""
        if not user_id or not nickname:
            continue
        result.append(
            {
                "user_id": user_id,
                "nickname": nickname,
                "avatar": user.get("avatar") or user.get("avatar_url") or user.get("image") or "",
                "xsec_token": user.get("xsec_token") or user.get("xsecToken") or "",
                "source_note": "User Search",
            }
        )
    return result[:10]


def _sync_official_mcp_cookies(context) -> None:
    """Import the official MCP's persisted cookies before the web request."""
    try:
        output = subprocess.check_output(
            ["docker", "exec", "xiaohongshu-mcp", "cat", "/app/data/cookies.json"],
            timeout=5,
            text=True,
        )
        payload = json.loads(output)
        cookies = []
        for cookie in payload.get("cookies", []):
            if not cookie.get("name") or not cookie.get("value"):
                continue
            item = {
                "name": cookie["name"],
                "value": cookie["value"],
                "domain": cookie.get("domain") or ".xiaohongshu.com",
                "path": cookie.get("path") or "/",
            }
            if cookie.get("expires", 0) > 0:
                item["expires"] = cookie["expires"]
            cookies.append(item)
        if cookies:
            context.add_cookies(cookies)
    except (OSError, subprocess.SubprocessError, ValueError, TypeError):
        return
