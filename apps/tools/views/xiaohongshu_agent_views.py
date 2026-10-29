"""Django page and bounded read-only API for Xiaohongshu profiles."""

from __future__ import annotations

import json
import logging
import hashlib
import os
import re
from functools import wraps
from urllib.parse import urlparse

import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.http import JsonResponse
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

from apps.tools.services import xiaohongshu_profile_agent as agent
from apps.tools.services import creator_sources
from apps.tools.services import creator_watch_service as watches
from apps.tools.services import creator_watch_service
from apps.tools.services import xiaohongshu_login_state
from apps.tools.services import xiaohongshu_wecom as wecom
from apps.tools.services.xiaohongshu_delivery import deliver_updates, send_snapshot_email
from apps.tools.services.creator_email_policy import EmailLimitError
from apps.tools.models import SocialMediaSubscription


logger = logging.getLogger(__name__)


def _api_user_required(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        from apps.users.wechat_auth import user_from_token
        from django.contrib.auth.models import User

        token_user = user_from_token(request)
        if token_user is not None:
            request.user = token_user
            return view(request, *args, **kwargs)
        # shortcut: local DEBUG smoke tests only; enable with PEEP_DEBUG_AUTH_BYPASS=1, remove before production.
        if settings.DEBUG and os.getenv("PEEP_DEBUG_AUTH_BYPASS") == "1":
            debug_user, _ = User.objects.get_or_create(username="peep-debug")
            request.user = debug_user
            return view(request, *args, **kwargs)
        if not request.user.is_authenticated:
            return JsonResponse({"error": "请先登录 Model Shift"}, status=401)
        return view(request, *args, **kwargs)

    return wrapped


def _admin_required(request):
    # Local development needs the logged-in tester to complete the shared MCP
    # QR login. Production keeps the existing staff-only restriction.
    if not request.user.is_staff and not settings.DEBUG:
        return JsonResponse({"error": "仅管理员可操作小红书登录"}, status=403)
    return None


def _input(request):
    if len(request.body) > 4096:
        raise agent.XhsInputError("输入内容过长")
    try:
        data = json.loads(request.body or b"{}")
    except (ValueError, UnicodeDecodeError) as exc:
        raise agent.XhsInputError("请求内容不是有效 JSON") from exc
    if not isinstance(data, dict):
        raise agent.XhsInputError("请求内容格式不正确")
    return data


def _throttled(request, action, seconds=8):
    return not cache.add(f"xhs-agent:{request.user.pk}:{action}", True, timeout=seconds)


@login_required
@require_GET
def xiaohongshu_agent_page(request):
    return render(
        request,
        "tools/xiaohongshu_agent.html",
        {
            "can_login_xhs": request.user.is_staff or settings.DEBUG,
        },
    )


@login_required
def xiaohongshu_agent_trends_page(request):
    return render(request, "tools/xiaohongshu_trends.html")


@require_POST
@_api_user_required
def xiaohongshu_agent_search_api(request):
    try:
        data = _input(request)
        keyword = data.get("keyword", "")
        platform = data.get("platform", "xiaohongshu")
        if not isinstance(keyword, str):
            raise agent.XhsInputError("请输入昵称或关键词")
        if _throttled(request, "search", seconds=20):
            return JsonResponse({"error": "查询太频繁，请稍后再试"}, status=429)
        return JsonResponse({"candidates": creator_sources.search_candidates(platform, keyword)})
    except agent.XhsInputError as exc:
        return JsonResponse({"error": str(exc)}, status=400)
    except agent.XhsServiceError as exc:
        return JsonResponse({"error": str(exc)}, status=502)


@require_POST
@_api_user_required
def xiaohongshu_agent_profile_api(request):
    try:
        data = _input(request)
        platform = data.get("platform", "xiaohongshu")
        link = data.get("profile_url", "")
        if link:
            if not isinstance(link, str):
                raise agent.XhsInputError("主页链接格式不正确")
            user_id, token = creator_sources.parse_profile_link(platform, link)
        else:
            user_id, token = data.get("user_id", ""), data.get("xsec_token", "")
        if not isinstance(user_id, str) or not isinstance(token, str):
            raise agent.XhsInputError("用户参数格式不正确")
        if _throttled(request, "profile"):
            return JsonResponse({"error": "查询太频繁，请稍后再试"}, status=429)
        return JsonResponse({"profile": creator_sources.read_profile(platform, user_id, token)})
    except agent.XhsInputError as exc:
        return JsonResponse({"error": str(exc)}, status=400)
    except agent.XhsServiceError as exc:
        return JsonResponse({"error": str(exc)}, status=502)


@require_GET
@_api_user_required
def xiaohongshu_agent_watches_api(request):
    # The Peep panel is shared by every supported platform. Keep the legacy
    # Xiaohongshu serializer and add the generic creator-watch subscriptions.
    xhs_items = [watches.serialize_watch(item) for item in watches.list_watches(request.user)]
    creator_items = [
        creator_watch_service.serialize_watch(item)
        for item in creator_watch_service.list_watches(request.user)
        if item.platform != "xiaohongshu"
    ]
    unique = []
    seen = set()
    for item in xhs_items + creator_items:
        key = (item.get("platform", "xiaohongshu"), str(item.get("user_id", "")))
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return JsonResponse({"watches": unique})


@require_GET
def xiaohongshu_agent_public_watches_api(request):
    """Read-only shared feed for the mini program; never exposes user settings."""
    from django.contrib.auth.models import User

    key = f"peep-public-watches:{request.META.get('REMOTE_ADDR', 'unknown')}"
    if not cache.add(key, True, timeout=1):
        return JsonResponse({"error": "请求太频繁，请稍后再试"}, status=429)
    username = os.getenv("PEEP_PUBLIC_WATCH_USERNAME", "")
    if not username and settings.DEBUG:
        username = "peep-debug"
    user = User.objects.filter(username=username, is_active=True).first() if username else None
    if user is None and not settings.DEBUG:
        # Production fallback keeps the public mini-program feed tied to the
        # first active staff account until an explicit shared username is set.
        user = User.objects.filter(is_active=True, is_staff=True).order_by("pk").first()
    if user is None:
        return JsonResponse({"error": "共享数据服务尚未配置"}, status=503)
    items = []
    for item in creator_watch_service.list_watches(user):
        data = creator_watch_service.serialize_watch(item)
        data.pop("alert_email", None)
        items.append(data)
    return JsonResponse({"watches": items})


@csrf_exempt
@require_POST
def xiaohongshu_agent_public_subscribe_api(request):
    """Add a creator to the shared feed without exposing the shared account."""
    from django.contrib.auth.models import User

    key = f"peep-public-subscribe:{request.META.get('REMOTE_ADDR', 'unknown')}"
    if not cache.add(key, True, timeout=8):
        return JsonResponse({"error": "操作太频繁，请稍后再试"}, status=429)
    username = os.getenv("PEEP_PUBLIC_WATCH_USERNAME", "")
    user = User.objects.filter(username=username, is_active=True).first() if username else None
    if user is None:
        user = User.objects.filter(is_active=True, is_staff=True).order_by("pk").first()
    if user is None:
        return JsonResponse({"error": "共享数据服务尚未配置"}, status=503)
    try:
        data = _input(request)
        platform = data.get("platform", "xiaohongshu")
        user_id, token = creator_sources.parse_profile_link(platform, data.get("profile_url", ""))
        item, created = creator_watch_service.subscribe(user, platform, user_id, token)
        result = creator_watch_service.serialize_watch(item)
        result.pop("alert_email", None)
        return JsonResponse({"watch": result, "created": created})
    except agent.XhsInputError as exc:
        return JsonResponse({"error": str(exc)}, status=400)
    except agent.XhsServiceError as exc:
        return JsonResponse({"error": str(exc)}, status=502)


@require_GET
@_api_user_required
def xiaohongshu_agent_cover_api(request, watch_id: int, note_id: str):
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,80}", note_id):
        return JsonResponse({"error": "笔记 ID 格式不正确"}, status=400)
    item = SocialMediaSubscription.objects.filter(pk=watch_id, user=request.user, platform="xiaohongshu").first()
    if item is None:
        return JsonResponse({"error": "找不到这个订阅"}, status=404)
    state = (item.last_profile_data or {}).get("xhs_agent") or {}
    candidates = []
    for snapshot in reversed(state.get("history") or []):
        candidates.extend(snapshot.get("notes") or [])
    candidates.extend((state.get("latest_update") or {}).get("notes") or [])
    note = next((entry for entry in candidates if isinstance(entry, dict) and entry.get("id") == note_id), None)
    cover = note.get("cover") if note else ""
    if not isinstance(cover, str):
        cover = ""
    if cover.startswith("http://"):
        cover = "https://" + cover[7:]
    host = (urlparse(cover).hostname or "").lower()
    if not cover.startswith("https://") or not (host == "xhscdn.com" or host.endswith(".xhscdn.com")):
        return JsonResponse({"error": "该笔记没有可读取的真实封面"}, status=404)

    def fetch(value):
        key = f"creator-cover:{hashlib.sha256(value.encode()).hexdigest()}"
        cached_value = cache.get(key)
        if cached_value:
            return cached_value
        response = requests.get(
            value,
            headers={"User-Agent": "Mozilla/5.0", "Referer": "https://www.xiaohongshu.com/"},
            timeout=12,
        )
        response.raise_for_status()
        media_type = (response.headers.get("Content-Type") or "").split(";", 1)[0].lower()
        body = response.content
        if not media_type.startswith("image/") or not body or len(body) > 5 * 1024 * 1024:
            raise requests.RequestException("invalid image response")
        result = (media_type, body)
        cache.set(key, result, timeout=3600)
        return result

    try:
        content_type, content = fetch(cover)
    except requests.RequestException:
        # XHS CDN URLs are signed and expire. Refresh the note through MCP
        # once, persist the fresh URL, then retry the image request.
        token = note.get("xsec_token") if isinstance(note, dict) else ""
        try:
            refreshed = agent.read_note_detail(note_id, token) if token else {}
            fresh_cover = next((item for item in refreshed.get("images", []) if isinstance(item, str)), "")
            if fresh_cover.startswith("http://"):
                fresh_cover = "https://" + fresh_cover[7:]
            fresh_host = (urlparse(fresh_cover).hostname or "").lower()
            if not fresh_cover.startswith("https://") or not (
                fresh_host == "xhscdn.com" or fresh_host.endswith(".xhscdn.com")
            ):
                raise requests.RequestException("MCP returned no usable cover")
            for entry in [note] + [
                item
                for snapshot in state.get("history") or []
                for item in snapshot.get("notes") or []
                if isinstance(item, dict) and item.get("id") == note_id
            ]:
                entry["cover"] = fresh_cover
            item.last_profile_data = item.last_profile_data or {}
            item.save(update_fields=["last_profile_data", "updated_at"])
            content_type, content = fetch(fresh_cover)
        except (requests.RequestException, agent.XhsServiceError, agent.XhsInputError):
            return JsonResponse({"error": "真实封面已过期，MCP 暂时无法刷新"}, status=502)
    result = HttpResponse(content, content_type=content_type)
    result["Cache-Control"] = "private, max-age=3600"
    result["X-Content-Type-Options"] = "nosniff"
    return result


@csrf_exempt
@require_POST
@_api_user_required
def xiaohongshu_agent_subscribe_api(request):
    try:
        data = _input(request)
        platform = data.get("platform", "xiaohongshu")
        if data.get("profile_url"):
            if not isinstance(data["profile_url"], str):
                raise agent.XhsInputError("主页链接格式不正确")
            user_id, token = creator_sources.parse_profile_link(platform, data["profile_url"])
        else:
            user_id, token = data.get("user_id", ""), data.get("xsec_token", "")
        if not isinstance(user_id, str) or not isinstance(token, str):
            raise agent.XhsInputError("用户参数格式不正确")
        if _throttled(request, "subscribe"):
            return JsonResponse({"error": "操作太频繁，请稍后再试"}, status=429)
        item, created = watches.subscribe(request.user, platform, user_id, token)
        return JsonResponse({"watch": watches.serialize_watch(item), "created": created})
    except agent.XhsInputError as exc:
        return JsonResponse({"error": str(exc)}, status=400)
    except agent.XhsServiceError as exc:
        return JsonResponse({"error": str(exc)}, status=502)


@require_POST
@_api_user_required
def xiaohongshu_agent_unsubscribe_api(request):
    data = _input(request)
    watch_id = data.get("watch_id")
    if not isinstance(watch_id, int):
        return JsonResponse({"error": "订阅 ID 格式不正确"}, status=400)
    deleted, _ = SocialMediaSubscription.objects.filter(pk=watch_id, user=request.user).delete()
    if not deleted:
        return JsonResponse({"error": "未找到该关注"}, status=404)
    return JsonResponse({"deleted": True})


@require_POST
@_api_user_required
def xiaohongshu_agent_alert_email_api(request):
    try:
        data = _input(request)
        watch_id, email = data.get("watch_id"), data.get("email", "")
        if not isinstance(watch_id, int):
            raise agent.XhsInputError("订阅 ID 格式不正确")
        item = watches.set_alert_email(request.user, watch_id, email)
        return JsonResponse({"watch": watches.serialize_watch(item)})
    except agent.XhsInputError as exc:
        return JsonResponse({"error": str(exc)}, status=400)


@require_POST
@_api_user_required
def xiaohongshu_agent_test_email_api(request):
    watch_id = None
    try:
        watch_id = _input(request).get("watch_id")
        if not isinstance(watch_id, int):
            raise agent.XhsInputError("订阅 ID 格式不正确")
        item = SocialMediaSubscription.objects.filter(pk=watch_id, user=request.user).first()
        if item is None:
            raise agent.XhsInputError("找不到这个订阅")
        recipient = watches.serialize_watch(item)["alert_email"]
        if not recipient:
            raise agent.XhsInputError("请先保存通知邮箱")
        if settings.EMAIL_BACKEND != "django.core.mail.backends.smtp.EmailBackend":
            return JsonResponse({"error": "当前环境没有配置真实 SMTP，无法发送测试邮件"}, status=503)
        if _throttled(request, f"test-email:{watch_id}", seconds=600):
            return JsonResponse({"error": "测试邮件每 10 分钟最多发送一次"}, status=429)
        sent = send_snapshot_email(
            item,
            recipient,
            subject="博主更新提醒 · 最近一次更新测试",
        )
        if sent != 1:
            return JsonResponse({"error": "SMTP 没有确认投递"}, status=502)
        return JsonResponse({"message": "SMTP 已接受测试邮件，请检查收件箱和垃圾箱"})
    except agent.XhsInputError as exc:
        return JsonResponse({"error": str(exc)}, status=400)
    except EmailLimitError as exc:
        return JsonResponse({"error": str(exc)}, status=429)
    except Exception:
        logger.exception("博主更新测试邮件发送失败，订阅 ID=%s", watch_id)
        return JsonResponse({"error": "测试邮件发送失败，请管理员检查 SMTP 配置与服务日志"}, status=502)


@require_POST
@_api_user_required
def xiaohongshu_agent_message_api(request):
    try:
        message = _input(request).get("message", "")
        if not isinstance(message, str):
            raise agent.XhsInputError("消息格式不正确")
        if _throttled(request, "message", seconds=3):
            return JsonResponse({"error": "正在处理上一条查询，请 3 秒后再试"}, status=429)
        result = watches.reply_to_message(request.user, message)
        if result.get("new_count") and result.get("watch", {}).get("id") and not result.get("cached"):
            subscription = SocialMediaSubscription.objects.get(pk=result["watch"]["id"], user=request.user)
            result["delivery"] = deliver_updates(subscription, result)
        return JsonResponse(result)
    except agent.XhsInputError as exc:
        return JsonResponse({"error": str(exc)}, status=400)
    except agent.XhsServiceError as exc:
        return JsonResponse({"error": str(exc)}, status=502)


@require_GET
@_api_user_required
def xiaohongshu_agent_login_status_api(request):
    if request.GET.get("cached") == "1":
        return JsonResponse(xiaohongshu_login_state.saved_status())
    return JsonResponse(xiaohongshu_login_state.check_and_store())


@require_POST
@_api_user_required
def xiaohongshu_agent_login_qrcode_api(request):
    denied = _admin_required(request)
    if denied is not None:
        return denied
    try:
        return JsonResponse(agent.login_qrcode())
    except agent.XhsServiceError as exc:
        return JsonResponse({"error": str(exc)}, status=502)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def xiaohongshu_agent_wecom_callback(request):
    try:
        if request.method == "GET":
            return HttpResponse(wecom.verify_url(request.GET), content_type="text/plain")
        if len(request.body) > 16384:
            raise wecom.WeComError("企业微信消息过长")
        return HttpResponse(wecom.handle_message(request.GET, request.body), content_type="application/xml")
    except wecom.WeComError:
        return HttpResponse("invalid callback", status=403, content_type="text/plain")
