"""Persistent per-user creator mail settings and atomic daily send reservations."""

from copy import deepcopy
from zoneinfo import ZoneInfo

from django.utils import timezone
from django.conf import settings

from apps.tools.models import SocialMediaSubscription

KEY = "creator_email_policy"
DAILY_LIMIT = 3


class EmailLimitError(RuntimeError):
    pass


def _anchor(user_id):
    return SocialMediaSubscription.objects.filter(user_id=user_id).order_by("pk").first()


def get_email(user_id):
    anchor = _anchor(user_id)
    if not anchor:
        return ""
    data = anchor.last_profile_data or {}
    if KEY in data:
        return data[KEY].get("email", "")
    # Existing users keep one deterministic address until they save shared settings.
    for item in SocialMediaSubscription.objects.filter(user_id=user_id).order_by("pk"):
        for key in ("xhs_agent", "creator_agent"):
            email = ((item.last_profile_data or {}).get(key) or {}).get("alert_email")
            if email:
                return email
    return ""


def _update(user_id, change):
    for _ in range(20):
        anchor = _anchor(user_id)
        if anchor is None:
            raise EmailLimitError("请先关注一个用户")
        old = anchor.last_profile_data
        data = deepcopy(old or {})
        policy = data.setdefault(KEY, {"email": get_email(user_id)})
        change(policy)
        # Compare-and-swap also protects SQLite, where select_for_update is a no-op.
        if SocialMediaSubscription.objects.filter(pk=anchor.pk, last_profile_data=old).update(last_profile_data=data):
            return
    raise EmailLimitError("邮箱设置正在更新，请稍后重试")


def set_email(user_id, email):
    _update(user_id, lambda policy: policy.update(email=email))


def reserve_send(user_id):
    # Local test runs need to exercise multiple notification types in one
    # session. Production keeps the persistent daily cap.
    if getattr(settings, "DEBUG", False):
        return
    today = timezone.now().astimezone(ZoneInfo("Asia/Shanghai")).date().isoformat()

    def reserve(policy):
        used = int(policy.get("used", 0)) if policy.get("date") == today else 0
        if used >= DAILY_LIMIT:
            raise EmailLimitError("今日邮件已达 3 封上限，请明天再试")
        policy.update(date=today, used=used + 1)

    _update(user_id, reserve)
