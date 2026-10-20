"""Focused contract tests for the creator update flow without calling Xiaohongshu."""

from datetime import timedelta
import base64
import json
import os

import pytest
from django.contrib.auth.models import User
from django.core import mail
from django.core.cache import cache
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone

from apps.tools.models import SocialMediaNotification, SocialMediaSubscription
from apps.tools.models.chat_models import ChatNotification
from apps.tools.services import creator_sources, creator_watch_service
from apps.tools.services import xiaohongshu_profile_agent as profile_agent
from apps.tools.services import xiaohongshu_login_state
from apps.tools.services import xiaohongshu_delivery
from apps.tools.services import xiaohongshu_watch_service as watch_service
from apps.tools.services import xiaohongshu_wecom as wecom
from apps.tools.services.xiaohongshu_delivery import deliver_updates


def profile(note_ids):
    return {
        "user_id": "abc123",
        "nickname": "测试博主",
        "avatar": "",
        "notes": [
            {
                "id": note_id,
                "xsec_token": "token",
                "title": f"笔记 {note_id}",
                "cover": f"https://example.com/{note_id}.jpg",
                "likes": "",
                "url": f"https://www.xiaohongshu.com/explore/{note_id}",
            }
            for note_id in note_ids
        ],
        "is_truncated": False,
    }


@pytest.mark.parametrize(
    "value",
    [
        "https://evil.example/user/profile/abc123?xsec_token=x",
        "https://www.xiaohongshu.com/user/profile/abc123",
        "https://www.xiaohongshu.com/explore/abc123?xsec_token=x",
    ],
)
def test_rejects_non_profile_links(value):
    with pytest.raises(profile_agent.XhsInputError):
        profile_agent.parse_profile_link(value)


def test_upstream_profile_shape_and_note_link(monkeypatch):
    def fake_call(method, path, **kwargs):
        assert method == "POST"
        assert path == "/api/v1/user/profile"
        return {
            "success": True,
            "data": {
                "userBasicInfo": {"nickname": "真实结构", "desc": "简介", "images": "https://example.com/avatar"},
                "interactions": [{"type": "fans", "count": "42"}],
                "feeds": [
                    {
                        "id": "note123",
                        "xsecToken": "abc/def",
                        "noteCard": {
                            "displayTitle": "今天更新",
                            "cover": {"urlDefault": "https://example.com/cover"},
                            "interactInfo": {"likedCount": "3"},
                        },
                    }
                ],
            },
        }

    monkeypatch.setattr(profile_agent, "_call_mcp", fake_call)
    result = profile_agent.read_profile("abc123", "token")
    assert result["note_count_loaded"] == 1
    assert result["counts"]["fans"] == "42"
    assert result["notes"][0]["url"].endswith("xsec_token=abc%2Fdef&xsec_source=pc_user")


@pytest.mark.django_db
def test_xiaohongshu_snapshot_reports_profile_count_changes(monkeypatch):
    user = User.objects.create_user(username="xhs-counts", password="test-password")
    initial = profile(["old-note"])
    initial["counts"] = {"fans": "42", "follows": "10", "interaction": "100"}
    current = profile(["old-note", "new-note"])
    current["counts"] = {"fans": "45", "follows": "11", "interaction": "120"}
    monkeypatch.setattr(profile_agent, "read_profile", lambda *_: initial)
    item, _ = watch_service.subscribe(user, "abc123", "token")
    data = item.last_profile_data
    data[watch_service.STATE_KEY]["history"][0]["date"] = (timezone.localdate() - timedelta(days=1)).isoformat()
    item.last_profile_data = data
    item.save(update_fields=["last_profile_data"])
    monkeypatch.setattr(profile_agent, "read_profile", lambda *_: current)
    monkeypatch.setattr(profile_agent, "read_note_detail", lambda *_: {})

    result = watch_service.check_watch(item)

    assert result["count_changes"]["fans"] == {"label": "粉丝", "before": "42", "after": "45"}
    assert result["count_changes"]["follows"]["after"] == "11"
    assert result["count_changes"]["interaction"]["after"] == "120"
    assert "账号数据变化" in result["answer"]


def test_empty_upstream_note_list_is_not_a_baseline(monkeypatch):
    calls = []

    def empty_profile(*args, **kwargs):
        calls.append(1)
        return {"success": True, "data": {"userBasicInfo": {"nickname": "作者"}, "feeds": []}}

    monkeypatch.setattr(profile_agent, "_call_mcp", empty_profile)
    with pytest.raises(profile_agent.XhsServiceError, match="未加载到笔记"):
        profile_agent.read_profile("emptyprofile", "unique-token")
    with pytest.raises(profile_agent.XhsServiceError, match="刚查询失败"):
        profile_agent.read_profile("emptyprofile", "unique-token")
    assert len(calls) == 1


def test_mcp_call_does_not_touch_lock_held_by_another_process(monkeypatch, tmp_path):
    if os.name == "nt":
        pytest.skip("POSIX flock interoperability probe")
    import fcntl

    lock_path = tmp_path / "mcp.lock"
    monkeypatch.setenv("XHS_MCP_LOCK_FILE", str(lock_path))
    monkeypatch.setattr(profile_agent.requests, "request", lambda *args, **kwargs: pytest.fail("MCP request must not start"))
    fd = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o600)
    try:
        os.write(fd, b"123.0")
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        with pytest.raises(profile_agent.XhsServiceError, match="另一个查询"):
            profile_agent._call_mcp("GET", "/api/v1/login/status")
        os.lseek(fd, 0, os.SEEK_SET)
        assert os.read(fd, 64) == b"123.0"
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)


def test_mcp_call_releases_lock_and_records_request_time(monkeypatch, tmp_path):
    lock_path = tmp_path / "mcp.lock"
    monkeypatch.setenv("XHS_MCP_LOCK_FILE", str(lock_path))

    class Response:
        status_code = 200

        @staticmethod
        def json():
            return {"success": True, "data": {"is_logged_in": True}}

    monkeypatch.setattr(profile_agent.requests, "request", lambda *args, **kwargs: Response())
    assert profile_agent._call_mcp("GET", "/api/v1/login/status")["success"] is True
    saved = lock_path.read_bytes()
    assert float(saved[1:] if os.name == "nt" else saved) > 0
    assert profile_agent._call_mcp("GET", "/api/v1/login/status")["success"] is True


def test_mcp_daily_budget_blocks_extra_requests(monkeypatch, tmp_path):
    key = f"xhs-agent:mcp-daily-requests:{timezone.localdate().isoformat()}"
    cache.delete(key)
    monkeypatch.setenv("XHS_MCP_DAILY_REQUEST_LIMIT", "1")
    monkeypatch.setenv("XHS_MCP_LOCK_FILE", str(tmp_path / "mcp.lock"))

    class Response:
        status_code = 200

        @staticmethod
        def json():
            return {"success": True}

    calls = []
    monkeypatch.setattr(profile_agent.requests, "request", lambda *args, **kwargs: calls.append(1) or Response())
    try:
        profile_agent._call_mcp("GET", "/health")
        with pytest.raises(profile_agent.XhsServiceError, match="安全访问额度"):
            profile_agent._call_mcp("GET", "/health")
        assert len(calls) == 1
    finally:
        cache.delete(key)


@pytest.mark.django_db
def test_yesterday_comparison_and_notification_dedup(monkeypatch):
    user = User.objects.create_user(username="xhs-agent-test", password="test-password")
    monkeypatch.setattr(profile_agent, "read_profile", lambda *_: profile(["old"]))
    item, created = watch_service.subscribe(user, "abc123", "token")
    assert created
    assert watch_service.check_watch(item)["comparison"] == "baseline"

    data = item.last_profile_data
    data[watch_service.STATE_KEY]["history"][0]["date"] = (timezone.localdate() - timedelta(days=1)).isoformat()
    item.last_profile_data = data
    item.save()
    monkeypatch.setattr(profile_agent, "read_profile", lambda *_: profile(["new", "old"]))
    monkeypatch.setattr(profile_agent, "read_note_detail", lambda *_: {"description": "新笔记正文"})
    first = watch_service.check_watch(item)
    second = watch_service.check_watch(item)
    assert first["comparison"] == "yesterday"
    assert first["previous_visible_count"] == 1
    assert first["current_visible_count"] == 2
    assert first["new_count"] == 1
    assert first["new_notes"][0]["description"] == "新笔记正文"
    assert second["new_count"] == 1
    assert SocialMediaNotification.objects.filter(subscription=item, data__note_id="new").count() == 1

    monkeypatch.setattr(profile_agent, "read_profile", lambda *_: profile(["old"]))
    protected = watch_service.check_watch(item)
    assert protected["current_visible_count"] == 2
    assert protected["new_count"] == 1

    monkeypatch.setattr(
        profile_agent,
        "read_profile",
        lambda *_: pytest.fail("同一天的普通对话不应重新读取平台"),
    )
    cached = creator_watch_service.reply_to_message(user, "测试博主今天更新了吗？")
    assert cached["cached"] is True
    assert cached["new_count"] == 1
    assert cached["new_notes"][0]["id"] == "new"


@pytest.mark.django_db
def test_page_and_api_auth_and_message(client, monkeypatch):
    page = reverse("tools:xiaohongshu_agent")
    watches = reverse("tools:xiaohongshu_agent_watches_api")
    message = reverse("tools:xiaohongshu_agent_message_api")
    login_status = reverse("tools:xiaohongshu_agent_login_status_api")
    assert client.get(page).status_code == 302
    assert client.get(watches).status_code == 401
    user = User.objects.create_user(username="xhs-ui-test", password="test-password")
    client.force_login(user)
    monkeypatch.setattr(profile_agent, "login_status", lambda: {"is_logged_in": False, "username": ""})
    assert client.get(page).status_code == 200
    assert client.get(watches).json()["watches"] == []
    assert client.get(login_status).status_code == 200
    response = client.post(message, data='{"message":"今天更新了吗"}', content_type="application/json")
    assert response.status_code == 200
    assert "还没有订阅" in response.json()["answer"]


@pytest.mark.django_db
def test_message_searches_before_asking_for_profile_link(monkeypatch):
    user = User.objects.create_user(username="xhs-named-query", password="test-password")
    SocialMediaSubscription.objects.create(
        user=user,
        platform="xiaohongshu",
        target_user_id="creator-one",
        target_user_name="昕妹叫昕昕",
        status="active",
    )

    monkeypatch.setattr(creator_sources, "search_candidates", lambda platform, keyword: [])

    result = creator_watch_service.reply_to_message(user, "小红书 田曦薇 今天更新了吗？")

    assert "Agent 已搜索小红书" in result["answer"]
    assert "没有找到“田曦薇”" in result["answer"]
    assert "粘贴该用户的主页完整链接" in result["answer"]
    assert result["new_notes"] == []

    generic = creator_watch_service.reply_to_message(user, "今天更新了吗？", refresh=False)
    assert "昕妹叫昕昕 尚未完成每日检查" in generic["answer"]


@pytest.mark.django_db
def test_message_auto_subscribes_one_exact_search_match(monkeypatch):
    user = User.objects.create_user(username="xhs-auto-discover", password="test-password")
    calls = []

    def search(platform, keyword):
        calls.append((platform, keyword))
        return [
            {
                "user_id": "creator-tian",
                "nickname": "田曦薇",
                "xsec_token": "profile-token",
                "source_note": "主页内容",
            }
        ]

    def subscribe(_user, platform, user_id, token=""):
        item = SocialMediaSubscription.objects.create(
            user=_user,
            platform=platform,
            target_user_id=user_id,
            target_user_name="田曦薇",
            status="active",
            subscription_types=[watch_service.AGENT_MARKER],
            last_profile_data={
                watch_service.STATE_KEY: {
                    "history": [
                        {
                            "date": timezone.localdate().isoformat(),
                            "checked_at": timezone.now().isoformat(),
                            "visible_count": 12,
                            "notes": [],
                        }
                    ]
                }
            },
        )
        return item, True

    monkeypatch.setattr(creator_sources, "search_candidates", search)
    monkeypatch.setattr(creator_watch_service, "subscribe", subscribe)

    result = creator_watch_service.reply_to_message(user, "小红书 田曦薇 今天更新了吗？")

    assert calls == [("xiaohongshu", "田曦薇")]
    assert result["discovered"] is True
    assert result["watch"]["nickname"] == "田曦薇"
    assert result["current_visible_count"] == 12
    assert "已自动关注" in result["answer"]
    assert "没有昨天的记录" in result["answer"]


@pytest.mark.django_db
def test_watch_api_returns_only_latest_update_batch_with_https_covers(client, monkeypatch):
    user = User.objects.create_user(username="xhs-real-snapshot", password="test-password")
    current = ["old-note"]

    def current_profile(*_):
        value = profile(current)
        if current[0] == "real-note":
            value["notes"][0]["cover"] = "http://sns-webpic-qc.xhscdn.com/real-cover.webp"
        return value

    monkeypatch.setattr(profile_agent, "read_profile", current_profile)
    monkeypatch.setattr(profile_agent, "read_note_detail", lambda *_: {"description": "真实更新正文"})
    item, _ = watch_service.subscribe(user, "abc123", "token")
    data = item.last_profile_data
    data[watch_service.STATE_KEY]["history"][-1]["date"] = (timezone.localdate() - timedelta(days=1)).isoformat()
    item.last_profile_data = data
    item.save(update_fields=["last_profile_data"])
    current.insert(0, "real-note")
    watch_service.check_watch(item)

    client.force_login(user)
    watch = client.get(reverse("tools:xiaohongshu_agent_watches_api")).json()["watches"][0]
    assert "latest_snapshot" not in watch
    assert watch["latest_update"]["date"] == timezone.localdate().isoformat()
    assert watch["latest_update"]["count"] == 1
    assert [note["id"] for note in watch["latest_update"]["notes"]] == ["real-note"]
    assert watch["latest_update"]["notes"][0]["cover"] == "https://sns-webpic-qc.xhscdn.com/real-cover.webp"


@pytest.mark.django_db
def test_real_cover_proxy_is_owner_scoped_and_returns_image(client, monkeypatch):
    owner = User.objects.create_user(username="xhs-cover-owner", password="test-password")
    stranger = User.objects.create_user(username="xhs-cover-stranger", password="test-password")
    monkeypatch.setattr(profile_agent, "read_profile", lambda *_: profile(["cover-note"]))
    item, _ = watch_service.subscribe(owner, "abc123", "token")
    data = item.last_profile_data
    data[watch_service.STATE_KEY]["history"][-1]["notes"][0][
        "cover"
    ] = "http://sns-webpic-qc.xhscdn.com/owner-scoped-cover.webp"
    item.last_profile_data = data
    item.save(update_fields=["last_profile_data"])
    route = reverse("tools:xiaohongshu_agent_cover_api", kwargs={"watch_id": item.pk, "note_id": "cover-note"})

    client.force_login(stranger)
    assert client.get(route).status_code == 404

    class CoverResponse:
        headers = {"Content-Type": "image/webp"}
        content = b"real-xhs-image"

        @staticmethod
        def raise_for_status():
            return None

    monkeypatch.setattr("apps.tools.views.xiaohongshu_agent_views.requests.get", lambda *args, **kwargs: CoverResponse())
    client.force_login(owner)
    response = client.get(route)
    assert response.status_code == 200
    assert response["Content-Type"] == "image/webp"
    assert response.content == b"real-xhs-image"


@pytest.mark.django_db
def test_login_failure_status_survives_requests_without_stale_success(client, monkeypatch):
    user = User.objects.create_user(username="xhs-login-state-test", password="test-password")
    client.force_login(user)
    route = reverse("tools:xiaohongshu_agent_login_status_api")
    monkeypatch.setattr(profile_agent, "login_status", lambda: {"is_logged_in": True, "username": "已登录账号"})
    success = client.get(route).json()
    assert success["status"] == "logged_in"
    assert success["is_logged_in"] is True
    assert success["last_success_at"]

    def unavailable():
        raise profile_agent.XhsServiceError("MCP 暂时不可用")

    monkeypatch.setattr(profile_agent, "login_status", unavailable)
    failed = client.get(route).json()
    assert failed["status"] == "error"
    assert failed["is_logged_in"] is False
    assert failed["error"] == "MCP 暂时不可用"
    assert failed["last_success_at"] == success["last_success_at"]
    assert xiaohongshu_login_state.saved_status()["status"] == "error"
    assert client.get(route + "?cached=1").json()["checked_at"] == failed["checked_at"]

    monkeypatch.setattr(profile_agent, "login_status", lambda: {"is_logged_in": False, "username": ""})
    logged_out = client.get(route).json()
    assert logged_out["status"] == "logged_out"
    assert logged_out["is_logged_in"] is False
    assert logged_out["last_success_at"] == success["last_success_at"]


@pytest.mark.parametrize(
    ("platform", "link", "user_id"),
    [
        ("bilibili", "https://space.bilibili.com/517327498", "517327498"),
        ("netease", "https://music.163.com/#/user/home?id=1", "1"),
        ("netease", "https://music.163.com/user/home?id=1", "1"),
    ],
)
def test_other_platform_profile_links(platform, link, user_id):
    assert creator_sources.parse_profile_link(platform, link) == (user_id, "")


def test_bilibili_412_stops_followup_requests(monkeypatch):
    from types import SimpleNamespace

    cache.delete("creator-source:bilibili:blocked")
    monkeypatch.setattr(creator_sources.shutil, "which", lambda _: "/fake/bili")
    calls = []

    def blocked(*args, **kwargs):
        calls.append(1)
        return SimpleNamespace(returncode=1, stdout='{"ok":false,"error":{"message":"HTTP 412"}}')

    monkeypatch.setattr(creator_sources.subprocess, "run", blocked)
    with pytest.raises(profile_agent.XhsServiceError, match="风控"):
        creator_sources._bili_call("user-videos", "517327498")
    with pytest.raises(profile_agent.XhsServiceError, match="暂停请求"):
        creator_sources._bili_call("user-videos", "517327498")
    assert len(calls) == 1
    cache.delete("creator-source:bilibili:blocked")


def test_bilibili_profile_normalizes_video(monkeypatch):
    cache.delete("creator-source:bilibili:42")

    def fake_call(*args):
        if args[0] == "user-videos":
            return [{"bvid": "BVabc", "title": "更新视频", "url": "https://www.bilibili.com/video/BVabc"}]
        return {"user": {"name": "作者"}, "relation": {"follower": 12}}

    monkeypatch.setattr(creator_sources, "_bili_call", fake_call)
    result = creator_sources.read_profile("bilibili", "42")
    assert result["nickname"] == "作者"
    assert result["notes"][0]["id"] == "BVabc"
    assert result["notes"][0]["url"].endswith("BVabc")
    cache.delete("creator-source:bilibili:42")


def test_netease_profile_normalizes_event(monkeypatch):
    cache.delete("creator-source:netease:42")

    def fake_call(path, *, payload=None):
        if "detail" in path:
            return {"profile": {"nickname": "歌迷", "avatarUrl": "https://example.com/a.png"}}
        return {"events": [{"id": 123, "json": '{"msg":"新歌分享"}', "pics": []}], "more": False}

    monkeypatch.setattr(creator_sources, "_netease_call", fake_call)
    result = creator_sources.read_profile("netease", "42")
    assert result["nickname"] == "歌迷"
    assert result["notes"][0]["title"] == "新歌分享"
    assert result["notes"][0]["url"] == "https://music.163.com/#/event?id=123"
    cache.delete("creator-source:netease:42")


@pytest.mark.django_db
def test_current_user_sees_existing_subscriptions_only(client, monkeypatch):
    owner = User.objects.create_user(username="creator-owner", password="test-password")
    stranger = User.objects.create_user(username="creator-stranger", password="test-password")
    for user, name in ((owner, "旧关注"), (stranger, "别人的关注")):
        SocialMediaSubscription.objects.create(
            user=user,
            platform="bilibili",
            target_user_id=str(user.pk),
            target_user_name=name,
            subscription_types=["newPosts"],
        )
    client.force_login(owner)
    response = client.get(reverse("tools:xiaohongshu_agent_watches_api"))
    assert response.status_code == 200
    assert [item["nickname"] for item in response.json()["watches"]] == ["旧关注"]
    assert response.json()["watches"][0]["monitoring_enabled"] is False


@pytest.mark.django_db
def test_bilibili_daily_comparison_and_named_message(monkeypatch):
    user = User.objects.create_user(username="creator-bili", password="test-password")
    current_ids = ["BVold"]
    profile_calls = []

    def fake_profile(platform, user_id, token=""):
        assert (platform, user_id) == ("bilibili", "517327498")
        profile_calls.append(user_id)
        return {
            "nickname": "罗翔说刑法",
            "avatar": "",
            "fetched_at": timezone.now().isoformat(),
            "notes": [
                {
                    "id": note_id,
                    "title": note_id,
                    "description": "内容简介",
                    "url": f"https://www.bilibili.com/video/{note_id}",
                }
                for note_id in current_ids
            ],
        }

    monkeypatch.setattr(creator_sources, "read_profile", fake_profile)
    item, created = creator_watch_service.subscribe(user, "bilibili", "517327498")
    assert created
    data = item.last_profile_data
    data[creator_watch_service.STATE_KEY]["history"][0]["date"] = (timezone.localdate() - timedelta(days=1)).isoformat()
    item.last_profile_data = data
    item.save()
    current_ids.insert(0, "BVnew")
    first = creator_watch_service.reply_to_message(user, "罗翔说刑法今天更新了吗？")
    second = creator_watch_service.reply_to_message(user, "罗翔说刑法今天更新了吗？")
    assert first["comparison"] == "yesterday"
    assert first["new_count"] == 1
    assert first["new_notes"][0]["id"] == "BVnew"
    assert second["new_count"] == 1
    assert second["cached"] is True
    assert len(profile_calls) == 2
    assert SocialMediaNotification.objects.filter(subscription=item, data__item_id="BVnew").count() == 1


@pytest.mark.django_db
@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend", DEFAULT_FROM_EMAIL="agent@example.com")
def test_user_email_alert_is_sent_once(monkeypatch):
    user = User.objects.create_user(username="xhs-mail-test", password="test-password")
    monkeypatch.setattr(profile_agent, "read_profile", lambda *_: profile(["old"]))
    item, _ = watch_service.subscribe(user, "abc123", "token")
    watch_service.set_alert_email(user, item.pk, "reader@qq.com")
    item.refresh_from_db()
    result = {
        "answer": "发现新笔记",
        "new_notes": [
            {
                "id": "new",
                "title": "新笔记",
                "cover": "https://example.com/new.jpg",
                "url": "https://www.xiaohongshu.com/explore/new",
            }
        ],
    }
    assert deliver_updates(item, result)["email"] == "已发送 1 篇"
    assert len(mail.outbox) == 1
    assert mail.outbox[0].alternatives
    assert "https://example.com/new.jpg" in mail.outbox[0].alternatives[0][0]
    assert "最近更新" in mail.outbox[0].alternatives[0][0]
    assert ChatNotification.objects.filter(user=user, message__metadata__source="creator_watch").count() == 1
    item.refresh_from_db()
    assert deliver_updates(item, result) == {}
    assert len(mail.outbox) == 1
    assert ChatNotification.objects.filter(user=user, message__metadata__source="creator_watch").count() == 1


@pytest.mark.django_db
@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend", DEFAULT_FROM_EMAIL="agent@example.com")
def test_email_embeds_real_xhs_cover_as_inline_image(monkeypatch):
    user = User.objects.create_user(username="xhs-inline-cover", password="test-password")
    monkeypatch.setattr(profile_agent, "read_profile", lambda *_: profile(["old"]))
    item, _ = watch_service.subscribe(user, "abc123", "token")
    watch_service.set_alert_email(user, item.pk, "reader@qq.com")
    item.refresh_from_db()
    cover = "https://sns-webpic-qc.xhscdn.com/inline-cover.webp"
    monkeypatch.setattr(xiaohongshu_delivery, "_download_cover", lambda value: ("image/webp", b"webp-data"))
    result = {
        "answer": "发现一篇新笔记",
        "checked_date": "2026-10-18",
        "new_notes": [
            {
                "id": "new-inline",
                "title": "真实封面更新",
                "cover": cover,
                "url": "https://www.xiaohongshu.com/explore/new-inline",
            }
        ],
    }
    assert deliver_updates(item, result)["email"] == "已发送 1 篇"
    html = mail.outbox[0].alternatives[0][0]
    assert "cid:creator-" in html
    assert cover not in html
    assert any(attachment.get("Content-ID") for attachment in mail.outbox[0].attachments)


@pytest.mark.django_db
@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend", DEFAULT_FROM_EMAIL="agent@example.com")
def test_two_new_notes_trigger_one_grouped_email_and_system_reminder(monkeypatch):
    user = User.objects.create_user(username="snapshot-mail-trace", password="test-password")
    visible_notes = ["old-note"]
    monkeypatch.setattr(profile_agent, "read_profile", lambda *_: profile(visible_notes))
    monkeypatch.setattr(profile_agent, "read_note_detail", lambda *_: {"description": "第二次快照新增的内容"})

    watch, _ = watch_service.subscribe(user, "abc123", "token")
    watch_service.set_alert_email(user, watch.pk, "1009383129@qq.com")
    first = watch.last_profile_data[watch_service.STATE_KEY]["history"][0]
    assert first["visible_count"] == 1
    assert mail.outbox == []

    # Move only the stored baseline date to yesterday; the second read is mocked as today's profile.
    watch.refresh_from_db()
    state = watch.last_profile_data
    state[watch_service.STATE_KEY]["history"][0]["date"] = (timezone.localdate() - timedelta(days=1)).isoformat()
    watch.last_profile_data = state
    watch.save(update_fields=["last_profile_data"])
    visible_notes[:0] = ["new-note-1", "new-note-2"]

    result = watch_service.check_watch(watch)
    delivered = deliver_updates(watch, result)
    assert result["comparison"] == "yesterday"
    assert result["previous_visible_count"] == 1
    assert result["current_visible_count"] == 3
    assert [note["id"] for note in result["new_notes"]] == ["new-note-1", "new-note-2"]
    assert result["new_notes"][0]["cover"] == "https://example.com/new-note-1.jpg"
    assert delivered["email"] == "已发送 2 篇"
    assert delivered["system"] == "已发送 2 篇"
    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == ["1009383129@qq.com"]
    assert "笔记 new-note-1" in mail.outbox[0].body
    assert "笔记 new-note-2" in mail.outbox[0].body
    html = mail.outbox[0].alternatives[0][0]
    assert "https://example.com/new-note-1.jpg" in html
    assert "https://example.com/new-note-2.jpg" in html
    assert "https://example.com/old-note.jpg" not in html
    notifications = ChatNotification.objects.filter(user=user, message__metadata__source="creator_watch")
    assert notifications.count() == 1
    metadata = notifications.get().message.metadata
    assert metadata["note_ids"] == ["new-note-1", "new-note-2"]
    assert [entry["url"] for entry in metadata["updates"]] == [
        "https://www.xiaohongshu.com/explore/new-note-1",
        "https://www.xiaohongshu.com/explore/new-note-2",
    ]
    assert deliver_updates(watch, result) == {}

    print(
        "CREATOR_WATCH_TRACE="
        + json.dumps(
            {
                "first_snapshot": {"visible_count": first["visible_count"], "note_ids": ["old-note"]},
                "second_snapshot": {"visible_count": result["current_visible_count"], "note_ids": visible_notes},
                "new_note_ids": [note["id"] for note in result["new_notes"]],
                "system": delivered["system"],
                "email": delivered["email"],
                "recipient": mail.outbox[0].to,
                "duplicate_delivery": 0,
            },
            ensure_ascii=False,
        )
    )


@pytest.mark.django_db
def test_creator_update_appears_in_system_notification_bell(client, monkeypatch):
    user = User.objects.create_user(username="creator-bell", password="test-password")
    monkeypatch.setattr(profile_agent, "read_profile", lambda *_: profile(["old"]))
    item, _ = watch_service.subscribe(user, "abc123", "token")
    result = {
        "answer": "发现新笔记",
        "new_notes": [
            {
                "id": "new",
                "title": "新笔记",
                "cover": "https://example.com/new.jpg",
                "url": "https://www.xiaohongshu.com/explore/new",
            }
        ],
    }
    assert deliver_updates(item, result)["system"] == "已发送 1 篇"
    client.force_login(user)
    response = client.get(reverse("tools:get_unread_notifications_api"))
    assert response.status_code == 200
    assert response.json()["total_unread"] == 1
    assert response.json()["notifications"][0]["metadata"]["jump_url"] == ("/tools/xiaohongshu-agent/#xhs-watches-panel")
    proxy_cover = f"/tools/api/xiaohongshu-agent/watches/{item.pk}/covers/new/"
    assert response.json()["notifications"][0]["metadata"]["cover"] == proxy_cover
    assert response.json()["notifications"][0]["metadata"]["note_ids"] == ["new"]
    assert response.json()["notifications"][0]["metadata"]["updates"][0]["cover"] == proxy_cover
    from apps.tools.management.commands.cleanup_inactive_chatrooms import Command

    assert ChatNotification.objects.get(user=user).room not in Command().find_inactive_rooms(
        timezone.now() + timedelta(days=1)
    )


@pytest.mark.django_db
def test_page_contains_no_hard_coded_snapshot_demo(client):
    user = User.objects.create_user(username="creator-real-photo-page", password="test-password")
    client.force_login(user)
    html = client.get(reverse("tools:xiaohongshu_agent")).content.decode()
    assert 'id="xhs-demo"' not in html
    assert "lake-6295829_1280.jpg" not in html
    assert "mountains-3048299_1280.jpg" not in html


@pytest.mark.django_db
@override_settings(EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend", DEFAULT_FROM_EMAIL="agent@example.com")
def test_test_email_sends_only_to_owned_saved_address(client, monkeypatch):
    user = User.objects.create_user(username="creator-mail-owner", password="test-password")
    other = User.objects.create_user(username="creator-mail-other", password="test-password")
    monkeypatch.setattr(profile_agent, "read_profile", lambda *_: profile(["old"]))
    item, _ = watch_service.subscribe(user, "abc123", "token")
    watch_service.set_alert_email(user, item.pk, "reader@qq.com")
    captured = []
    monkeypatch.setattr(
        "apps.tools.views.xiaohongshu_agent_views.send_snapshot_email",
        lambda subscription, recipient, **kwargs: captured.append((subscription, recipient, kwargs)) or 1,
    )
    client.force_login(other)
    denied = client.post(
        reverse("tools:xiaohongshu_agent_test_email_api"),
        data={"watch_id": item.pk},
        content_type="application/json",
    )
    assert denied.status_code == 400
    client.force_login(user)
    accepted = client.post(
        reverse("tools:xiaohongshu_agent_test_email_api"),
        data={"watch_id": item.pk},
        content_type="application/json",
    )
    assert accepted.status_code == 200
    assert captured[0][1] == "reader@qq.com"
    assert captured[0][0].pk == item.pk


@pytest.mark.django_db
@override_settings(EMAIL_BACKEND="django.core.mail.backends.console.EmailBackend")
def test_test_email_rejects_console_backend(client, monkeypatch):
    user = User.objects.create_user(username="creator-mail-console", password="test-password")
    monkeypatch.setattr(profile_agent, "read_profile", lambda *_: profile(["old"]))
    item, _ = watch_service.subscribe(user, "abc123", "token")
    watch_service.set_alert_email(user, item.pk, "reader@qq.com")
    client.force_login(user)
    response = client.post(
        reverse("tools:xiaohongshu_agent_test_email_api"),
        data={"watch_id": item.pk},
        content_type="application/json",
    )
    assert response.status_code == 503
    assert "SMTP" in response.json()["error"]


@pytest.mark.django_db
@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend", DEFAULT_FROM_EMAIL="agent@example.com")
def test_email_is_not_marked_sent_when_backend_reports_zero(monkeypatch):
    user = User.objects.create_user(username="xhs-mail-zero", password="test-password")
    monkeypatch.setattr(profile_agent, "read_profile", lambda *_: profile(["old"]))
    item, _ = watch_service.subscribe(user, "abc123", "token")
    watch_service.set_alert_email(user, item.pk, "reader@qq.com")
    item.refresh_from_db()
    monkeypatch.setattr("apps.tools.services.xiaohongshu_delivery.send_snapshot_email", lambda *args, **kwargs: 0)
    result = {"answer": "发现新笔记", "new_notes": [{"id": "new", "title": "新笔记"}]}
    assert "失败" in deliver_updates(item, result)["email"]
    item.refresh_from_db()
    assert not (item.last_profile_data[watch_service.STATE_KEY].get("sent_note_ids") or {}).get("email")


def test_wecom_signature_and_encryption_roundtrip(monkeypatch):
    key = b"0123456789abcdef0123456789abcdef"
    monkeypatch.setenv("XHS_WECOM_CALLBACK_TOKEN", "callback-token")
    monkeypatch.setenv("XHS_WECOM_ENCODING_AES_KEY", base64.b64encode(key).decode().rstrip("="))
    monkeypatch.setenv("XHS_WECOM_CORP_ID", "corp-test")
    encrypted = wecom._encrypt(key, "verify-me", "corp-test")
    query = {
        "timestamp": "123",
        "nonce": "abc",
        "echostr": encrypted,
        "msg_signature": wecom._signature("callback-token", "123", "abc", encrypted),
    }
    assert wecom.verify_url(query) == "verify-me"
    query["msg_signature"] = "wrong"
    with pytest.raises(wecom.WeComError):
        wecom.verify_url(query)


@pytest.mark.django_db
@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
def test_creator_email_shared_address_and_persistent_daily_cap(monkeypatch):
    from apps.tools.services import creator_email_policy as policy

    user = User.objects.create_user(username="mail-daily-cap")
    first = SocialMediaSubscription.objects.create(
        user=user, platform="xiaohongshu", target_user_id="one", target_user_name="One"
    )
    second = SocialMediaSubscription.objects.create(
        user=user, platform="bilibili", target_user_id="two", target_user_name="Two"
    )
    creator_watch_service.set_alert_email(user, first.pk, "first@qq.com")
    creator_watch_service.set_alert_email(user, second.pk, "second@qq.com")
    assert creator_watch_service.serialize_watch(first)["alert_email"] == "second@qq.com"
    assert creator_watch_service.serialize_watch(second)["alert_email"] == "second@qq.com"
    for item in (first, second, first):
        assert xiaohongshu_delivery.send_snapshot_email(item, "second@qq.com") == 1
    cache.clear()
    with pytest.raises(policy.EmailLimitError, match="3 封上限"):
        xiaohongshu_delivery.send_snapshot_email(second, "second@qq.com")
    assert len(mail.outbox) == 3
    creator_watch_service.set_alert_email(user, first.pk, "changed@qq.com")
    with pytest.raises(policy.EmailLimitError):
        xiaohongshu_delivery.send_snapshot_email(first, "changed@qq.com")
    tomorrow = timezone.now() + timedelta(days=1)
    monkeypatch.setattr(policy.timezone, "now", lambda: tomorrow)
    assert xiaohongshu_delivery.send_snapshot_email(second, "changed@qq.com") == 1
    assert len(mail.outbox) == 4
