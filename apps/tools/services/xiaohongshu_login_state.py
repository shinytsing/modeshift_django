"""Persist the last observed Xiaohongshu MCP login state without credentials."""

from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from apps.tools.models import SocialMediaPlatformConfig
from apps.tools.services import xiaohongshu_profile_agent as agent


STATE_KEY = "mcp_login_state"


def _save(status: str, *, username: str = "", error: str = "") -> dict:
    now = timezone.now().isoformat()
    with transaction.atomic():
        config, _ = SocialMediaPlatformConfig.objects.select_for_update().get_or_create(
            platform="xiaohongshu", defaults={"name": "小红书"}
        )
        crawler_config = config.crawler_config or {}
        previous = crawler_config.get(STATE_KEY) or {}
        state = {
            "status": status,
            "checked_at": now,
            "username": username if status == "logged_in" else "",
            "error": error[:300] if status == "error" else "",
            "last_success_at": now if status == "logged_in" else previous.get("last_success_at"),
        }
        crawler_config[STATE_KEY] = state
        config.crawler_config = crawler_config
        config.save(update_fields=["crawler_config", "updated_at"])
    return state


def check_and_store() -> dict:
    """Return a fresh state, keeping the last success only as historical context."""
    try:
        live = agent.login_status()
    except agent.XhsServiceError as exc:
        state = _save("error", error=str(exc))
        return {**state, "is_logged_in": False}
    status = "logged_in" if live["is_logged_in"] else "logged_out"
    state = _save(status, username=live.get("username") or "")
    return {**state, "is_logged_in": status == "logged_in"}


def saved_status() -> dict:
    config = SocialMediaPlatformConfig.objects.filter(platform="xiaohongshu").only("crawler_config").first()
    state = ((config.crawler_config or {}).get(STATE_KEY) or {}) if config else {}
    return {**state, "is_logged_in": state.get("status") == "logged_in"}
